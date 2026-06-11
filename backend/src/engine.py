import os
from langchain_mistralai import ChatMistralAI, MistralAIEmbeddings
from langchain_classic.prompts import PromptTemplate
from langchain_chroma import Chroma
from langchain_classic.chains import ConversationalRetrievalChain

CONFIG = {
    "company_name": "CloudMerg",
    "location": "Doha, Qatar (Qatar Financial Centre)",
    "description": "specializing in custom software development, education management systems, and AI-driven solutions.",
    "contact_email": "info@cloudmerg.com",
    "tone": "professional and helpful"
}


# # =========================
# # NORMAL (NON-STREAMING)
# # =========================
# def get_chat_response(user_query, chat_history, api_key):

#     embeddings = MistralAIEmbeddings(
#         model="mistral-embed",
#         mistral_api_key=api_key
#     )

#     persist_directory = "data/processed/chroma_db"

#     if not os.path.exists(persist_directory):
#         return "System Error: Database not found. Please run ingest.py first."

#     vector_db = Chroma(
#         persist_directory=persist_directory,
#         embedding_function=embeddings
#     )

#     llm = ChatMistralAI(
#         model="mistral-small-latest",
#         mistral_api_key=api_key,
#         temperature=0.1
#     )

#     template = f"""
#     You are the official AI Assistant for {CONFIG['company_name']}.

#     RULES:
#     - Be concise and professional.
#     - Use context when relevant.
#     - If unknown, suggest contacting {CONFIG['contact_email']}.
#     - Tone: {CONFIG['tone']}.
#     - Always respond in the same language as the user's question.
#     - If the user asks in English, answer in English.
#     - If the user asks in Arabic, answer in Arabic.
#     - Do not answer in any language other than the user's language.
#     - If the user's language cannot be identified, answer in English.

#     Context: {{context}}
#     Question: {{question}}

#     Answer:
#     """

#     QA_CHAIN_PROMPT = PromptTemplate(
#         input_variables=["context", "question"],
#         template=template,
#     )

#     retriever = vector_db.as_retriever(search_kwargs={"k": 3})

#     qa_chain = ConversationalRetrievalChain.from_llm(
#         llm=llm,
#         retriever=retriever,
#         combine_docs_chain_kwargs={"prompt": QA_CHAIN_PROMPT},
#         return_source_documents=False,
#         output_key="answer"
#     )

#     result = qa_chain.invoke({
#         "question": user_query,
#         "chat_history": chat_history
#     })

#     return result.get("answer", "No response generated.")


# =========================
# STREAMING VERSION
# =========================
def get_chat_response_stream(user_query, chat_history, api_key):

    embeddings = MistralAIEmbeddings(
        model="mistral-embed",
        mistral_api_key=api_key
    )

    persist_directory = "data/processed/chroma_db"

    if not os.path.exists(persist_directory):
        yield "System Error: Database not found. Please run ingest.py first."
        return

    vector_db = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings
    )

    llm = ChatMistralAI(
        model="mistral-small-latest",
        mistral_api_key=api_key,
        temperature=0.0
    )

    template = f"""
    You are the official AI Assistant for {CONFIG['company_name']}.

    RULES:
    - Answer with the shortest clear response possible.
    - Do not add extra details, explanations, or marketing language.
    - Do not use bullet lists unless explicitly requested.
    - Always respond in the same language as the user's question.
    - If the user asks in English, answer in English.
    - If the user asks in Arabic, answer in Arabic.
    - If the user's language cannot be determined, answer in English.
    - If the user asks for contact details, provide only the requested contact information.
    - Keep answers under two sentences whenever possible.
    - Be professional, direct, and efficient.
    - Use context only when it directly helps answer the question.
    - If unknown, ask a brief clarifying question.

    Context: {{context}}
    Question: {{question}}

    Answer:
    """

    QA_CHAIN_PROMPT = PromptTemplate(
        input_variables=["context", "question"],
        template=template,
    )

    retriever = vector_db.as_retriever(search_kwargs={"k": 3})

    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        combine_docs_chain_kwargs={"prompt": QA_CHAIN_PROMPT},
        return_source_documents=False,
        output_key="answer"
    )

    try:
        result = qa_chain.invoke({
            "question": user_query,
            "chat_history": chat_history
        })

        answer = result.get("answer", "")

        # fallback if empty
        if not answer:
            yield "I'm here to help. Could you rephrase your question?"
            return

        # STREAM RESPONSE CHARACTER BY CHARACTER
        for char in answer:
            yield char

    except Exception as e:
        yield f"Error: {str(e)}"