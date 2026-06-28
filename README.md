# Asset Management AI

A LangChain-powered Asset Management module built for the **Buguard Internship Acceptance Task (AI Track)**.

This project implements a secure AI layer over an Attack Surface Management (ASM) asset inventory. Instead of allowing the LLM to generate SQL directly, natural-language requests are converted into validated structured queries, translated into SQLAlchemy expressions, and executed against PostgreSQL. This architecture minimizes hallucinations, prevents SQL injection, and ensures that AI-generated responses remain grounded in the stored inventory.

---

# Features

## Core Features

* Bulk asset import into PostgreSQL
* Idempotent imports
* Asset deduplication
* Asset relationship management
* PostgreSQL persistence
* FastAPI REST API
* OpenAPI / Swagger documentation

## AI Features

### Natural Language Asset Query

Convert English questions into structured database queries.

Example:

```
Show me all active domains
```

↓

Structured Query

```json
{
  "filters": {
    "type": "domain",
    "status": "active"
  },
  "limit": 100
}
```

↓

SQLAlchemy Query

↓

PostgreSQL

---

### Risk Assessment

Generate grounded cybersecurity risk summaries using only the imported asset inventory.

---

### Asset Enrichment

Automatically classify assets by:

* Environment
* Category
* Criticality

while remaining grounded in the stored asset data.

---

### Report Generation

Generate executive inventory reports based only on imported assets.

The LLM never invents assets or vulnerabilities.

---

# Architecture

```
                User
                  │
                  ▼
          Natural Language
                  │
                  ▼
             LangChain
                  │
                  ▼
      Structured AssetQuery
                  │
                  ▼
        Pydantic Validation
                  │
                  ▼
           SQLAlchemy ORM
                  │
                  ▼
            PostgreSQL
                  │
                  ▼
          Grounded Context
                  │
                  ▼
      Risk / Report / Enrichment
```

---

# Tech Stack

* Python 3.12
* FastAPI
* PostgreSQL
* SQLAlchemy
* Alembic
* LangChain
* Groq LLM
* Pydantic
* Docker
* Docker Compose

---

# Project Structure

```text
asset_management_ai/
├── app/
├── alembic/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── sample_dataset.json
├── .env.example
└── README.md
```

---

# Installation

```bash
git clone <repository_url>

cd asset_management_ai
```

Create a virtual environment

Windows

```bash
python -m venv venv

venv\Scripts\activate
```

Linux / macOS

```bash
python -m venv venv

source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

# Environment Variables

Create a `.env` file.

For Docker:

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@postgres:5432/asset_management

GROQ_API_KEY=your_groq_api_key_here
```

---

# Running the Project

Start the complete application:

```bash
docker compose up --build
```

Docker Compose automatically:

* Starts PostgreSQL
* Waits until PostgreSQL becomes healthy
* Executes Alembic migrations
* Starts the FastAPI application

Swagger UI:

```
http://localhost:8000/docs
```

---

# API Endpoints

POST /import

POST /ai/query

POST /ai/risk

POST /ai/enrich

POST /ai/report

---

# Design Decisions

## Why Structured Queries?

Natural-language requests are first converted into a strongly typed `AssetQuery`.

The validated query is then translated into SQLAlchemy expressions instead of allowing the LLM to generate SQL directly.

Benefits:

* Reduced hallucinations
* SQL injection protection
* Deterministic database queries
* Easier validation
* Better maintainability

---

## Hallucination Prevention

The LLM never accesses PostgreSQL directly.

Workflow:

```
Natural Language

↓

Structured Query

↓

SQLAlchemy

↓

PostgreSQL

↓

Grounded Context

↓

LLM
```

All reports, enrichment, and risk assessments are generated only from retrieved database records.

---

# Security Considerations

Implemented protections include:

* SQLAlchemy ORM only (no raw SQL)
* Parameterized queries
* Pydantic validation
* Grounded LLM responses
* Prompt injection mitigation
* SQL injection protection
* Out-of-scope request rejection
* Secrets loaded from environment variables

---

# Running Tests

The project was manually tested using the FastAPI Swagger interface.

Verified scenarios:

* Dataset import
* Idempotent import
* Asset deduplication
* Natural-language asset querying
* Risk assessment
* Asset enrichment
* Report generation
* SQL injection resistance
* Prompt injection resistance
* Out-of-scope request handling

---

# Example Prompts

## Query

Prompt

```
Show me all active domains
```

Example Result

Returns all active domain assets stored in PostgreSQL.

---

## Risk

Prompt

```
Analyze api.example.com
```

Example Result

Returns a grounded cybersecurity risk assessment including findings and recommendations.

---

## Enrichment

Prompt

```
Enrich api.example.com
```

Example Result

Returns the inferred environment, category, criticality, and summary.

---

## Report

Prompt

```
Generate report for all active assets
```

Example Result

Returns an executive inventory report generated only from imported assets.

---

# Assumptions

* The provided dataset is the source of truth.
* PostgreSQL is used as the persistent storage layer.
* Unsupported natural-language requests are rejected.
* SQL generation is handled exclusively through SQLAlchemy.
* AI responses are grounded only in stored asset data.
* API secrets are loaded from environment variables.

---

# Future Improvements

* Authentication & RBAC
* Multi-tenant support
* Relationship graph visualization
* CI/CD pipeline
* Redis caching
* Agentic LangChain workflow
* Automated evaluation
* Retrieval-Augmented Generation (RAG)
* Expanded unit and integration tests

---

# Acknowledgements

Developed as part of the **Buguard AI Applications Internship Acceptance Task**.

The implementation focuses on secure LLM integration, grounded AI responses, and robust asset management using FastAPI, PostgreSQL, SQLAlchemy, and LangChain.
