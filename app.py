from flask import Flask, render_template, request, jsonify
from groq import Groq
import json
import os

app = Flask(__name__)

# ── API config ────────────────────────────────────────────────────────────────
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

# Swap to "llama-3.3-70b-versatile" for higher quality / slower responses
GROQ_MODEL = "llama-3.1-8b-instant"

# Single shared client instance
client = Groq(api_key=GROQ_API_KEY)


# ── Helper ────────────────────────────────────────────────────────────────────
def call_groq(prompt: str) -> str:
    """Send a prompt to Groq and return the raw text response."""
    completion = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    return completion.choices[0].message.content


# ── Routes ────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/synthesize-graph", methods=["POST"])
def synthesize_graph():
    """
    Accepts a concept string, queries Groq for a prerequisite DAG,
    and returns a JSON dependency map.
    """
    data = request.get_json()
    concept = data.get("concept", "").strip()
    if not concept:
        return jsonify({"error": "No concept provided"}), 400

    prompt = f"""
    You are an expert VLSI Engineering AI.
    Generate a prerequisite dependency graph for a student learning: '{concept}'.
    Return EXACTLY a raw JSON object. Do not wrap in markdown format blocks.
    Format example:
    {{
      "Topic A": {{"prereqs": []}},
      "Topic B": {{"prereqs": ["Topic A"]}}
    }}
    Ensure strict technical accuracy [Topological Sortable Directed Acyclic Graph].
    Keep the scope focused. Limit to 5 to 8 essential nodes maximum.
    """

    try:
        raw_text = call_groq(prompt)
        clean_text = raw_text.replace("```json", "").replace("```", "").strip()
        graph = json.loads(clean_text)
        return jsonify({"graph": graph})
    except json.JSONDecodeError as e:
        return jsonify({"error": "JSON parse failed", "detail": str(e), "raw": raw_text}), 500
    except Exception as e:
        return jsonify({"error": "Groq API error", "detail": str(e)}), 502


@app.route("/api/generate-schedule", methods=["POST"])
def generate_schedule():
    """
    Accepts the user goal string and an ordered list of required topics,
    returns a JSON array of time-blocked study sessions.
    """
    data = request.get_json()
    goal = data.get("goal", "").strip()
    required_topics = data.get("required_topics", [])

    if not goal:
        return jsonify({"error": "No goal provided"}), 400
    if not required_topics:
        return jsonify({"schedule": [], "all_complete": True})

    topic_str = ", ".join(required_topics)

    prompt = f"""
    You are an expert VLSI Engineering AI integrated into a Python backend.

    USER TIME CONSTRAINTS: {goal}
    TOPOLOGICAL CRITICAL PATH (Topics to learn): {topic_str}

    CONSTRAINT 1: Explain using Silicon level analogies. Focus on electron hole physics where applicable.
    CONSTRAINT 2: Ensure absolute technical accuracy. Simplify if needed, but you MUST include the actual technical concept in brackets [like this] next to the simplification.
    CONSTRAINT 3: Generate a time blocked study schedule allocating time to each topic in the Critical Path based on the user constraints.

    OUTPUT FORMAT: You must return EXACTLY a valid JSON array of objects. Do not wrap in markdown block characters.
    Format:
    [
      {{
        "time": "Day 1: 09:00 AM to 11:00 AM",
        "title": "Topic Name",
        "description": "Detailed explanation incorporating Constraints 1 and 2."
      }}
    ]
    """

    try:
        raw_text = call_groq(prompt)
        clean_text = raw_text.replace("```json", "").replace("```", "").strip()
        schedule = json.loads(clean_text)
        return jsonify({"schedule": schedule})
    except json.JSONDecodeError as e:
        return jsonify({"error": "JSON parse failed", "detail": str(e), "raw": raw_text}), 500
    except Exception as e:
        return jsonify({"error": "Groq API error", "detail": str(e)}), 502


if __name__ == "__main__":
    app.run(debug=True)