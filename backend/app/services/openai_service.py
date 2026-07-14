from openai import OpenAI
from app.core.config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def ask_llm(question: str):

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful medical assistant."
            },
            {
                "role": "user",
                "content": question
            }
        ]
    )

    return response.choices[0].message.content