import os
import re
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import customtkinter as ctk
import ollama
from memory import AgentMemory
import datetime


class PragmaticCodingAgent(ctk.CTk):
    def __init__(self):
        super().__init__()
        # Engines
        initial_session = datetime.datetime.now().strftime("%H-%M-%S")
        self.memory = AgentMemory(session_id=initial_session)
        self.model = "qwen2.5-coder:1.5b"

        # UI Config
        self.title("Coding agent")
        self.geometry("1100x850")
        ctk.set_appearance_mode("dark")

        # Sidebar
        self.sidebar_frame = ctk.CTkFrame(self, width=240, corner_radius=0)
        self.sidebar_frame.pack(side="left", fill="y")

        self.new_chat_btn = ctk.CTkButton(self.sidebar_frame, text="+ New Session", fg_color="#238636",
                                          command=self.create_new_session)
        self.new_chat_btn.pack(pady=20, padx=20)

        self.session_list_container = ctk.CTkScrollableFrame(self.sidebar_frame, fg_color="transparent")
        self.session_list_container.pack(fill="both", expand=True, padx=5)

        # --- MAIN CHAT PANEL ---
        self.chat_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#1e1e1e")
        self.chat_frame.pack(side="right", fill="both", expand=True)

        self.status_label = ctk.CTkLabel(self.chat_frame, text="SYSTEM STATUS: IDLE", font=("Arial", 10),
                                         text_color="#777")
        self.status_label.pack(pady=2)

        self.chat_display = ctk.CTkTextbox(self.chat_frame, font=("Segoe UI", 14), border_width=0, state="disabled")
        self.chat_display.pack(padx=20, pady=(5, 10), fill="both", expand=True)

        # Styling Tags
        self.chat_display.tag_config("user_tag", foreground="#4cc9f0")
        self.chat_display.tag_config("agent_tag", foreground="#f72585")
        self.chat_display.tag_config("system_tag", foreground="#777777")


        # Input Area
        self.input_container = ctk.CTkFrame(self.chat_frame, fg_color="transparent")
        self.input_container.pack(padx=20, pady=20, fill="x")

        self.attach_btn = ctk.CTkButton(self.input_container, text="+", width=40, height=45,
                                        fg_color="#343541", hover_color="#40414f", font=("Arial", 20),
                                        command=self.upload_single_file)
        self.attach_btn.pack(side="left", padx=(0, 5))

        self.input_entry = ctk.CTkEntry(self.input_container, placeholder_text="Ask about your code...", height=45)
        self.input_entry.pack(side="left", fill="x", expand=True)
        self.input_entry.bind("<Return>", lambda e: self.start_generation())

        self.chat_display.bind("<Button-3>", self.show_copy_menu)
        self.refresh_session_sidebar()

    def show_copy_menu(self, event):
        """Right-click menu that works on disabled text boxes."""
        menu = tk.Menu(self, tearoff=0, bg="#202123", fg="white", activebackground="#40414f")

        selection = self.chat_display.get("sel.first", "sel.last")
        if selection:
            menu.add_command(label="📋 Copy Selection", command=self.copy_text)

        menu.tk_popup(event.x_root, event.y_root)

    def copy_text(self):
        """Manual copy trigger for selected text."""
        try:
            content = self.chat_display.get("sel.first", "sel.last")
            self.clipboard_clear()
            self.clipboard_append(content)
            self.status_label.configure(text="SYSTEM STATUS: TEXT COPIED", text_color="#4cc9f0")
        except tk.TclError:
            pass

    # --- Core Methods ---
    def upload_single_file(self):
        path = filedialog.askopenfilename(
            filetypes=[("Code Files", "*.py *.java *.js *.html *.css *.txt"), ("All Files", "*.*")])
        if path:
            try:
                file_name = os.path.basename(path)
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                display_msg = f"📎 📄 File: {file_name}"
                self.memory.project_context += f"\n--- FILE: {file_name} ---\n{content}\n"
                self.memory.add_message("system", display_msg)

                self.chat_display.configure(state="normal")
                self.chat_display.insert("end", f"\n{display_msg}\n", "system_tag")
                self.chat_display.configure(state="disabled")
                self.chat_display.see("end")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def start_generation(self):
        query = self.input_entry.get()
        if not query: return

        if any(char in self.memory.session_id for char in ["-", ":"]):
            clean_name = re.sub(r'[^\w\s-]', '', query[:25]).strip()
            if clean_name and self.memory.rename_session(clean_name):
                self.refresh_session_sidebar()

        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", "\nUSER ➤ ", "user_tag")
        self.chat_display.insert("end", f"{query}\n\n")
        self.chat_display.insert("end", "AGENT 🤖 ", "agent_tag")
        self.chat_display.configure(state="disabled")

        self.input_entry.delete(0, "end")
        self.status_label.configure(text="SYSTEM STATUS: THINKING...", text_color="#f72585")
        threading.Thread(target=self.generation_thread, args=(query,), daemon=True).start()

    def generation_thread(self, query):
        messages = self.memory.get_context().copy()
        if self.memory.project_context:
            messages.insert(1, {"role": "system", "content": f"FILES:\n{self.memory.project_context}"})

        messages.append({"role": "user", "content": query})
        full_text = ""
        try:
            stream = ollama.chat(model=self.model, messages=messages, stream=True)
            for chunk in stream:
                content = chunk['message']['content']
                full_text += content
                self.after(0, lambda c=content: self.update_ui(c))

            self.memory.add_message("user", query)
            self.memory.add_message("assistant", full_text)
            self.after(50, lambda: self.highlight_code(full_text))
            self.after(0, lambda: self.status_label.configure(text="SYSTEM STATUS: IDLE", text_color="#777"))
        except Exception as e:
            self.after(0, lambda: self._err(e))

    def update_ui(self, chunk):
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", chunk)
        self.chat_display.see("end")
        self.chat_display.configure(state="disabled")

    def highlight_code(self, text):
        """Finds code blocks and colors them."""
        self.chat_display.configure(state="normal")
        for match in re.finditer(r"```(?:\w+)?\n(.*?)\n```", text, re.DOTALL):
            code = match.group(1)
            start = self.chat_display.search(code, "1.0", tk.END)
            if start:
                end = f"{start} + {len(code)} chars"
                self.chat_display.tag_add("code_block", start, end)
        self.chat_display.configure(state="disabled")

    # --- Session Management (Fixes your AttributeError) ---
    def create_new_session(self):
        new_id = datetime.datetime.now().strftime("%H-%M-%S")
        self.switch_session(new_id)

    def switch_session(self, session_id):
        self.memory = AgentMemory(session_id=session_id)
        self.chat_display.configure(state="normal")
        self.chat_display.delete("1.0", "end")
        for msg in self.memory.get_context():
            if msg["role"] == "user":
                self.chat_display.insert("end", "\nUSER ➤ ", "user_tag")
                self.chat_display.insert("end", f"{msg['content']}\n\n")
            elif msg["role"] == "assistant":
                self.chat_display.insert("end", "AGENT 🤖 ", "agent_tag")
                self.chat_display.insert("end", f"{msg['content']}\n")
                self.highlight_code(msg['content'])
            elif msg["role"] == "system" and "📎" in msg["content"]:
                self.chat_display.insert("end", f"\n{msg['content']}\n", "system_tag")
        self.chat_display.configure(state="disabled")
        self.refresh_session_sidebar()

    def refresh_session_sidebar(self):
        for w in self.session_list_container.winfo_children(): w.destroy()
        for s in self.memory.get_all_sessions():
            f = ctk.CTkFrame(self.session_list_container, fg_color="transparent")
            f.pack(fill="x", pady=2)
            clr = "#333" if s == self.memory.session_id else "transparent"
            b = ctk.CTkButton(f, text=s, fg_color=clr, anchor="w", width=150,
                              command=lambda sid=s: self.switch_session(sid))
            b.pack(side="left")
            b.bind("<Button-3>", lambda e, sid=s: self.show_sidebar_menu(e, sid))
            ctk.CTkButton(f, text="X", width=30, fg_color="#900", command=lambda sid=s: self.delete_session(sid)).pack(
                side="right")

    def show_sidebar_menu(self, event, sid):
        m = tk.Menu(self, tearoff=0)
        m.add_command(label="✏️ Rename", command=lambda: self.manual_rename(sid))
        m.tk_popup(event.x_root, event.y_root)

    def manual_rename(self, old):
        new = simpledialog.askstring("Rename", f"Rename '{old}':")
        if new and AgentMemory(session_id=old).rename_session(new):
            if self.memory.session_id == old: self.memory.session_id = new
            self.refresh_session_sidebar()

    def delete_session(self, sid):
        if messagebox.askyesno("Delete", f"Delete {sid}?"):
            p = os.path.join("sessions", f"{sid}.json")
            if os.path.exists(p): os.remove(p)
            self.create_new_session()

    def _err(self, e):
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", f"\nError: {e}\n", "system_tag")
        self.chat_display.configure(state="disabled")


if __name__ == "__main__":
    app = PragmaticCodingAgent()
    app.mainloop()