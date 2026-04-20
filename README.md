# AI Study Assistant

Project work for GenAI Course. Personalized Learning Chatbot for Students.
Built with Streamlit + Gemini API.

## Features

- Chat with PDFs using semantic search (LangChain + FAISS)
- Quiz Generator for topic-based MCQs
- Learning Path Generator with roadmap and resources
- Smart Notes Generator with detail-level control
- PDF export for generated outputs

## Tech Stack

- Python 3.11
- Streamlit
- Google Gemini API (default: gemini-2.5-flash)
- LangChain + FAISS
- PyPDF2
- fpdf2

## Project Structure

```text
resume_ready_app/
├── app.py
├── integrated_app.py
├── requirements.txt
├── runtime.txt
├── .env.example
├── .gitignore
└── .streamlit/
    ├── config.toml
    └── secrets.toml.example
```

## Local Setup

1. Create and activate virtual environment.
2. Install dependencies.
3. Create .env from .env.example.
4. Run app.

```bash
pip install -r requirements.txt
streamlit run app.py
```

Example .env values:

```env
GOOGLE_API_KEY=your_google_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

## Deploy on Streamlit Community Cloud

1. Push code to GitHub.
2. Create new app in Streamlit Community Cloud.
3. Set main file path: app.py.
4. Add secrets in app settings:

```toml
GOOGLE_API_KEY = "your_google_api_key_here"
GEMINI_MODEL = "gemini-2.5-flash"
```

5. Deploy.

## Model Notes

- Default model: gemini-2.5-flash
- Override with GEMINI_MODEL (env var or Streamlit secrets)
- Preview/experimental models not recommended for stable resume demo
