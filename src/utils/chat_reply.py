from openai import OpenAI

from common.config import get_settings
from db.vector_db import VectorDBClient

settings = get_settings()


async def chat_reply(query: str, top_k: int, vector_db: VectorDBClient):
    _, _, metadata = await vector_db.search(query, top_k)

    context = ""
    for idx, doc in enumerate(metadata):
        if doc:
            doc_content = "\t ".join([f"{key}: {value}" for key, value in doc.items()])
            context += f"Document {idx+1}:\n{doc_content}\n\n"

    chat_history = ""
    system_prompt = """
    You are an expert customer insights assistant. Your role is to analyze customer feedback provided in the context and generate clear, concise, and insightful answers to user questions. 

    Guidelines:
    - Use only the information provided in the **Context** to answer the question.
    - If the context does not contain enough information to answer, respond with: *"The provided context does not contain enough information to answer this question."*
    - Summarize relevant feedback items where appropriate to provide a well-rounded answer.
    - Maintain a professional, informative tone.

    <Context>
    {{context}}
    </Context>

    <Chat_History>
    {{chat_history}}
    </Chat_History>

    <Question>
    {{query}}
    </Question>

    <Answer>
    """
    openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
    response = openai_client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt.format(
                    context=context, chat_history=chat_history, query=query
                ),
            },
        ],
        max_tokens=settings.OPENAI_MAX_TOKENS,
        temperature=settings.OPENAI_TEMPERATURE,
    )
    answer = response.choices[0].message.content

    return answer, metadata
