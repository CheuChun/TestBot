history = {}
MAX_HISTORY = 5

def add_message(user_id: int, role: str, content: str):
    if user_id not in history:
        history[user_id] = []

    history[user_id].append({"role": role, "content": content})

    if len(history[user_id]) > MAX_HISTORY:
        history[user_id] = history[user_id][-MAX_HISTORY:]

def get_history(user_id: int):
    return history.get(user_id, [])
