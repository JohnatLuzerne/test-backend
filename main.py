from fastapi import FastAPI
import sqlite3

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

@app.get("/migrate")
def migrate():
    cursor.execute("ALTER TABLE portals ADD COLUMN lat REAL DEFAULT 0")
    cursor.execute("ALTER TABLE portals ADD COLUMN lon REAL DEFAULT 0")
    conn.commit()
    return {"status": "done"}
@app.get("/ping")
def ping():
    return {"message": "alive"}

@app.get("/echo")
def echo(value: str):
    return {"you_sent": value}


@app.get("/capture")
def capture(portal_id: int, faction: str):
    cursor.execute(
        "UPDATE portals SET faction = ? WHERE id = ?",
        (faction, portal_id)
    )
    conn.commit()

    return {"portal_id": portal_id, "controlled_by": faction}


@app.get("/add_portal")
def add_portal(portal_id: int, lat: float, lon: float):
    cursor.execute("""
        INSERT OR REPLACE INTO portals (id, lat, lon, faction)
        VALUES (?, ?, ?, NULL)
    """, (portal_id, lat, lon))

    conn.commit()

    return {
        "portal_id": portal_id,
        "lat": lat,
        "lon": lon,
        "message": "portal created"
    }
    
@app.get("/state")
def state():
    cursor.execute("SELECT id, lat, lon, faction FROM portals")
    rows = cursor.fetchall()

    return {
        "portals": [
            {
                "portal_id": r[0],
                "lat": r[1],
                "lon": r[2],
                "controlled_by": r[3]
            }
            for r in rows
        ]
    }
