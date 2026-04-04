# VLSI Nexus — AI ECE Dynamic Planner

A Flask-based web application that uses the Gemini API to generate prerequisite
dependency graphs and time-blocked study schedules for VLSI / ECE topics.

## Project Structure

```
vlsi_nexus/
├── app.py               # Flask application & API routes
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variable template
├── templates/
│   └── index.html       # Single-page frontend (Tailwind + Mermaid + vanilla JS)
└── static/              # Reserved for future CSS / JS assets
    ├── css/
    └── js/
```

## Key Architecture Changes vs. Original

| Original (single HTML file)          | Flask App                                   |
|--------------------------------------|---------------------------------------------|
| PyScript (Python in browser/WASM)    | Server-side Python via Flask routes         |
| API key hardcoded / exposed client   | API key stored as environment variable      |
| NetworkX runs in browser via PyScript | NetworkX available server-side if needed   |
| Gemini called directly from browser  | Gemini called from `/api/synthesize-graph` and `/api/generate-schedule` |
| Topological sort via NetworkX/WASM   | Kahn's algorithm implemented in vanilla JS  |

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set your Gemini API key

```bash
export GEMINI_API_KEY=your_key_here
# or copy .env.example to .env and source it
```

### 3. Run the development server

```bash
python app.py
```

Visit http://127.0.0.1:5000

## API Endpoints

### POST `/api/synthesize-graph`
- **Body:** `{ "concept": "Current Mirrors in MOSFETs" }`
- **Returns:** `{ "graph": { "Topic A": { "prereqs": [] }, ... } }`

### POST `/api/generate-schedule`
- **Body:** `{ "goal": "3 day plan", "required_topics": ["Topic A", "Topic B"] }`
- **Returns:** `{ "schedule": [{ "time": "...", "title": "...", "description": "..." }] }`

## Production Deployment

For production use, replace `app.run(debug=True)` with a proper WSGI server:

```bash
pip install gunicorn
gunicorn app:app
```
