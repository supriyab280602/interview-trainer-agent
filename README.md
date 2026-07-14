# IBM watsonx AI - Interview Trainer Agent

An advanced, production-grade AI Interview Trainer Agent built using Retrieval-Augmented Generation (RAG). Developed using FastAPI for the backend service layer and Streamlit for a modern, premium SaaS frontend experience. The application uses the **IBM Granite-3-8b-instruct** foundation model via the official `ibm-watsonx-ai` SDK and integrates with IBM Cloud Object Storage (COS) and IBM Cloudant NoSQL database.

---

## Key Features

- **Personalized Interview Generation**: Granite AI generates natural, conversational, and role-specific questions suited to target job focus and candidate experience tracks.
- **RAG-Grounded Appraising**: Uses an independent semantic embedding pipeline (`sentence-transformers/all-MiniLM-L6-v2`) and ChromaDB vector stores to feed relevant rubrics, expected answers, and STAR frameworks to Granite before grading.
- **Optional Resume Analysis**: PDF parser extracts structural skills, technologies, education, achievements, and past projects to adapt interview context dynamically.
- **Session-Based Authentication**: Secure registration and password hashing using `bcrypt` backed by Cloudant sessions.
- **Performance Analytics Center**: Interactive Plotly tracking of user scores timeline, completed rates, strongest/weakest topics, and custom study plans.
- **Printable PDF Reports**: Exporter compiling candidate responses, grading scores, constructive tips, and model answers using `fpdf2`.
- **Local Database & Storage Fallbacks**: Automatically falls back to local JSON database storage and local folder uploads if Cloudant or Cloud Object Storage (COS) credentials are not yet configured, allowing you to run database features locally.

---

## Project Structure

```
InterviewTrainer/
├── app.py                     # Premium Streamlit UI Client
├── main.py                    # FastAPI Backend Application Server
├── engine.py                  # IBM Granite Engine (watsonx SDK)
├── rag_pipeline.py            # RAG Pipeline (semantic chunking, ChromaDB, Sentence-Transformers)
├── auth.py                    # Security Utilities (hashing, UUID sessions)
├── storage.py                 # IBM Cloud Object Storage Service Wrapper
├── config.py                  # Pydantic v2 Environment Config Loader
├── test_backend.py            # Automated Unit and Mock DB test suite
├── requirements.txt           # Package Dependencies list
├── .env.example               # Template environment variables
├── prompts/                   # Granite Prompt Templates
│   ├── question_prompt.py
│   ├── evaluation_prompt.py
│   ├── summary_prompt.py
│   └── resume_prompt.py
├── schemas/                   # Pydantic Request Validation Schemas
│   ├── auth.py
│   └── interview.py
├── models/                    # Pydantic Database Record Representations
│   ├── user.py
│   ├── interview.py
│   └── resume.py
├── services/                  # Business Logic Layer
│   ├── auth_service.py
│   ├── resume_service.py
│   ├── interview_service.py
│   ├── evaluation_service.py
│   ├── analytics_service.py
│   ├── cloudant_service.py
│   ├── cos_service.py
│   └── rag_service.py
└── api/                       # API Routing Layer
    ├── auth_routes.py
    ├── profile_routes.py
    ├── resume_routes.py
    ├── interview_routes.py
    └── analytics_routes.py
```

---

## Prerequisites

- **Python 3.12 or 3.14**
- **pip** package installer

---

## Installation & Setup

1. **Clone/Open workspace**:
   Navigate to the project root directory.

2. **Install Package Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Copy `.env.example` to `.env` and enter your IBM Cloud credentials:
   ```bash
   cp .env.example .env
   ```

---

## IBM Cloud Services Configuration

### 1. IBM watsonx.ai

1. Go to the [IBM Cloud Console](https://cloud.ibm.com/) and create a **watsonx.ai** instance.
2. Open the watsonx console, create a new Project, and retrieve the **Project ID** from the project _Settings_ tab.
3. Obtain an IAM API key from _Manage > Access (IAM) > API keys_.
4. Populate `IBM_CLOUD_API_KEY`, `IBM_PROJECT_ID`, and `IBM_ENDPOINT_URL` in `.env`.

### 2. IBM Cloudant (NoSQL DB)

1. Search and deploy a **Cloudant** instance in your Cloud account (Select the _IAM and Cloudant credentials_ authentication option).
2. Go to the Cloudant Service Credentials tab, create credentials, and copy the `url` and `apikey`.
3. Populate `IBM_CLOUDANT_URL` and `IBM_CLOUDANT_API_KEY` in `.env`.

### 3. IBM Cloud Object Storage (COS)

1. Deploy a **Cloud Object Storage** instance.
2. Create a bucket (e.g. `interview-trainer-resumes`) and set the regional endpoint URL.
3. Generate Service Credentials with _Writer_ role and enable _HMAC credentials_.
4. Populate `IBM_COS_API_KEY`, `IBM_COS_ENDPOINT`, and `IBM_COS_BUCKET` in `.env`.

---

## Execution Instructions

The backend and frontend are run concurrently on separate ports:

### 1. Launch FastAPI Backend

Launch the server using Uvicorn:

```bash
uvicorn main:app --reload
```

The backend server runs at `http://localhost:8000`. You can inspect automated Swagger API documentations at `http://localhost:8000/docs`.

### 2. Launch Streamlit Frontend

In a new terminal shell:

```bash
streamlit run app.py
```

The frontend application will open automatically in your browser at `http://localhost:8501`.

---

## Testing & Verification

Run the automated Python test suite to verify security utility hashes, schema models, and database mock CRUD operations:

```bash
python test_backend.py
```
