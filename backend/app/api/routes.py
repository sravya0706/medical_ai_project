
from fastapi import APIRouter
from app.services.openai_service import ask_llm

router = APIRouter()


@router.get("/ask")
def ask(question: str):

    answer = ask_llm(question)

    return {
        "question": question,
        "answer": answer
    }