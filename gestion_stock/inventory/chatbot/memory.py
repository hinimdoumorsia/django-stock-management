from langchain_community.chat_message_histories import ChatMessageHistory

# mémoire en RAM (simple MVP)
session_memories = {}

MAX_HISTORY = 20  # sécurité

def get_memory_for_session(session_id: str):
    if session_id not in session_memories:
        session_memories[session_id] = ChatMessageHistory()

    memory = session_memories[session_id]

    # limitation mémoire
    if len(memory.messages) > MAX_HISTORY:
        memory.messages = memory.messages[-MAX_HISTORY:]

    return memory