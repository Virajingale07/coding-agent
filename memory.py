import json
import os
import glob


class AgentMemory:
    def __init__(self, session_id="default"):
        self.sessions_dir = "sessions"
        if not os.path.exists(self.sessions_dir):
            os.makedirs(self.sessions_dir)

        self.session_id = session_id
        self.memory_file = os.path.join(self.sessions_dir, f"{self.session_id}.json")

        # New: Initialize project_context
        self.project_context = ""
        self.history = self.load_memory()

    def load_memory(self):
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    data = json.load(f)
                    # Support both old format (list) and new format (dict)
                    if isinstance(data, dict):
                        self.project_context = data.get("project_context", "")
                        return data.get("history", self.get_default_history())
                    return data
            except:
                return self.get_default_history()
        return self.get_default_history()

    def save_memory(self):
        # Save both history and project_context to the JSON file
        with open(self.memory_file, 'w') as f:
            json.dump({
                "history": self.history,
                "project_context": self.project_context
            }, f, indent=4)

    def rename_session(self, new_name):
        """Renames the current session safely, even if the file isn't on disk yet."""
        # Clean the name for Windows file system compatibility
        new_name = "".join(c for c in new_name if c.isalnum() or c in (' ', '-', '_')).strip()
        new_file = os.path.join(self.sessions_dir, f"{new_name}.json")

        if os.path.exists(new_file) or not new_name:
            return False

        # If the current session already has a file on disk, rename it
        if os.path.exists(self.memory_file):
            try:
                os.rename(self.memory_file, new_file)
            except Exception as e:
                print(f"Rename error: {e}")
                return False

        # Update internal paths
        self.session_id = new_name
        self.memory_file = new_file

        # Force a save so the new filename is created immediately
        self.save_memory()
        return True

    def get_default_history(self):
        return [
            {
                "role": "system",
                "content": (
                    "You are a Pragmatic Senior Developer with 'Adaptive Complexity' logic. "
                    "Follow these rules for every request:\n"
                    "1. ANALYZE SCALE: Determine if the task is a 'Simple Logic/Algorithm' or a 'Production System'.\n"
                    "2. SIMPLE TASKS: If the request is a basic algorithm (e.g., prime numbers, sorting, math), "
                    "provide a clean, standard solution .\n"
                    "3. PRODUCTION TASKS: If the request involves I/O, Web, or API work, use robust patterns "
                    "4. LANGUAGE INTEGRITY: Never suggest Python libraries (like aiohttp) when writing in other languages .\n"
                    "5. BE CONCISE: Avoid fluff. Focus on high-quality, idiomatic code."
                )
            }
        ]

    def add_message(self, role, content):
        self.history.append({"role": role, "content": content})
        if len(self.history) > 20:
            self.history = [self.history[0]] + self.history[-19:]
        self.save_memory()

    def get_context(self):
        return self.history

    def get_all_sessions(self):
        files = glob.glob(os.path.join(self.sessions_dir, "*.json"))
        return [os.path.basename(f).replace(".json", "") for f in files]