import os
from typing import Optional

import google.generativeai as genai
import streamlit as st
from dotenv import load_dotenv
from fpdf import FPDF
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

DEFAULT_GEMINI_MODEL = "gemini-2.5-flash"
EMBEDDING_MODEL = "models/embedding-001"


def get_config_value(key: str, default: str = "") -> str:
    env_value = os.getenv(key, "").strip()
    if env_value:
        return env_value
    try:
        secret_value = st.secrets.get(key, "")
    except Exception:
        secret_value = ""
    if secret_value is None:
        return default
    if not isinstance(secret_value, str):
        secret_value = str(secret_value)
    secret_value = secret_value.strip()
    return secret_value or default


GEMINI_MODEL = get_config_value("GEMINI_MODEL", DEFAULT_GEMINI_MODEL)


def configure_gemini() -> bool:
    api_key = get_config_value("GOOGLE_API_KEY")
    if not api_key:
        return False
    genai.configure(api_key=api_key)
    return True


def is_preview_or_experimental(model_name: str) -> bool:
    lowered = model_name.lower()
    return "preview" in lowered or "-exp" in lowered or "experimental" in lowered


def normalize_for_pdf(text: str) -> str:
    replacements = {
        "\u201c": '"',
        "\u201d": '"',
        "\u2018": "'",
        "\u2019": "'",
        "\u2013": "-",
        "\u2014": "-",
        "\u2026": "...",
    }
    cleaned = text
    for old, new in replacements.items():
        cleaned = cleaned.replace(old, new)
    return cleaned.encode("latin-1", "replace").decode("latin-1")


def build_pdf_bytes(content: str, title: str) -> bytes:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", style="B", size=16)
    pdf.cell(0, 10, txt=normalize_for_pdf(title), ln=True, align="C")
    pdf.ln(6)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 8, normalize_for_pdf(content))
    raw_output = pdf.output(dest="S")
    if isinstance(raw_output, str):
        return raw_output.encode("latin-1", "replace")
    return bytes(raw_output)


def generate_model_text(prompt: str) -> str:
    model = genai.GenerativeModel(GEMINI_MODEL)
    response = model.generate_content(prompt)
    text = getattr(response, "text", "")
    return text.strip()


def extract_pdf_text(pdf_docs) -> str:
    all_text = []
    for pdf in pdf_docs:
        reader = PdfReader(pdf)
        for page in reader.pages:
            page_text = page.extract_text() or ""
            if page_text.strip():
                all_text.append(page_text.strip())
    return "\n\n".join(all_text)


def create_pdf_vector_store(raw_text: str) -> Optional[FAISS]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=150)
    chunks = [chunk for chunk in splitter.split_text(raw_text) if chunk.strip()]
    if not chunks:
        return None
    embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)
    return FAISS.from_texts(chunks, embedding=embeddings)


def answer_pdf_question(user_question: str, vector_store: FAISS) -> str:
    docs = vector_store.similarity_search(user_question, k=4)
    context = "\n\n".join(doc.page_content for doc in docs)
    prompt = f"""
You are a helpful study assistant.
Answer only from context below.
If context does not contain answer, say: Answer is not available in uploaded PDFs.

Context:
{context}

Question:
{user_question}

Answer:
"""
    return generate_model_text(prompt)


def init_session_state() -> None:
    defaults = {
        "pdf_vector_store": None,
        "quiz_content": "",
        "learning_path": "",
        "notes_content": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def chat_pdf_interface() -> None:
    st.subheader("Chat with PDFs")
    uploaded_pdfs = st.file_uploader(
        "Upload one or more PDF files",
        type=["pdf"],
        accept_multiple_files=True,
    )

    if st.button("Process PDFs", key="process_pdfs_btn"):
        if not uploaded_pdfs:
            st.warning("Upload at least one PDF before processing.")
        else:
            with st.spinner("Processing PDFs..."):
                try:
                    raw_text = extract_pdf_text(uploaded_pdfs)
                    if not raw_text.strip():
                        st.session_state.pdf_vector_store = None
                        st.error("No readable text found in uploaded PDFs.")
                    else:
                        st.session_state.pdf_vector_store = create_pdf_vector_store(raw_text)
                        if st.session_state.pdf_vector_store is None:
                            st.error("Could not create vector index from PDFs.")
                        else:
                            st.success("PDFs processed. Ask your question below.")
                except Exception as exc:
                    st.session_state.pdf_vector_store = None
                    st.error(f"PDF processing failed: {exc}")

    if st.session_state.pdf_vector_store is not None:
        st.info("PDF knowledge base ready.")

    user_question = st.text_input("Ask a question about uploaded PDFs")
    if st.button("Get Answer", key="ask_pdf_btn"):
        if not user_question.strip():
            st.warning("Enter a question first.")
        elif st.session_state.pdf_vector_store is None:
            st.warning("Process PDFs first, then ask question.")
        else:
            with st.spinner("Generating answer..."):
                try:
                    answer = answer_pdf_question(user_question, st.session_state.pdf_vector_store)
                    if answer:
                        st.write(answer)
                    else:
                        st.error("No response generated. Try rephrasing question.")
                except Exception as exc:
                    st.error(f"Failed to answer question: {exc}")


def quiz_interface() -> None:
    st.subheader("Quiz Generator")
    topic = st.text_input("Enter quiz topic")
    num_questions = st.number_input("Number of questions", min_value=1, max_value=20, value=5)

    if st.button("Generate Quiz", key="generate_quiz_btn"):
        if not topic.strip():
            st.warning("Enter topic first.")
        else:
            prompt = f"""
Generate {num_questions} multiple-choice questions on topic: {topic}.
Rules:
- 4 options per question (a, b, c, d)
- one correct answer
- include answer key after each question
"""
            with st.spinner("Generating quiz..."):
                try:
                    st.session_state.quiz_content = generate_model_text(prompt)
                    if not st.session_state.quiz_content:
                        st.error("Model returned empty quiz. Try again.")
                except Exception as exc:
                    st.session_state.quiz_content = ""
                    st.error(f"Quiz generation failed: {exc}")

    if st.session_state.quiz_content:
        st.markdown(st.session_state.quiz_content)
        st.download_button(
            "Download Quiz PDF",
            data=build_pdf_bytes(st.session_state.quiz_content, f"Quiz: {topic or 'Topic'}"),
            file_name="quiz.pdf",
            mime="application/pdf",
        )


def learning_path_interface() -> None:
    st.subheader("Learning Path Generator")
    topic = st.text_input("Enter learning topic")

    if st.button("Generate Learning Path", key="generate_path_btn"):
        if not topic.strip():
            st.warning("Enter topic first.")
        else:
            prompt = f"""
Create a structured learning path for: {topic}.
Include:
- roadmap by week
- core concepts
- best resources (free + paid)
- practical projects
- interview prep checklist
"""
            with st.spinner("Generating learning path..."):
                try:
                    st.session_state.learning_path = generate_model_text(prompt)
                    if not st.session_state.learning_path:
                        st.error("Model returned empty learning path. Try again.")
                except Exception as exc:
                    st.session_state.learning_path = ""
                    st.error(f"Learning path generation failed: {exc}")

    if st.session_state.learning_path:
        st.markdown(st.session_state.learning_path)
        st.download_button(
            "Download Learning Path PDF",
            data=build_pdf_bytes(st.session_state.learning_path, f"Learning Path: {topic or 'Topic'}"),
            file_name="learning_path.pdf",
            mime="application/pdf",
        )


def notes_interface() -> None:
    st.subheader("Smart Notes Generator")
    topic = st.text_input("Enter note topic")
    detail_level = st.selectbox("Detail level", ["Concise", "Detailed", "Comprehensive"])

    if st.button("Generate Notes", key="generate_notes_btn"):
        if not topic.strip():
            st.warning("Enter topic first.")
        else:
            prompt = f"""
Create {detail_level.lower()} study notes for: {topic}.
Include:
- definitions and key terms
- important concepts
- examples
- quick revision bullets
"""
            with st.spinner("Generating notes..."):
                try:
                    st.session_state.notes_content = generate_model_text(prompt)
                    if not st.session_state.notes_content:
                        st.error("Model returned empty notes. Try again.")
                except Exception as exc:
                    st.session_state.notes_content = ""
                    st.error(f"Notes generation failed: {exc}")

    if st.session_state.notes_content:
        st.markdown(st.session_state.notes_content)
        st.download_button(
            "Download Notes PDF",
            data=build_pdf_bytes(st.session_state.notes_content, f"Notes: {topic or 'Topic'}"),
            file_name="study_notes.pdf",
            mime="application/pdf",
        )


def main() -> None:
    st.set_page_config(page_title="AI Study Assistant", layout="wide")

    if not configure_gemini():
        st.error("Missing GOOGLE_API_KEY. Add it in .env for local run or secrets in Streamlit Cloud.")
        st.stop()

    init_session_state()
    st.title("AI Study Assistant")
    st.caption("Deploy-ready portfolio project with PDF Q&A, Quiz, Learning Path, and Notes.")
    st.caption(f"Model in use: {GEMINI_MODEL}")
    if is_preview_or_experimental(GEMINI_MODEL):
        st.warning("Current GEMINI_MODEL appears preview/experimental. For stable deploy use gemini-2.5-flash.")

    with st.sidebar:
        app_mode = st.radio(
            "Choose Feature",
            ["Chat with PDFs", "Quiz Generator", "Learning Path", "Smart Notes"],
        )

    if app_mode == "Chat with PDFs":
        chat_pdf_interface()
    elif app_mode == "Quiz Generator":
        quiz_interface()
    elif app_mode == "Learning Path":
        learning_path_interface()
    else:
        notes_interface()


if __name__ == "__main__":
    main()