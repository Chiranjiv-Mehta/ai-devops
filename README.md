# AI DevOps Assistant 🚀🛡️

An intelligent, interactive DevOps and SRE Assistant featuring automated log troubleshooting, Infrastructure-as-Code (IaC) generation, a knowledgeable DevOps chatbot, and workflow automation.

---

## Features

1. **💬 DevOps Chatbot**: Ask questions about containerization, orchestration, scripting, cloud operations, and security practices.
2. **🔍 Logs & IaC Analyzer**: Paste crash reports or upload server/build/deployment logs to get instantaneous explanations, root-cause analysis, and copy-pasteable configuration hotfixes.
3. **🛠️ IaC Config Generator**: Fill out interactive forms to write optimized, multi-stage Dockerfiles, Kubernetes Deployments/Services, CI/CD pipelines (GitHub Actions), and Terraform configs following security best practices.
4. **🔗 n8n Workflow Automation**: Includes a webhook-based n8n blueprint that hooks into alert notifications, queries the AI engine for a diagnosis, and sends formatted messages to Slack.

---

## Project Structure

```
ai-devops-assistant/
├── backend/
│   ├── main.py                # FastAPI server entry point
│   ├── ai_service.py          # AI logic (Gemini & OpenAI API integrations)
│   ├── routes/                # FastAPI endpoint handlers
│   ├── services/              # Log parsing and truncation
│   ├── utils/                 # Configuration manager
│   ├── requirements.txt       # Python backend packages
│   └── .env                   # Local configuration and API keys
│
├── frontend/
│   ├── app.py                 # Streamlit UI configuration and routing
│   └── components/            # Chatbot, analyzer, and generator tab views
│
├── workflows/
│   └── n8n-workflows/         # n8n workflow JSON blueprints
│
├── docker/
│   ├── Dockerfile             # Multi-stage container builds
│   └── docker-compose.yml     # Service orchestration (backend + frontend + n8n)
│
├── uploads/                   # Uploaded log files folder
├── logs/                      # Backend application runtime logs
└── README.md                  # This documentation
```

---

## Local Setup & Installation

### Prerequisites
- Python 3.10+
- Google Gemini API Key (or OpenAI API Key)

### 1. Set Up Backend
1. Navigate to the `backend/` directory:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
5. Open backend `.env` and add your **`GEMINI_API_KEY`** (obtained from Google AI Studio) or **`OPENAI_API_KEY`**.

6. Start the backend:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

### 2. Set Up Frontend
1. Open a new terminal and navigate to the project root.
2. Activate your virtual environment and install Streamlit:
   ```bash
   pip install streamlit
   ```
3. Run the Streamlit application:
   ```bash
   streamlit run frontend/app.py --server.port 8501
   ```
4. Open your browser and navigate to: [http://localhost:8501](http://localhost:8501)

---

## Running with Docker Compose

If you have Docker installed, you can spin up the backend, frontend, and n8n services together with a single command:

1. Add your API keys to `backend/.env`.
2. From the project root, navigate to the `docker/` folder and run:
   ```bash
   docker-compose up --build
   ```
3. Access points:
   - **Frontend UI**: [http://localhost:8501](http://localhost:8501)
   - **Backend API**: [http://localhost:8000](http://localhost:8000)
   - **n8n Automation Console**: [http://localhost:5678](http://localhost:5678)

---

## Triggering n8n Workflow

1. Open n8n at [http://localhost:5678](http://localhost:5678).
2. Create a new workflow, click the top-right menu, and select **Import from File**. Import the `workflows/n8n-workflows/alert_troubleshooter.json` file.
3. Configure the **Send Slack Alert** node with your Slack Webhook URL.
4. Activate the webhook and test by POSTing an alert payload to your n8n webhook URL:
   ```bash
   curl -X POST http://localhost:5678/webhook-test/devops-alert \
     -H "Content-Type: application/json" \
     -d '{"log": "Traceback (most recent call last):\n  File \"app.py\", line 15, in <module>\n    import psycopg2\nModuleNotFoundError: No name \"psycopg2\" in module list"}'
   ```
5. You will receive a rich, diagnosed alert summary in Slack!
