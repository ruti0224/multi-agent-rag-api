# 🛡️ Sentinel RAG API

Sentinel RAG API is a robust FastAPI backend designed for autonomous document analysis, summarization, and data extraction using Retrieval-Augmented Generation (RAG) and OpenAI's LLMs.

The system is specially architected to ensure strict data isolation and maintain high stability in environments with rigorous network filtering (e.g., Netfree) and proxy servers.

## ✨ Key Features

* **Advanced RAG Engine:** Accurate, context-aware Q&A based solely on the currently active document.
* **Universal Document Summarization:** Automatically generates an executive summary (type, entities, key data points) for any uploaded text or PDF file.
* **Data Leakage Prevention:** Utilizes strict Metadata Filtering to ensure answers are extracted *only* from the requested file, preventing context bleeding between documents.
* **Smart Memory Management (Idempotency):** Detects existing files in the Vector Database and skips duplicate embedding to save API costs and memory.
* **Network-Resilient Architecture:** 
  * Custom HTTP client configurations (`verify=False`, extended timeouts) to bypass strict firewall/proxy SSL inspections.
  * "Fake Streaming" implementation: Delivers stable JSON responses from the backend while allowing the frontend to simulate a real-time typing effect, preventing proxy timeouts during actual SSE streams.

## 🛠️ Tech Stack

* **Backend Framework:** FastAPI / Python 3.x
* **AI & Embeddings:** OpenAI API (`gpt-4o-mini`, `text-embedding-3-small`)
* **Database:** Vector Database for chunk storage and semantic search
* **Network Handling:** `httpx`, `pip-system-certs` (for OS-level certificate resolution)

## 🚀 Getting Started

### Prerequisites
* Python 3.9+
* An active OpenAI API Key

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/ruti0224/sentinel-rag-api.git
   cd sentinel-rag-api
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Mac/Linux:
   source .venv/bin/activate
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   # Required for seamless operation behind strict web filters:
   pip install pip-system-certs
   ```

4. Environment Variables:
   Create a `.env` file in the root directory and add your API key:
   ```env
   OPENAI_API_KEY=your_api_key_here
   ```

### Running the Server

Start the FastAPI application:
```bash
python main.py
```
The server will be available at `[http://127.0.0.1:8000](http://127.0.0.1:8000)`.

## 📡 Core API Endpoints

* `POST /analyze`: Accepts an uploaded file (`UploadFile`) and a user query (`question`). Handles document chunking, dynamic vector storage, and returns an AI-generated answer based on the document text, alongside the source context.
* `GET /summary/{filename}`: Automatically generates a concise Hebrew executive summary of the specified document directly from the vector store.

## 📝 Next Steps / Roadmap
* Implementation of a Multi-Agent architecture (Reader, Analyzer, Critic) for complex data pipelines.
* Cross-document search capabilities ("Query all files").