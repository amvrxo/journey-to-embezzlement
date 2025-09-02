
class TodoList:
    def __init__(self):
        self._next_id = 1
        self.tasks = []  # list of dicts: {"id": int, "text": str, "done": bool}

    def add(self, text: str):
        item = {"id": self._next_id, "text": text, "done": False}
        self._next_id += 1
        self.tasks.append(item)
        return item

    def toggle_done(self, tid: int):
        for t in self.tasks:
            if t["id"] == tid:
                t["done"] = not t["done"]
                return t["done"]
        return None

    def delete(self, tid: int):
        self.tasks = [t for t in self.tasks if t["id"] != tid]
