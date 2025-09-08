# build_embeddings.py
import sqlite3, json
from sentence_transformers import SentenceTransformer
import numpy as np

DB = "data.db"
MODEL_NAME = "all-MiniLM-L6-v2"  # small and fast

def main():
    model = SentenceTransformer(MODEL_NAME)
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT id, expected_answer FROM questions")
    rows = cur.fetchall()
    print(f"Encoding {len(rows)} answers with {MODEL_NAME} ...")
    for qid, ans in rows:
        emb = model.encode(ans).tolist()
        cur.execute("INSERT OR REPLACE INTO embeddings(question_id, embedding) VALUES (?, ?)",
                    (qid, json.dumps(emb)))
    conn.commit()
    conn.close()
    print("Embeddings built and saved into data.db")

if __name__ == "__main__":
    main()
