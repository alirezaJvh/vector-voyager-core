from src.common.config import get_settings
from openai import OpenAI

from src.db.vector_db import VectorDBClient

settings = get_settings()

 
async def chat_reply(query: str, top_k: int):
    vector_db = VectorDBClient()
    _, _, metadata = await vector_db.search(query, top_k)

    context = ""
    for idx, doc in enumerate(metadata):
        print(doc)
        if doc:
            doc_content = "\t ".join([f"{key}: {value}" for key, value in doc.items()])
            context += f"Document {idx+1}:\n{doc_content}\n\n"

    # TODO: use better prompt
    chat_history = ""
    system_prompt = """
    You are a helpful assistant that answers questions based on the provided context.
    """
    user_prompt = """
    Answer the following question based on the provided context.
    
    Context:
    {{context}}
    
    <chat_history>
    {{chat_history}}
    </chat_history>
    
    Question: {{query}}
    
    Answer:
    """
    openai_client = OpenAI(
        api_key=settings.OPENAI_API_KEY
    )
    response = openai_client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {"role": "user", "content": user_prompt.format(context=context, chat_history=chat_history, query=query)},
        ],
        max_tokens=settings.OPENAI_MAX_TOKENS,
        temperature=settings.OPENAI_TEMPERATURE,
    )
    answer = response.choices[0].message.content

    return answer, metadata
