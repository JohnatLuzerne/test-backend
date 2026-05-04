from fastapi import FastAPI

conn = sqlite3.connect("game.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS portals (
    id INTEGER PRIMARY KEY,
    faction TEXT
)
""")
conn.commit()
app = FastAPI()

@app.get("/ping")
def ping():
    return {"message": "alive"}

@app.get("/echo")
def echo(value: str):
    return {"you_sent": value}


@app.get("/capture")
def capture(portal_id: int, faction: str):
    cursor.execute(
        "INSERT OR REPLACE INTO portals (id, faction) VALUES (?, ?)",
        (portal_id, faction)
    )
    conn.commit()

    return {"portal_id": portal_id, "controlled_by": faction}
