# AI-Powered CX Reply Assistant

An AI-powered customer-support reply assistant built with **React, FastAPI, PostgreSQL/pgvector, and Google Gemini**. The application supports multiple brands, retrieves relevant brand-specific policies, generates grounded customer-support reply drafts, and allows agents to edit and approve responses.

## Live Demo

- **Frontend:** [Open the deployed application](https://datastraw-cx-reply-assistant.vercel.app/)
- **Backend API:** [Open the API](https://datastraw-cx-reply-assistant-api.onrender.com/)
- **API Documentation:** [Explore the API endpoints](https://datastraw-cx-reply-assistant-api.onrender.com/docs)
- **GitHub Repository:** [View the source code](https://github.com/ImOmkar/datastraw-cx-reply-assistant)

## Features

- **Multi-brand support:** Maintain separate knowledge-base policies for different brands.
- **Knowledge-base management:** Create, edit, deactivate, and delete policy entries.
- **Conversation management:** View customer and agent messages with persistent conversation history.
- **Semantic policy retrieval:** Retrieve relevant active policies using Gemini embeddings and PostgreSQL with pgvector.
- **Query rewriting:** Refine customer queries to improve policy search relevance.
- **Policy reranking:** Reorder retrieved candidates to prioritize relevant policy context.
- **AI reply generation:** Generate customer-support drafts grounded in available order information and retrieved policies.
- **Human review:** Edit and approve generated drafts before sending.
- **Persistence:** Retain conversations, messages, and approved responses.
- **Fallback handling:** Avoid treating unrelated or unavailable policy information as evidence.
- **Automated tests:** Test backend functionality and important application behavior.

## Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | React, Vite, Tailwind CSS |
| Backend | Python, FastAPI |
| Database and ORM | PostgreSQL, pgvector, SQLAlchemy |
| Migrations | Alembic |
| AI and embeddings | Google Gemini |
| Testing | pytest |

## Architecture Overview

1. The React frontend provides the conversation interface and knowledge-base management.
2. The FastAPI backend handles conversations, policy management, retrieval, and reply generation.
3. PostgreSQL stores application data, while pgvector supports semantic similarity search over policy embeddings.
4. Gemini supports query rewriting, policy reranking, embedding generation, and customer-reply drafting.
5. Retrieved policy context is supplied to the reply-generation workflow so the draft can be reviewed against the available evidence.

## Prerequisites

For local development, install:

- Python 3.12
- Node.js and npm
- PostgreSQL with the pgvector extension available
- A Google Gemini API key

The example database configuration below uses PostgreSQL port `5433`. Change it if your local database uses another port.

## Local Setup

### 1. Clone the repository

```powershell
git clone https://github.com/ImOmkar/datastraw-cx-reply-assistant.git
cd datastraw-cx-reply-assistant
```

### 2. Create and activate a Python environment

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install backend dependencies

If the committed dependency file is located at `backend/requirements.txt`, run:

```powershell
pip install -r backend/requirements.txt
```

### 4. Configure environment variables

Create the backend `.env` file at the location expected by the application's configuration. Configure the database connection and Gemini API key using the variable names required by the code.

Example configuration:

```dotenv
DATABASE_URL=postgresql+psycopg://<DB_USER>:<DB_PASSWORD>@localhost:5433/datastraw_cx
GEMINI_API_KEY=<YOUR_GEMINI_API_KEY>
GEMINI_MODEL=<MODEL_CONFIGURED_BY_THE_APPLICATION>
```

The embedding model configured by the application is `gemini-embedding-001`.

Use the actual model name and environment-variable names from the project configuration. Do not commit API keys, passwords, or `.env` files.

### 5. Create the database and apply migrations

Create the PostgreSQL database and ensure the required pgvector extension is available. Update `DATABASE_URL` to match your local configuration.

Apply migrations using the Alembic configuration committed with the project. For example, if `backend/alembic.ini` is configured to work from the repository root:

```powershell
python -m alembic -c backend/alembic.ini upgrade head
```

Use this command only if it matches the repository's actual Alembic configuration.

### 6. Start the backend

From the repository root, activate the virtual environment and run the project's configured FastAPI application entry point. For example, if the module path is `backend.app.main`:

```powershell
python -m uvicorn backend.app.main:app --reload
```

The API is then typically available at:

- API: `http://127.0.0.1:8000`
- Interactive API documentation: `http://127.0.0.1:8000/docs`

### 7. Start the frontend

Open a second terminal:

```powershell
cd frontend
npm install
```

Configure `VITE_API_BASE_URL` in `frontend/.env` if the frontend uses this variable:

```dotenv
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Start the development server:

```powershell
npm run dev
```

Open the local URL printed by Vite, typically `http://localhost:5173`.

## Running Tests

Activate the backend virtual environment and run the test suite using the project's configured test paths:

```powershell
python -m pytest -v
```

Run the tests after changes to policy retrieval, reply generation, database persistence, or other critical application behavior.

## Manual Verification

Use the following checks to verify the main workflows:

1. Open a conversation associated with a brand and submit a customer question about a damaged item.
2. Generate a reply and inspect the retrieved policy context.
3. Verify that retrieved policies belong to the selected brand and are relevant to the current request.
4. Submit an unrelated request and check that irrelevant policies are not treated as evidence.
5. Edit the generated draft and approve it.
6. Refresh the application and verify that the conversation and approved response persist.
7. Repeat a relevant scenario for another brand and verify that its distinct policy terms are used.

## Limitations and Future Improvements

This project is an assignment prototype and is not intended to be a production-ready customer-support system.

- Query rewriting, policy reranking, and reply generation are probabilistic and require evaluation against representative test cases.
- Retrieval thresholds and candidate counts should be tuned using real-world data.
- Production deployment would require authentication and authorization, stronger tenant-isolation controls, structured logging, rate limiting, secure secret management, monitoring, and robust retry and idempotency handling.
- Sensitive or ambiguous cases should be escalated for human review.
- A generated reply must not be treated as authorization to issue a refund or replacement. Agents should verify the applicable policy and order information before sending a response.

## Security and Repository Hygiene

- Keep API keys, passwords, and other secrets out of source control.
- Commit source code, database migrations, tests, and a sanitized `.env.example`.
- Exclude `.env` files, virtual environments, `node_modules`, database files, build output, and temporary debug artifacts from Git.
- Document the required environment variables without including their secret values.
