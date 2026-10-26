# AI-Powered CX Reply Assistant

A prototype customer-support reply assistant for multiple brands. It
stores brand-specific knowledge-base policies, retrieves relevant active
policies for a conversation, drafts a reply with Gemini, and lets an
agent edit and approve the response.

## Features

-   Multiple brands with brand-specific knowledge-base entries.
-   Create, edit, deactivate, and delete knowledge-base entries through
    the application.
-   Customer/agent conversation view with persisted messages.
-   Semantic policy retrieval using Gemini embeddings and
    PostgreSQL/pgvector.
-   Query rewriting and policy reranking to improve retrieval relevance.
-   AI-generated reply drafts grounded in retrieved policy context and
    available order information.
-   Draft editing and approval, with approved response persistence.
-   Fallback behavior when no relevant policy is found.
-   Automated backend tests.

## Technology stack

-   **Frontend:** React, Vite, Tailwind CSS
-   **Backend:** Python, FastAPI, SQLAlchemy, Alembic
-   **Database:** PostgreSQL with pgvector
-   **AI:** Google Gemini for embeddings, query rewriting, reranking,
    and reply generation

## Prerequisites

Install the following before setup:

-   Python 3.12
-   Node.js and npm
-   PostgreSQL
-   A Google Gemini API key

The local development setup described below uses PostgreSQL port `5433`.
Change the connection string if your PostgreSQL instance uses a
different port.

## Setup

### 1. Clone the repository and create a Python environment

``` powershell
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd datastraw_assignment

py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install backend dependencies

Use the dependency file committed with the project, if present:

``` powershell
pip install -r backend\requirements.txt
```

If your project keeps `requirements.txt` in a different location, use
that path. Do not commit the virtual environment.

### 3. Configure environment variables

Create the backend `.env` file in the location read by the backend
configuration. Use your existing local configuration as the source of
truth. Example values:

``` dotenv
DATABASE_URL=postgresql+psycopg://<DB_USER>:<DB_PASSWORD>@localhost:5433/datastraw_cx
GEMINI_API_KEY=<YOUR_GEMINI_API_KEY>
GEMINI_MODEL=gemini-3.6-flash
```

Do not commit `.env`, API keys, database passwords, or other secrets.
The embedding model configured by the application is
`gemini-embedding-001`.

### 4. Create the database and run migrations

Create a PostgreSQL database named `datastraw_cx` (or update
`DATABASE_URL` to match your database). From the repository root,
activate the virtual environment and run:

``` powershell
python -m alembic -c backend\alembic.ini upgrade head
```

If Alembic is configured to be run from the backend directory in your
checkout, run the project's existing migration command from that
directory instead. Confirm the migration configuration path before
running it.

### 5. Start the backend

From the repository root, with the virtual environment active:

``` powershell
python -m uvicorn backend.app.main:app --reload
```

The API should be available at `http://127.0.0.1:8000`; interactive API
documentation is at `http://127.0.0.1:8000/docs`.

### 6. Install and start the frontend

Open a second PowerShell terminal:

``` powershell
cd frontend
npm install
```

Create `frontend/.env` if needed:

``` dotenv
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Then start the frontend:

``` powershell
npm run dev
```

Open the local URL printed by Vite, normally `http://localhost:5173`.

## Run tests

From the repository root, activate the backend virtual environment and
run:

``` powershell
python -m pytest -v
```

Use the test suite as the first verification step after changing
retrieval, reply-generation, or persistence logic.

## Suggested manual smoke test

1.  Open a conversation for a brand and send a customer message about a
    damaged item.
2.  Generate a reply and inspect the retrieved policy context.
3.  Confirm the retrieved policies belong to the selected brand and are
    relevant to the current message.
4.  Try an unrelated request and verify the application does not invent
    a policy when no relevant entry exists.
5.  Edit the generated draft and approve it.
6.  Refresh the page and verify the conversation and approved response
    persist.
7.  Repeat a relevant scenario for a second brand and check that its
    distinct policy terms are used.

## Important limitations

-   This is an assignment prototype, not a production-ready
    customer-support system.
-   AI-generated query rewriting, reranking, and replies are
    probabilistic and must be evaluated against a representative test
    set.
-   The retrieval threshold and number of candidate policies are
    configuration choices that should be validated with real data.
-   Production deployment should add authentication and authorization,
    stronger tenant isolation controls, structured logging, rate limits,
    secret management, monitoring, retry/idempotency handling, and a
    human-review workflow for sensitive decisions.
-   Do not treat a generated reply as authorization to issue a refund or
    replacement. Agents should verify the policy and order facts before
    sending.

## Repository hygiene before submission

-   Commit source code, migrations, tests, and a sanitized
    `.env.example`.
-   Ensure `.env`, credentials, database files, `.venv`, `node_modules`,
    build output, and debug artifacts are excluded from Git.
-   Replace this README's repository URL placeholder with the actual
    repository URL.
-   Verify the setup instructions from a clean checkout before
    submitting.
