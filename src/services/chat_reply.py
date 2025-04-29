from openai import OpenAI

from src.common.config import get_settings
from src.db.vector_db import VectorDBClient

settings = get_settings()


async def chat_reply(query: str, top_k: int, vector_db: VectorDBClient):
    _, _, metadata = await vector_db.search(query, top_k)

    context = ""
    for idx, doc in enumerate(metadata):
        if doc:
            doc_content = "\t ".join([f"{key}: {value}" for key, value in doc.items()])
            context += f"Review {idx+1}:\n{doc_content}\n\n"

    chat_history = ""
    system_prompt = """
    You are a highly skilled customer insights assistant. Your primary role is to help users explore and analyze customer feedback data.

    Behavior guidelines:
    - Base your answers solely on the provided **Context** (which contains retrieved customer feedback records).
    - Do not use outside knowledge or make assumptions beyond the provided information.
    - If the **Context** does not contain any information, clearly respond with: "The provided context does not contain enough information to answer this question."
    - Provide clear, concise, and insightful responses.
    - Summarize key points from the feedback records when helpful, focusing on trends, sentiments, or recurring issues.
    - Maintain a professional, objective, and informative tone at all times.
    """

    user_prompt = f"""
    You will answer the following question based strictly on the provided **Context** containing customer feedback records.

    <Context>
    {context}
    </Context>


    <Question>
    {query}
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
                    context=context, query=query
                ),
            },
        ],
        max_tokens=settings.OPENAI_MAX_TOKENS,
        temperature=settings.OPENAI_TEMPERATURE,
    )
    answer = response.choices[0].message.content

    return answer, metadata
