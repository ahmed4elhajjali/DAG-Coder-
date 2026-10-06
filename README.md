# DAG Coder

**DAG Coder** is an **Agentic AI coding system** that transforms a natural-language software request into a complete code project using a **Directed Acyclic Graph (DAG)** and multiple specialized AI agents.

### Workflow

**User Prompt → Orchestrator → DAG → Parallel Sub-Agents → Integrator → Final Code**

* **Orchestrator:** Understands the user's request and breaks it into smaller development tasks.
* **DAG:** Organizes tasks and their dependencies to determine the execution order.
* **Parallel Sub-Agents:** Execute independent tasks simultaneously to improve efficiency and reduce execution time.
* **Integrator:** Combines the outputs from all agents, resolves inconsistencies, and generates the final project using an LLM through the **Groq API**.
* **Output:** Saves the generated project files to the configured output directory.

### Configuration

The system is configured through `.env`:

* `GROQ_API_KEY` — Groq API key
* `MODEL` — LLM model to use
* `MAX_PARALLEL` — Maximum number of parallel agents
* `MAX_RETRIES` — Maximum retry attempts
* `OUTPUT_DIR` — Directory for generated files

### Running the Project

**Install dependencies:**

```bash
pip install -r requirements.txt
```

**Configure the environment:**

```bash
cp .env.example .env
```

Add your `GROQ_API_KEY` to `.env`.

**Run the Streamlit GUI:**

```bash
streamlit run app.py
```

**Run from the CLI:**

```bash
python main.py "Build a FastAPI todo app with SQLite and JWT auth"
```

Or run the built-in example:

```bash
python main.py --example
```

### Key Idea

DAG Coder combines **LLM-based planning, DAG task orchestration, parallel multi-agent execution, and result integration** to turn a high-level software description into a structured, working codebase.
