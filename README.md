# Pragmatic Architect v6.0 🛡️💻

**Pragmatic Architect** is a high-performance, privacy-first AI coding agent designed to run entirely on local hardware. By bypassing cloud-based LLM APIs, it ensures absolute data sovereignty for developers working on sensitive or proprietary codebases.

---

## 🌟 The Moto
The mission of this project is to provide an **Air-Gapped AI Partner**. In an era where code is frequently sent to external servers for inference, Pragmatic Architect returns power to the developer by keeping 100% of the computation on local silicon.

---

## 🛠️ Core Technical Features

* **Local Inference Pipeline**: Integrated with **Ollama** to run models like `qwen2.5-coder` locally, ensuring zero data leakage and offline availability.
* **Multi-threaded Architecture**: Separates the **Reasoning Engine (LLM)** from the **UI Thread** to maintain a responsive interface during heavy computation.
* **Stateless Context Injection**: Dynamically injects local file data into the model’s reasoning window for deep project awareness without permanent data storage.
* **Two-Panel Streamlined GUI**: Built with **CustomTkinter** for a modern, high-DPI scaled developer experience.
* **Persistent Session Management**: Custom JSON-based memory layer to track, rename, and switch between coding projects.

---

## 🚀 Getting Started

### 1. Prerequisites
* Install [Ollama](https://ollama.com/).
* Pull the required model:
  ```bash
  ollama pull qwen2.5-coder:1.5b
2. Installation
Clone the repository and install the dependencies:

Bash
git clone [https://github.com/YOUR_USERNAME/coding-agent.git](https://github.com/YOUR_USERNAME/coding-agent.git)
cd coding-agent
pip install -r requirements.txt
3. Usage
Run the application:

Bash
python app.py
🏗️ System Architecture
The agent follows a concurrency-first approach to handle local AI processing:

User Interface (UI): Manages interactions and rendering via CustomTkinter.

Reasoning Thread: Handles background communication with the local Ollama server.

Local Hardware: All inference is processed by your local CPU/GPU.

🔒 Security & Privacy
No Cloud Dependency: Works without an internet connection once the model is downloaded.

Local Memory: Chat histories are stored in your local sessions/ directory in JSON format.

Open Source: Fully transparent codebase with no hidden data collection.