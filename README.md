# Sentinel AI Platform 🛡️

**Sentinel AI** is an AI-powered Cybersecurity Threat Detection System built with a robust FastAPI backend. It features dynamic machine learning threat analysis for phishing URLs, a hybrid rule-based payload scanner for vulnerabilities like XSS and SQL Injection, and an integrated generative AI chatbot acting as a cybersecurity expert to guide users.

## ✨ Features

- **Phishing URL Detection**: Built-in Machine Learning analysis using a pre-trained ONNX model from Hugging Face hub (`pirocheto/phishing-url-detection`) to score malicious links.
- **Payload Analyzer & Threat Scoring**: Hybrid approach combining ML models and rule-based regex detection to flag code injections (e.g., SQLi, XSS, insecure HTTP headers, raw IP usage) and generate severity matrices.
- **Cyber AI Chatbot**: Integrated with Google's **Gemini 2.5 Flash** LLM via **LangChain** to act as a cybersecurity expert assistant. It can explain vulnerabilities, analyze risks, and provide preventative actions.
- **FastAPI Backend**: High-performance asynchronous API endpoints (`/api/analyze`, `/api/chat`).
- **Web UI**: User-friendly dashboard utilizing Jinja2 templates and Vanilla JS/CSS communicating directly with the backend APIs.

## 🛠️ Technology Stack

- **Backend**: Python, FastAPI, Uvicorn
- **Machine Learning**: ONNX Runtime, Hugging Face Hub (`hf_hub_download`), Numpy
- **Generative AI**: LangChain, Google Generative AI (`gemini-2.5-flash`)
- **Frontend**: HTML5, Vanilla JavaScript, CSS3, Jinja2 Templates
- **Environment**: Python `dotenv` for secure environment variable management

## 🚀 Getting Started

### Prerequisites

- Python 3.8+ installed on your system.
- A valid **Google API Key** for accessing the Gemini model.

### 1. Configure the Environment Variables

Create a file named `.env` in the root directory and add your Google API key:

```ini
GOOGLE_API_KEY="your-google-api-key-here"
```

### 2. Install Dependencies & Start Server

Open your terminal in the root project directory, install dependencies, and start the local web development server:

```bash
pip install -r requirements.txt
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### 3. Access the Application

Once the server has started, open your browser and navigate to:
**http://127.0.0.1:8000**

## 📂 Project Structure

```text
Ai-Powered-Cyber-Threat-Detection-System/
│
├── core/              # ML Models & huggingface loader (model_loader.py)
├── routes/            # FastAPI API Endpoint definitions (analyze.py, chat.py)
├── schemas/           # Pydantic request & response models
├── services/          # Business logic for chat and threat analysis
├── static/            # Frontend static assets (css, js, images)
├── templates/         # HTML Jinja templates (index.html)
├── .env               # Environment attributes (API keys - required)
├── main.py            # FastAPI App initialiser & configurator
├── requirements.txt   # Python dependency list
└── README.md          # Project documentation
```

## 🔐 API Endpoints

- `GET /` - Serves the main User Interface dashboard.
- `GET /api/health` - Basic server health-check indicator.
- `POST /api/analyze` - Analyzes a provided text payload or URL and returns a comprehensive threat score & indicators matrix.
- `POST /api/chat` - Queries the LangChain/Gemini Chatbot service with a cybersecurity question.
