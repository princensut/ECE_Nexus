# 🚀 VLSI Nexus — AI-Powered ECE Dynamic Planner

VLSI Nexus is a Flask-based web application that intelligently generates **prerequisite dependency graphs** and **time-optimized study schedules** for VLSI and Electronics & Communication Engineering (ECE) topics using the Gemini API.

It transforms a simple topic into a structured learning path—helping students move from confusion to clarity with guided progression.

---

## ✨ Features

* 🧠 **AI-Generated Learning Graphs**
  Automatically builds prerequisite relationships between concepts.

* 📅 **Smart Study Schedules**
  Converts required topics into actionable, time-blocked plans.

* 🔐 **Secure API Handling**
  Keeps API keys safely on the server (no client exposure).

* ⚡ **Lightweight Frontend**
  Single-page UI using Tailwind CSS, Mermaid.js, and vanilla JavaScript.

* 🔄 **Dynamic Workflow**
  From topic → dependency graph → personalized study plan.

---

## 🏗️ Project Structure

```
vlsi_nexus/
├── app.py               # Flask app with API routes
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
├── templates/
│   └── index.html       # Frontend (Tailwind + Mermaid + JS)
└── static/              # Optional static assets
    ├── css/
    └── js/
```

---

## ⚙️ Architecture Overview

| Component          | Previous Approach       | Current Implementation              |
| ------------------ | ----------------------- | ----------------------------------- |
| Python Execution   | PyScript (browser/WASM) | Flask (server-side Python)          |
| API Key Handling   | Exposed in frontend     | Stored securely in environment vars |
| Graph Processing   | NetworkX in browser     | Optional server-side processing     |
| Gemini Integration | Direct browser calls    | Backend API endpoints               |
| Topological Sort   | NetworkX                | Kahn’s Algorithm (JS)               |

---

## 🔧 Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Set your Gemini API key:

```bash
export GEMINI_API_KEY=your_api_key_here
```

Or use the `.env` file:

```bash
cp .env.example .env
```

---

### 3. Run the Application

```bash
python app.py
```

Visit:

```
http://127.0.0.1:5000
```

---

## 🔌 API Endpoints

### 📊 Generate Dependency Graph

**POST** `/api/synthesize-graph`

**Request Body:**

```json
{
  "concept": "Current Mirrors in MOSFETs"
}
```

**Response:**

```json
{
  "graph": {
    "Topic A": { "prereqs": [] }
  }
}
```

---

### 📅 Generate Study Schedule

**POST** `/api/generate-schedule`

**Request Body:**

```json
{
  "goal": "3 day plan",
  "required_topics": ["Topic A", "Topic B"]
}
```

**Response:**

```json
{
  "schedule": [
    {
      "time": "...",
      "title": "...",
      "description": "..."
    }
  ]
}
```

---

## 🚀 Production Deployment

For production environments, avoid using Flask’s built-in server.

### Use Gunicorn:

```bash
pip install gunicorn
gunicorn app:app
```

---

## 💡 Use Cases

* 📘 VLSI / ECE exam preparation
* 🧩 Breaking down complex engineering topics
* ⏳ Time-constrained study planning
* 🧠 Concept dependency visualization

---

## 🔮 Future Improvements

* User authentication & saved plans
* Export schedules (PDF / calendar integration)
* Interactive graph editing
* Advanced analytics on learning progress

---

## 🤝 Contributing

Contributions are welcome! Feel free to fork the repo and submit pull requests for improvements, bug fixes, or new features.

---

## 📜 License

This project is open-source and available under the MIT License.

---

## 🙌 Acknowledgments

* Gemini API for intelligent content generation
* Mermaid.js for graph visualization
* Tailwind CSS for UI design

---

**Built to make learning VLSI structured, efficient, and actually manageable.**
