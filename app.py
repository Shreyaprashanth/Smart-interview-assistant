# app.py
import os, json, sqlite3, numpy as np, random
from flask import Flask, render_template, request, session, redirect, url_for, g
from sentence_transformers import SentenceTransformer
from datetime import timedelta

# optional OpenAI for better feedback
try:
    import openai
    OPENAI_AVAILABLE = True
except Exception:
    OPENAI_AVAILABLE = False

DB = "data.db"
MODEL_NAME = "all-MiniLM-L6-v2"
MODEL = SentenceTransformer(MODEL_NAME)

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET", "devsecret")
app.permanent_session_lifetime = timedelta(days=7)

# --- DB helpers ---
def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DB)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_conn(exc):
    db = getattr(g, "_database", None)
    if db:
        db.close()

def load_embedding(db_conn, qid):
    cur = db_conn.cursor()
    cur.execute("SELECT embedding FROM embeddings WHERE question_id=?", (qid,))
    r = cur.fetchone()
    if not r:
        return None
    return np.array(json.loads(r[0]), dtype=float)

# --- scoring helpers ---
def cosine_sim(a, b):
    a = np.array(a)
    b = np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-10))

def score_points(sim, streak):
    base = 0
    if sim >= 0.85:
        base = 15
    elif sim >= 0.7:
        base = 10
    elif sim >= 0.5:
        base = 5
    else:
        return 0

    # streak bonus
    bonus = streak * 2

    # critical hit chance
    if sim >= 0.85 and random.random() < 0.1:  # 10% chance
        return (base + bonus) * 2  # Critical hit!

    # combo multiplier
    if streak >= 5:
        return int((base + bonus) * 1.5)  # 1.5x after 5 streak

    return base + bonus

# --- feedback generator ---
def generate_feedback_with_openai(question, expected, user, similarity):
    if not OPENAI_AVAILABLE:
        return None
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        return None
    openai.api_key = key
    prompt = f"""
You are a helpful technical tutor. Provide:
1) One-line assessment (positive/negative) given similarity {similarity:.2f}.
2) Up to 3 bullet keywords the student missed or should mention.
3) One short follow-up question to deepen understanding.

Question: {question}
Expected answer: {expected}
Student answer: {user}
"""
    try:
        resp = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=180,
            temperature=0.6
        )
        return resp.choices[0].text.strip()
    except Exception as e:
        print("OpenAI error:", e)
        return None

def fallback_feedback(expected, user, similarity):
    exp_words = set([w.lower().strip(".,()") for w in expected.split() if len(w)>3])
    user_words = set([w.lower().strip(".,()") for w in user.split() if len(w)>3])
    missed = list(exp_words - user_words)
    keywords = ", ".join(missed[:5])
    assessment = "Good answer" if similarity>0.7 else "Partially correct" if similarity>0.5 else "Needs improvement"
    follow_up = "Can you provide an example or explain why?" if similarity<0.7 else "Can you expand with an example?"
    return f"{assessment}.\nKeywords to include: {keywords}\nFollow-up: {follow_up}"

# --- routes ---
@app.route("/")
def index():
    session.permanent = True
    session.setdefault("username", "anon")
    session.setdefault("points", 0)
    session.setdefault("streak", 0)
    return render_template("index.html", points=session["points"], streak=session["streak"])

@app.route("/start/<subject>")
def start(subject):
    session["subject"] = subject
    return redirect(url_for("ask"))

@app.route("/ask")
def ask():
    subject = session.get("subject", "os")
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT id, question, expected_answer FROM questions WHERE subject=? ORDER BY RANDOM() LIMIT 1", (subject,))
    r = cur.fetchone()
    if not r:
        return "No questions for subject: " + subject
    qid = r["id"]
    question = r["question"]
    expected = r["expected_answer"]
    session["current_qid"] = qid
    session["expected_answer"] = expected
    session["question_text"] = question
    return render_template("ask.html", question=question, subject=subject.upper(),
                           points=session.get("points", 0), streak=session.get("streak", 0))

@app.route("/check", methods=["POST"])
def check():
    user_answer = request.form.get("user_answer", "").strip()
    if user_answer == "":
        return redirect(url_for("ask"))
    db = get_db()
    qid = session.get("current_qid")
    if qid is None:
        return redirect(url_for("index"))

    expected_answer = session.get("expected_answer", "")
    expected_emb = load_embedding(db, qid)
    user_emb = MODEL.encode(user_answer)
    sim = cosine_sim(user_emb, expected_emb) if expected_emb is not None else 0.0
    pts = score_points(sim, session.get("streak", 0))

    # update gamification state
    if pts > 0:
        session["points"] = session.get("points", 0) + pts
        session["streak"] = session.get("streak", 0) + 1
    else:
        session["streak"] = 0

    # generate feedback
    feedback_text = None
    if OPENAI_AVAILABLE and os.getenv("OPENAI_API_KEY"):
        feedback_text = generate_feedback_with_openai(session["question_text"], expected_answer, user_answer, sim)
    if not feedback_text:
        feedback_text = fallback_feedback(expected_answer, user_answer, sim)

    # special messages
    special_msg = ""
    if pts >= 25:
        special_msg = "💥 Critical Hit! Amazing!"
    elif session["streak"] >= 5:
        special_msg = "🔥 You're on fire! Keep going!"
    elif session["streak"] == 3:
        special_msg = "⚡ Combo x3! Streak bonus unlocked!"

    # simple badge logic
    badges = []
    total = session.get("points", 0)
    if total >= 100:
        badges.append("🏆 Subject Master")
    elif total >= 50:
        badges.append("🌟 Rising Star")

    return render_template("result.html",
                           question=session["question_text"],
                           user_answer=user_answer,
                           expected_answer=expected_answer,
                           similarity=sim,
                           points_awarded=pts,
                           total_points=session.get("points", 0),
                           streak=session.get("streak", 0),
                           badges=badges,
                           feedback=feedback_text,
                           special_msg=special_msg)

@app.route("/reset")
def reset():
    session["points"] = 0
    session["streak"] = 0
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
