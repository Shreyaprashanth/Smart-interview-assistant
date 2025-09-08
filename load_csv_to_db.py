
import sqlite3
import csv
import os

DB = "data.db"

# Create table if not exists
def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject TEXT,
        question TEXT,
        expected_answer TEXT
    )
    """)
    conn.commit()
    conn.close()

# Load CSV into DB
def load_csv(filename, subject):
    if not os.path.exists(filename):
        print(f"⚠️ File not found: {filename}")
        return

    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    with open(filename, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            q = row.get("question") or row.get("Question")
            ans = row.get("expected_answer") or row.get("Answer")

            if q and ans:
                cur.execute(
                    "INSERT INTO questions (subject, question, expected_answer) VALUES (?, ?, ?)",
                    (subject, q.strip(), ans.strip())
                )

    conn.commit()
    conn.close()
    print(f"✅ Loaded {filename} into subject '{subject}'")

if __name__ == "__main__":
    init_db()
    load_csv("data/cn_questions.csv", "cn")
    load_csv("data/dbms_questions.csv", "dbms")
    load_csv("data/os_interview_questions.csv", "os")

    print("🎉 All CSVs loaded successfully!")
