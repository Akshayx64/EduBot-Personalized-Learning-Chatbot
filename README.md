# AI Study Assistant

Production-ready GenAI study app for portfolio and resume demos.
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

## If .streamlit Folder Cannot Be Uploaded

Some web upload tools skip dot-folders.
Good news: app does not require .streamlit files in repo to run on cloud.

Use this flow:

1. Upload all non-hidden files.
2. In Streamlit Cloud, add secrets manually in app settings.
3. Deploy normally.

Visible helper templates included:

1. streamlit_secrets_template.toml
2. streamlit_config_template.toml

Optional better method:

1. Use git push from terminal instead of web upload.
2. Dot-folders upload correctly with git.

## Model Notes

- Default model: gemini-2.5-flash
- Override with GEMINI_MODEL (env var or Streamlit secrets)
- Preview/experimental models not recommended for stable resume demo

## Resume Highlights

- Built deployable AI learning platform with 4 user workflows
- Implemented PDF Q&A with embedding-based retrieval
- Added production-grade input checks and error handling

## Project Reflection (150 words)

Problem identified: Many students waste time switching between scattered tools for notes, quizzes, and resource planning, while PDF-based revision is slow and inconsistent. Existing workflows also break easily when deployed, especially around environment configuration and model version drift. Result: good ideas fail during demos and feel unreliable in real use.

Approach taken: I built a single Streamlit application that combines PDF Q&A, quiz generation, learning-path planning, and smart notes in one interface. I added input validation, safer defaults, and clear configuration handling through environment variables and Streamlit secrets. I also standardized model selection to a stable Gemini release and packaged deployment files for quick hosting.

What I would improve today: I would add user authentication, persistent history, caching for repeated prompts, and structured output parsing. I would also add tests, telemetry, and better UI polish for mobile usage. These steps would improve reliability, observability, and confidence for recruiters and users.

## Author

- Sachin Tambe
- GitHub: https://github.com/Sachin-Tambe

