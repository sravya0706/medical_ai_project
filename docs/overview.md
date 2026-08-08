# MediAssist — AI-Powered Healthcare Assistant

## System Architecture & Application Flow

This document provides a detailed overview of the MediAssist application's architecture, explaining the purpose of each component and how they interact in the end-to-end application flow. It also serves as a reference for understanding the technical design and implementation.

---

## Overview

MediAssist is an AI-powered healthcare assistant designed to provide intelligent insights and recommendations based on user inputs. The system integrates multiple components, including natural language processing (NLP), machine learning (ML), and large language models (LLMs), to deliver a seamless user experience.

---

## Directory Structure

### `app/`
The core application logic resides here. Key submodules include:
- **`agents/`**: Implements various agents for task-specific operations.
- **`auth/`**: Handles authentication and authorization (e.g., JWT-based token management).
- **`config.py`**: Centralized configuration settings for the application.
- **`db/`**: Manages database interactions and ORM models (e.g., MongoDB persistence).
- **`llm/`**: Handles interactions with large language models for generating responses.
- **`main.py`**: Entry point of the application, initializing configurations and starting the server.
- **`memory/`**: Manages in-memory data storage for session-based operations.
- **`ml/`**: Contains machine learning models for predictive analytics.
- **`nlp/`**: Implements natural language processing tasks such as entity recognition and text classification.
- **`ocr/`**: Extracts text from images using optical character recognition.
- **`routes/`**: Defines API endpoints and their handlers.
- **`schemas.py`**: Contains data validation schemas for API requests and responses.

### `data/`
Stores datasets, pre-trained models, and other resources:
- **`chroma_db/`**: Stores embeddings for retrieval tasks.
- **`model.pkl`**: Serialized machine learning model for predictions.
- **`symptom_disease_dataset.csv`**: Dataset for symptom-disease mapping.

### `frontend/`
Contains the React-based frontend code for the user interface.

### `docs/`
Holds documentation files, including architecture diagrams and technical references.

---

## End-to-End Application Flow

### 1. **Application Initialization**
   - The application starts with `main.py`, which:
     - Loads environment variables and configurations from `config.py`.
     - Initializes database connections (e.g., MongoDB).
     - Sets up API routes defined in the `routes/` module.
     - Starts the server to listen for incoming requests.

### 2. **User Interaction**
   - A user interacts with the system via the **frontend** (React-based UI) or directly through API endpoints.
   - Example user actions:
     - Submitting symptoms for diagnosis.
     - Uploading medical reports for analysis.
     - Asking health-related questions.

### 3. **Request Handling**
   - The frontend sends requests to the backend via RESTful API endpoints defined in `routes/`.
   - Each route corresponds to a specific functionality:
     - **Symptom Analysis**: `/api/symptoms`
     - **Medical Report Analysis**: `/api/reports`
     - **General Queries**: `/api/queries`

### 4. **Core Processing**
   - The backend processes the request by delegating tasks to the appropriate modules:
     - **NLP (`nlp/`)**: Processes and extracts key information from user inputs.
     - **OCR (`ocr/`)**: Extracts text from uploaded medical reports.
     - **ML (`ml/`)**: Runs predictive models to analyze symptoms and suggest possible conditions.
     - **LLM (`llm/`)**: Generates natural language responses for user queries.

### 5. **Data Management**
   - If the request involves database operations:
     - The `db/` module interacts with MongoDB to fetch or store data.
     - Example: Storing user session data or retrieving historical medical records.
   - For retrieval tasks, embeddings stored in `chroma_db/` are used.

### 6. **Response Generation**
   - The processed results are formatted into a user-friendly response.
   - Example:
     - A list of possible conditions based on symptoms.
     - Insights extracted from medical reports.
     - Answers to health-related queries.

### 7. **Response Delivery**
   - The backend sends the response back to the frontend or API client.
   - The frontend displays the results in an intuitive and interactive format.

---

## Key Components

### `routes/`
Defines the API endpoints and their handlers. Each route corresponds to a specific functionality and delegates tasks to the appropriate modules.

### `llm/`
Handles interactions with large language models, including prompt construction and response parsing.

### `ml/`
Contains machine learning models for predictive analytics, such as symptom-disease mapping.

### `nlp/`
Implements natural language processing tasks, including entity recognition and text classification.

### `db/`
Manages database interactions, including user data persistence and retrieval.

---

## Configuration

- **`config.py`**: Centralized configuration file for managing environment variables and application settings.
- **`.env`**: Stores sensitive environment variables.
- **`.env.example`**: Template for environment variables.

---

## Development and Deployment

### Development
1. Set up the virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt



## 2. End-to-End Architecture Diagram (Expanded)

The MediAssist system is designed as a modular, scalable, and extensible architecture. Below is a detailed explanation of the end-to-end architecture, covering multiple scenarios to illustrate how the system handles different types of requests.

---

### 2.1 High-Level Architecture

The system consists of the following key components:

1. **Frontend (React-based UI)**:
   - Provides an intuitive interface for users to interact with the system.
   - Sends requests to the backend via RESTful API endpoints.
   - Displays results such as symptom analysis, medical report insights, or general health-related responses.

2. **Backend (FastAPI-based)**:
   - Processes requests from the frontend or API clients.
   - Delegates tasks to specialized modules (e.g., NLP, ML, LLM, OCR).
   - Manages data persistence and retrieval using MongoDB, ChromaDB, and Neo4j.

3. **Database Layer**:
   - **MongoDB**: Stores user data, session information, and historical medical records.
   - **ChromaDB**: Handles vector embeddings for RAG (Retrieval-Augmented Generation).
   - **Neo4j**: Manages relationships between symptoms, diseases, medications, and treatments.

4. **External Services**:
   - Integrates with external APIs (e.g., OpenAI ChatGPT API, Vision LLM) to enhance functionality.

---

### 2.2 Detailed Scenarios

#### Scenario 1: Symptom Analysis
**Objective**: The user submits symptoms to receive a list of possible conditions.

1. **Frontend**:
   - The user enters symptoms (e.g., "fever, headache, fatigue") into the chat interface.
   - The frontend sends a POST request to the `/api/symptoms` endpoint with the symptoms as input.

2. **Backend**:
   - The `routes/` module receives the request and validates the input using `schemas.py`.
   - The `nlp/` module processes the symptoms to extract key entities (e.g., "fever", "headache").
   - The `ml/` module uses a pre-trained XGBoost model (`model.pkl`) to predict possible conditions based on the symptoms.
   - The `db/` module logs the request and stores the results for future reference.

3. **Response**:
   - The backend formats the results (e.g., a ranked list of conditions) and sends them back to the frontend.
   - The frontend displays the results in a user-friendly format.

---

#### Scenario 2: Medical Report Analysis
**Objective**: The user uploads a medical report to extract insights.

1. **Frontend**:
   - The user uploads a PDF or image of the medical report via the UI.
   - The frontend sends the file to the `/api/reports` endpoint.

2. **Backend**:
   - The `routes/` module receives the file and validates its format.
   - The `ocr/` module extracts text from the uploaded file.
   - The `nlp/` module processes the extracted text to identify key medical terms and insights.
   - The `llm/` module generates a summary of the report using a large language model.
   - The `db/` module stores the extracted data and insights for future reference.

3. **Response**:
   - The backend sends the summarized insights back to the frontend.
   - The frontend displays the insights in an easy-to-read format.

---

#### Scenario 3: General Health Query
**Objective**: The user asks a general health-related question (e.g., "What are the symptoms of diabetes?").

1. **Frontend**:
   - The user enters the query into the search bar.
   - The frontend sends a GET request to the `/api/queries` endpoint with the query as a parameter.

2. **Backend**:
   - The `routes/` module receives the query and validates it.
   - The `llm/` module constructs a prompt for the large language model and sends the query for processing.
   - The LLM generates a natural language response based on its training data and any additional context provided by the system.

3. **Response**:
   - The backend sends the generated response back to the frontend.
   - The frontend displays the response in a conversational format.

---

#### Scenario 4: User Authentication
**Objective**: The user logs in to access personalized features.

1. **Frontend**:
   - The user enters their credentials (email and password) into the login form.
   - The frontend sends a POST request to the `/api/auth/login` endpoint.

2. **Backend**:
   - The `auth/` module validates the credentials against the database.
   - If valid, a JWT token is generated and returned to the user.
   - If invalid, an error message is returned.

3. **Response**:
   - The frontend stores the JWT token and uses it for subsequent authenticated requests.

---

#### Scenario 5: Data Retrieval
**Objective**: The user retrieves their historical medical records.

1. **Frontend**:
   - The user navigates to the "My Records" section.
   - The frontend sends a GET request to the `/api/records` endpoint, including the JWT token for authentication.

2. **Backend**:
   - The `auth/` module verifies the JWT token.
   - The `db/` module retrieves the user's records from MongoDB.
   - The records are formatted and sent back to the frontend.

3. **Response**:
   - The frontend displays the records in a structured format.

---

### 2.3 Architecture Diagram (Expanded)

Below is a visual representation of the MediAssist architecture:

```text
                              ┌─────────────────────┐
                              │   React Frontend     │
                              │ (Chat / Upload / Auth│
                              │  / History / Profile)│
                              └──────────┬───────────┘
                                         │ REST (Axios) + JWT
                                         ▼
                              ┌─────────────────────┐
                              │  FastAPI Backend      │
                              │  Controllers → Svcs   │
                              └──────────┬───────────┘
                                         │
                                         ▼
                              ┌─────────────────────┐
                              │  JWT Auth Middleware  │
                              └──────────┬───────────┘
                                         │
                                         ▼
                              ┌─────────────────────┐
                              │  Request Analyzer     │
                              │  (LangGraph Router)   │
                              └──────────┬───────────┘
              ┌──────────────┬───────────┼───────────────┬────────────────┐
              ▼              ▼           ▼                ▼                ▼
         ┌────────┐   ┌───────────┐ ┌────────┐   ┌─────────────────┐  ┌────────┐
         │  NLP   │   │ Vision LLM│ │  OCR   │   │ Conversation      │  │  Chat  │
         │ (intent│   │ (image    │ │ (docs/ │   │ Memory (session   │  │History │
         │/symptom│   │ findings) │ │ scans) │   │ context)          │  │(Mongo) │
         │extract)│   └─────┬─────┘ └───┬────┘   └─────────┬─────────┘  └────────┘
         └───┬────┘         │           │                  │
             ▼               │      ┌────▼────┐             │
    ┌──────────────────┐     │      │   PII    │             │
    │ Symptom           │     │      │Redaction │             │
    │ Classification     │     │      └────┬────┘             │
    │ (XGBoost, 85%+)    │     │           │                  │
    └────────┬───────────┘     │           │                  │
             │                 └─────┬─────┘                  │
             ▼                       ▼                        │
      ┌──────────────────────────────────────┐                │
      │        RAG Retrieval (ChromaDB)        │◄──────────────┘
      └──────────────────┬────────────────────┘
                          ▼
      ┌──────────────────────────────────────┐
      │   Knowledge Graph Enrichment (Neo4j)   │
      └──────────────────┬────────────────────┘
                          ▼
      ┌──────────────────────────────────────┐
      │              Prompt Builder             │
      │ (query + symptoms + prediction +        │
      │  RAG docs + KG relations + history +    │
      │  vision findings + safety instructions) │
      └──────────────────┬────────────────────┘
                          ▼
      ┌──────────────────────────────────────┐
      │       OpenAI ChatGPT API (LLM)          │
      └──────────────────┬────────────────────┘
                          ▼
      ┌──────────────────────────────────────┐
      │     Safety Guardrail Engine             │
      │ (escalate high-risk symptoms instead     │
      │  of self-diagnosis)                      │
      └──────────────────┬────────────────────┘
                          ▼
                  Final Response (JSON)
                          │
                          ▼
                  React Chat UI renders it