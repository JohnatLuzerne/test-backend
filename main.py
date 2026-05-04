from fastapi import FastAPI
import sqlite3
import math

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

def distance(lat1, lon1, lat2, lon2):
    # simple Euclidean approximation (good enough for small distances)
    return math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2)

@app.get("/capture")
def capture(portal_id: int, lat: float, lon: float, faction: str):
    # get portal location
    cursor.execute("SELECT lat, lon FROM portals WHERE id = ?", (portal_id,))
    row = cursor.fetchone()

    if row is None:
        return {"error": "portal not found"}

    portal_lat, portal_lon = row

    dist = distance(lat, lon, portal_lat, portal_lon)

    # threshold ~0.001 ≈ ~300 feet (rough estimate)
    if dist > 0.001:
        return {"error": "too far from portal", "distance": dist}

    # allow capture
    cursor.execute(
        "UPDATE portals SET faction = ? WHERE id = ?",
        (faction, portal_id)
    )
    conn.commit()

    return {
        "portal_id": portal_id,
        "controlled_by": faction,
        "distance": dist
    }
@app.get("/migrate")
def migrate():
    try:
        cursor.execute("ALTER TABLE portals ADD COLUMN lat REAL")
    except Exception as e:
        print("lat column:", e)

    try:
        cursor.execute("ALTER TABLE portals ADD COLUMN lon REAL")
    except Exception as e:
        print("lon column:", e)

    conn.commit()
    return {"status": "migration attempted"}

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
