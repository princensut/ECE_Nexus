from flask import Flask, render_template, request, jsonify

import json
import re
import os
import requests

app = Flask(__name__)


# ── Robust JSON extractor ─────────────────────────────────────────────────────
def extract_json(text: str):
    """
    Pulls a JSON object or array out of a string that may be wrapped in
    markdown fences, have leading/trailing prose, or contain stray characters.
    Tries in order:
      1. Strip common markdown fences, then parse directly.
      2. Regex-extract the first {...} or [...] block, then parse.
    Raises json.JSONDecodeError if nothing works.
    """
    # 1. Strip all flavours of markdown code fences
    cleaned = re.sub(r"```(?:json)?\s*", "", text, flags=re.IGNORECASE).replace("```", "").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # 2. Pull the first {...} or [...] block (handles leading prose)
    for pattern in (r"(\{[\s\S]*\})", r"(\[[\s\S]*\])"):
        m = re.search(pattern, text)
        if m:
            try:
                return json.loads(m.group(1))
            except json.JSONDecodeError:
                pass

    # Nothing worked — raise so the caller can return a useful error
    raise json.JSONDecodeError("No valid JSON found in model response", text, 0)


# ── API config ────────────────────────────────────────────────────────────────
GROQ_API_KEY = "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" # <-- paste your key here
GROQ_MODEL = "llama-3.1-8b-instant"
GROQ_URL     = "https://api.groq.com/openai/v1/chat/completions"


# ── Helper — uses plain requests, no groq SDK ─────────────────────────────────
def call_groq(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3,
        "max_tokens": 2048,
    }
    resp = requests.post(GROQ_URL, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


# ── Debug route ───────────────────────────────────────────────────────────────
GROQ_API_KEY = "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"

@app.route("/api/debug")
def debug():
    
    key_status = "SET" if GROQ_API_KEY else "MISSING"
    try:
        result = call_groq("Reply with just the word: OK")
        api_status = "OK — " + result.strip()
    except Exception as e:
        api_status = f"FAILED — {str(e)}"

    return jsonify({
        "api_key_status": key_status,
        "model": GROQ_MODEL,
        "groq_call": api_status,
    })


# ── Routes ────────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/synthesize-graph", methods=["POST"])
def synthesize_graph():
    data = request.get_json()
    concept = data.get("concept", "").strip()
    if not concept:
        return jsonify({"error": "No concept provided"}), 400

    prompt = f"""
    You are an expert VLSI Engineering AI.
    Generate a prerequisite dependency graph for a student learning: '{concept}'.
    Return ONLY a raw JSON object — no markdown, no explanation, no extra text.
    Format:
    {{
      "Topic A": {{"prereqs": []}},
      "Topic B": {{"prereqs": ["Topic A"]}}
    }}
    Rules: topologically sortable DAG, 5–8 nodes maximum, strict technical accuracy.
    """

    try:
        raw_text = call_groq(prompt)
        graph = extract_json(raw_text)
        return jsonify({"graph": graph})
    except json.JSONDecodeError as e:
        return jsonify({"error": "JSON parse failed", "detail": str(e), "raw": raw_text}), 500
    except Exception as e:
        return jsonify({"error": "Groq API error", "detail": str(e)}), 502


@app.route("/api/generate-schedule", methods=["POST"])
def generate_schedule():
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
    CONSTRAINT 2: Ensure absolute technical accuracy. Simplify if needed, but include the actual technical concept in brackets [like this].
    CONSTRAINT 3: Generate a time-blocked study schedule allocating time to each topic based on user constraints.

    Return ONLY a raw JSON array — no markdown, no explanation, no extra text.
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
        schedule = extract_json(raw_text)
        return jsonify({"schedule": schedule})
    except json.JSONDecodeError as e:
        return jsonify({"error": "JSON parse failed", "detail": str(e), "raw": raw_text}), 500
    except Exception as e:
        return jsonify({"error": "Groq API error", "detail": str(e)}), 502


if __name__ == "__main__":
    app.run(debug=False)
