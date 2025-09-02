import json
import os

DATA_FILE = "todo_data.json"

class TodoList:
    def __init__(self, data_file=DATA_FILE):
        self.data_file = data_file
        self.tasks = self.load()
        self.spawn_counter = 0

    def load(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        out = []
                        for it in data:
                            if isinstance(it, dict):
                                out.append({
                                    "id": it.get("id", str(len(out)+1)),
                                    "text": str(it.get("text", "")),
                                    "done": bool(it.get("done", False))
                                })
                        return out
            except Exception:
                pass
        return []

    def save(self):
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.tasks, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print("Failed to save tasks:", e)

    def add(self, text):
        new_id = str(max([int(it["id"]) for it in self.tasks] + [0]) + 1)
        item = {"id": new_id, "text": text, "done": False}
        self.tasks.append(item)
        self.save()
        return item

    def toggle_done(self, tid):
        for it in self.tasks:
            if it["id"] == tid:
                it["done"] = not it["done"]
                self.save()
                return it["done"]
        return None

    def delete(self, tid):
        for i, it in enumerate(self.tasks):
            if it["id"] == tid:
                self.tasks.pop(i)
                self.save()
                return True
        return False

    def next_spawn_pos(self, base_x=260, base_y=160):
        dx = 24 * (self.spawn_counter % 10)
        dy = 24 * (self.spawn_counter % 10)
        pos = (base_x + dx, base_y + dy)
        self.spawn_counter += 1
        return pos