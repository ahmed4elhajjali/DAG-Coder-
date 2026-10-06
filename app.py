import asyncio
import io
import os
import zipfile

import streamlit as st

import config
import llm
from examples import EXAMPLES
from integrator import save_files
from pipeline import run_pipeline

st.set_page_config(page_title="DAG Coder", page_icon="🧩", layout="wide")

st.markdown(
    """
<style>
.block-container {padding-top: 2rem; max-width: 1300px;}
.hero h1 {font-size: 2.2rem; margin-bottom: 0;
  background: linear-gradient(90deg,#7c5cff,#22d3ee); -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;}
.hero p {color: #8892a6; margin-top: .2rem;}
.card {background:#161b26; border:1px solid #232a3b; border-radius:12px; padding:.6rem .9rem;
  margin-bottom:.45rem; display:flex; justify-content:space-between; align-items:center;}
.card small {color:#8892a6;}
.badge {padding:2px 10px; border-radius:999px; font-size:.75rem; font-weight:600;}
.pending{background:#2b3040;color:#9aa4b2}
.running{background:#4a3a00;color:#ffd166}
.done{background:#0f3d31;color:#5eead4}
.failed{background:#4a1520;color:#ff7b8a}
</style>
<div class="hero"><h1>🧩 DAG Coder</h1>
<p>Orchestrator → DAG → parallel sub-agents → Integrator</p></div>
""",
    unsafe_allow_html=True,
)

COLORS = {"pending": "#2b3040", "running": "#b8860b", "done": "#14806b", "failed": "#b3263f"}


def dag_dot(tasks: dict, status: dict) -> str:
    L = [
        "digraph G {", "rankdir=LR;", 'bgcolor="transparent";', "nodesep=0.35;",
        'node [shape=box, style="rounded,filled", fontname="Helvetica", fontcolor="white", color="#00000000", margin="0.15,0.08"];',
        'edge [color="#8892a6"];',
    ]
    L.append(f'ORCH [label="Orchestrator", shape=ellipse, fillcolor="{COLORS[status.get("ORCH", "running")]}"];')
    L.append(f'INTEG [label="Integrator", shape=ellipse, fillcolor="{COLORS[status.get("INTEG", "pending")]}"];')
    has_dependents = {d for t in tasks.values() for d in t["depends_on"]}
    for tid, t in tasks.items():
        title = t["title"].replace('"', "'")[:26]
        L.append(f'"{tid}" [label="{tid}\\n{title}", fillcolor="{COLORS[status.get(tid, "pending")]}"];')
        if not t["depends_on"]:
            L.append(f'ORCH -> "{tid}";')
        for d in t["depends_on"]:
            L.append(f'"{d}" -> "{tid}";')
        if tid not in has_dependents:
            L.append(f'"{tid}" -> INTEG;')
    L.append("}")
    return "\n".join(L)


def cards_html(tasks: dict, status: dict) -> str:
    rows = []
    for tid, t in tasks.items():
        s = status.get(tid, "pending")
        deps = ", ".join(t["depends_on"]) or "—"
        rows.append(
            f'<div class="card"><div><b>{tid}</b> · {t["title"]}<br><small>depends on: {deps}</small></div>'
            f'<span class="badge {s}">{s}</span></div>'
        )
    return "".join(rows)


LANG = {"py": "python", "md": "markdown", "json": "json", "txt": "text", "toml": "toml",
        "yml": "yaml", "yaml": "yaml", "html": "html", "js": "javascript", "css": "css"}

# ---------------- sidebar ----------------
with st.sidebar:
    st.header("⚙️ Settings")
    key = st.text_input("Groq API Key", type="password",
                        help="Leave empty to use GROQ_API_KEY from .env")
    config.MODEL = st.text_input("Model", value=config.MODEL)
    max_par = st.slider("Max parallel agents", 1, 6, config.MAX_PARALLEL)
    save_disk = st.checkbox("Also save files to disk", value=True)
    out_dir = st.text_input("Output dir", value=config.OUTPUT_DIR)

# ---------------- input ----------------
c1, c2 = st.columns([1, 2])
with c1:
    choice = st.selectbox("Example tasks", ["— custom —"] + list(EXAMPLES))
default = EXAMPLES.get(choice, "")
task = st.text_area("Coding task", value=default, height=110, key=f"task_{choice}",
                    placeholder="Describe the project you want built...")
run = st.button("🚀 Run", type="primary", use_container_width=True)

st.divider()
left, right = st.columns([3, 2])
graph_ph = left.empty()
status_ph = right.empty()
progress_ph = st.empty()
log_ph = st.empty()

# ---------------- run ----------------
if run:
    llm.set_api_key(key)
    if not task.strip():
        st.warning("Write a task first.")
        st.stop()
    if not os.getenv("GROQ_API_KEY"):
        st.error("No GROQ_API_KEY — add it in the sidebar or in .env")
        st.stop()

    state = {"tasks": {}, "status": {"ORCH": "running"}, "log": []}

    def render():
        graph_ph.graphviz_chart(dag_dot(state["tasks"], state["status"]), use_container_width=True)
        status_ph.markdown(cards_html(state["tasks"], state["status"]), unsafe_allow_html=True)
        n = len(state["tasks"])
        done = sum(1 for t in state["tasks"] if state["status"].get(t) == "done")
        if n:
            progress_ph.progress(done / n, text=f"{done}/{n} sub-agents finished")
        log_ph.code("\n".join(state["log"][-8:]) or " ", language="text")

    def on_event(event, **d):
        s, lg = state["status"], state["log"]
        if event == "plan":
            state["tasks"] = d["tasks"]
            s["ORCH"] = "done"
            s.update({t: "pending" for t in d["tasks"]})
            lg.append(f"Plan ready: {len(d['tasks'])} tasks")
        elif event == "start":
            s[d["tid"]] = "running"; lg.append(f"start {d['tid']}")
        elif event == "done":
            s[d["tid"]] = "done"; lg.append(f"done  {d['tid']}")
        elif event == "failed":
            s[d["tid"]] = "failed"; lg.append(f"FAILED {d['tid']}: {d['error'][:120]}")
        elif event == "integrating":
            s["INTEG"] = "running"; lg.append("integrating...")
        elif event == "finished":
            s["INTEG"] = "done"; lg.append(f"finished: {len(d['files'])} files")
        render()

    render()
    try:
        tasks, results, files = asyncio.run(run_pipeline(task, on_event, max_par))
        if save_disk:
            save_files(files, out_dir)
        st.session_state["result"] = {
            "tasks": tasks, "results": results, "files": files,
            "status": dict(state["status"]), "log": state["log"],
        }
    except Exception as e:
        st.error(f"Run failed: {e}")
        st.stop()
elif "result" in st.session_state:
    r = st.session_state["result"]
    graph_ph.graphviz_chart(dag_dot(r["tasks"], r["status"]), use_container_width=True)
    status_ph.markdown(cards_html(r["tasks"], r["status"]), unsafe_allow_html=True)

# ---------------- results ----------------
r = st.session_state.get("result")
if r:
    st.subheader("📦 Result")
    files = r["files"]
    if not files:
        st.warning("Integrator returned no parsable files. Check the agent outputs tab.")
    t_files, t_agents = st.tabs([f"Files ({len(files)})", "Agent outputs"])
    with t_files:
        if files:
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
                for p, c in files.items():
                    z.writestr(p, c)
            st.download_button("⬇️ Download project (.zip)", buf.getvalue(),
                               file_name="generated_project.zip", mime="application/zip")
            sel = st.selectbox("File", list(files))
            st.code(files[sel], language=LANG.get(sel.rsplit(".", 1)[-1], None))
    with t_agents:
        for tid, out in r["results"].items():
            with st.expander(f"{tid} · {r['tasks'][tid]['title']}"):
                st.markdown(out)
