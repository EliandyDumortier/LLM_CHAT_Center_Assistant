# AI-Powered Call Center Assistant

A comprehensive full-stack application featuring a RAG-powered chat system with Ollama, Django marketing site, and React chat widget.

## Project Structure

```
├── backend_fastapi/          # FastAPI backend with RAG
│   ├── app/
│   │   ├── core/config.py    # Configuration settings
│   │   ├── db/client.py      # ChromaDB client
│   │   ├── rag/
│   │   │   ├── ingest.py     # CSV ingestion & embedding
│   │   │   └── query.py      # RAG query engine
│   │   ├── routers/
│   │   │   ├── ingest.py     # Admin ingestion endpoints
│   │   │   └── chat.py       # Chat endpoints
│   │   └── main.py           # FastAPI app
│   ├── data/                 # CSV data files
│   ├── requirements.txt
│   └── .env
├── company_site_backend_django/  # Django marketing site
│   ├── company_site/         # Django project
│   ├── website/              # Django app
│   └── requirements.txt
└── frontend_widget/          # React chat widget
    ├── src/
    │   ├── ChatWidget.js     # Main chat component
    │   ├── AgentConsole.js   # Agent monitoring console
    │   └── App.js
    └── package.json
```

## Features

### Backend (FastAPI)
- **RAG Pipeline**: Retrieval-Augmented Generation with Ollama and ChromaDB
- **CSV Ingestion**: Automatic processing of customer service data
- **Vector Search**: Semantic search through embedded documents
- **Chat API**: RESTful endpoints for real-time chat
- **Agent Support**: Console for monitoring and responding to chats

### Frontend (React)
- **Chat Widget**: Embeddable chat interface
- **Agent Console**: Dashboard for customer service agents
- **Real-time Updates**: Live chat functionality
- **Responsive Design**: Works on all devices

### Django Site
- **Marketing Pages**: Beautiful Airbnb-inspired design
- **Contact Forms**: Integrated contact system
- **Widget Integration**: Embedded React chat widget
- **Static File Serving**: Optimized for production

## Setup Instructions

### 1. Backend Setup

```bash
cd backend_fastapi
pip install -r requirements.txt

# Start Ollama (separate terminal)
ollama serve
ollama pull llama2

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Start FastAPI
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Django Setup

```bash
cd company_site_backend_django
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Start Django
python manage.py runserver
```

### 3. React Widget Setup

```bash
cd frontend_widget
npm install
npm run build

# Copy build files to Django static
cp -r build/* ../company_site_backend_django/static/chat_widget/
```

## API Endpoints

### FastAPI (http://localhost:8000)
- `POST /chat/query` - Send chat message
- `GET /chat/pending` - Get pending chats for agents
- `POST /chat/agent_respond` - Agent response to chat
- `POST /admin/ingest_csv` - Ingest CSV data
- `GET /admin/collection_stats` - Get database stats
- `GET /health` - Health check

### Django (http://localhost:8000)
- `/` - Home page
- `/about/` - About page
- `/contact/` - Contact page
- `/contact/submit/` - Contact form submission

## Usage

1. **Data Ingestion**: Upload CSV files to `/backend_fastapi/data/` and call `/admin/ingest_csv`
2. **Chat**: Use the widget on Django pages or directly via API
3. **Agent Console**: Access at `http://localhost:3000/agent` for monitoring
4. **Customer Support**: Real-time chat with AI assistance and agent oversight

## Configuration

### Environment Variables (.env)
```
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama2
CHROMA_PERSIST_DIRECTORY=./chroma_db
CHROMA_COLLECTION_NAME=airbnb_support
```

### Deployment
- FastAPI: Use `uvicorn` with `--host 0.0.0.0` for production
- Django: Configure `ALLOWED_HOSTS` and use `gunicorn`
- React: Built files are served by Django's static file handler

## Development Notes

- **CORS**: Configured for local development
- **Security**: Update secret keys and CORS origins for production
- **Database**: ChromaDB with persistent storage
- **Monitoring**: Health check endpoints available
- **Scaling**: Consider Redis for session storage in production

## Technologies Used

- **Backend**: FastAPI, Python, ChromaDB, LangChain
- **AI**: Ollama (Llama2), Sentence Transformers
- **Frontend**: React, Tailwind CSS, Lucide Icons
- **Database**: ChromaDB (vector), SQLite (Django)
- **Deployment**: Django + WhiteNoise for static files

This system provides a complete AI-powered customer service solution with beautiful UI, intelligent responses, and comprehensive monitoring capabilities.