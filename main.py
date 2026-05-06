
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import sqlite3
import math

conn = sqlite3.connect("game.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS portals (
    id INTEGER PRIMARY KEY,
    lat REAL,
    lon REAL,
    faction TEXT
)
""")
conn.commit()
app = FastAPI()
def distance(lat1, lon1, lat2, lon2):
    # simple Euclidean approximation (good enough for small distances)
    #
    return math.sqrt((lat1 - lat2)**2 + (lon1 - lon2)**2)

@app.get("/capture")
def capture(portal_id: int, lat: float, lon: float, faction: str):
    # get portal location
    cursor.execute("SELECT lat, lon FROM portals WHERE id = ?", (portal_id,))
    row = cursor.fetchone()

    if row is None:
        return {"status": "portal not found"}

    portal_lat, portal_lon = row

    dist = distance(lat, lon, portal_lat, portal_lon)

    # threshold ~0.001 ≈ ~300 feet (rough estimate)
    if dist > 0.001:
        return {"status": "too far from portal", "distance": dist}

    # allow capture
    cursor.execute(
        "UPDATE portals SET faction = ? WHERE id = ?",
        (faction, portal_id)
    )
    conn.commit()

    return {
        "status": "captured",
        "portal_id": portal_id
    }

@app.get("/migrate")
def migrate():
    portals = [
        (1, 41.4089, -75.6624, "red"),
        (2, 41.4235, -75.6132, "blue"),
        (3, 41.3890, -75.6885, None),
        (4, 41.4370, -75.6500, "red"),
        (5, 41.4015, -75.6200, "blue"),
    ]

    for p in portals:
        cursor.execute("""
            INSERT OR REPLACE INTO portals (id, lat, lon, faction)
            VALUES (?, ?, ?, ?)
        """, p)

    conn.commit()
    return {"status": "seeded"}
    
@app.get("/ping")
def ping():
    return {"message": "alive"}

@app.get("/echo")
def echo(value: str):
    return {"you_sent": value}

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
                "id": r[0],
                "lat": r[1],
                "lon": r[2],
                "controlled_by": r[3]
            }
            for r in rows
        ]
    }

app.mount("/", StaticFiles(directory=".", html=True), name="static")
