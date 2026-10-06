# DAG Coder
Orchestrator -> DAG -> parallel sub-agents -> Integrator (LLM via Groq API).

    pip install -r requirements.txt
    cp .env.example .env          # put your GROQ_API_KEY

GUI (dark):

    streamlit run app.py

CLI:

    python main.py "Build a FastAPI todo app with SQLite and JWT auth"
    python main.py --example

Everything is configured through .env (MODEL, MAX_PARALLEL, MAX_RETRIES, OUTPUT_DIR).
