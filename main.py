
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
    faction TEXT,
    owner TEXT,
    portal_name TEXT
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS players (
    id INTEGER PRIMARY KEY,
    name TEXT,
    player_faction TEXT,
    energy INTEGER,
    experience INTEGER
)
""")
conn.commit()

app = FastAPI()
from fastapi.responses import FileResponse

@app.get("/")
def root():
    return FileResponse("index.html")

app.mount("/static", StaticFiles(directory=".", html=True), name="static")

def distance(lat1, lon1, lat2, lon2):
    # simple Euclidean approximation (good enough for small distances)
    #
    return ((lat1 - lat2)**2 + (lon1 - lon2)**2)

@app.get("/player")
def get_player():
    cursor.execute("SELECT name, faction, energy, experience FROM players WHERE id = 1")
    row = cursor.fetchone()

    return {
        "name": row[0],
        "faction": row[1],
        "energy": row[2],
        "experience": row[3]
    }
    
@app.get("/capture")
def capture(portal_id: int, lat: float, lon: float, faction: str, owner: str):
    # get portal location
    cursor.execute("SELECT lat, lon FROM portals WHERE id = ?", (portal_id,))
    row = cursor.fetchone()

    if row is None:
        return {"status": "portal not found"}

    portal_lat, portal_lon = row

    dist = distance(lat, lon, portal_lat, portal_lon)

    # threshold ~0.001 ≈ ~300 feet (rough estimate)
    if dist > 0.0005:
        return {"status": "too far from portal", "distance": dist}

    # allow capture
    cursor.execute(
        "UPDATE portals SET faction = ?, owner = ? WHERE id = ?",
        (faction, owner, portal_id)
    )

    # update player info
    cursor.execute("""
    UPDATE players
    SET
        energy = energy - 10,
        experience = experience + 5
    WHERE id = 1
    """)    
    conn.commit()

    return {
        "status": "captured",
        "portal_id": portal_id
    }

@app.get("/migrate")
def migrate():
    portals = [
    (1, 41.4086, -75.6621, "Knights", None, "Lackawanna County Courthouse"),
    (2, 41.4056, -75.6625, "Skylords", None, "Steamtown National Historic Site"),
    (3, 41.4092, -75.6649, "Elves", None, "Scranton Cultural Center"),
    (4, 41.4045, -75.6690, "Knights", None, "University of Scranton"),
    (5, 41.4023, -75.6245, "Skylords", None, "Nay Aug Park"),
    (6, 41.3255, -75.7893, "Skylords", None, "Pittston Memorial Library"),
    (7, 41.3270, -75.7898, "Knights", None, "Greater Pittston YMCA"),
    (8, 41.3260, -75.7890, "Elves", None, "Pittston City Hall"),

    (9, 41.3342, -75.7370, "Skylords", None, "Dupont Borough Building"),
    (10, 41.3350, -75.7355, "Knights", None, "Sacred Heart of Jesus Church"),

    (11, 41.3395, -75.7280, "Elves", None, "Avoca Municipal Building"),
    (12, 41.3388, -75.7305, "Skylords", None, "St. Mary’s Church Avoca")
    ]   

    players = [
        (1, "John", "Skylords", 50000, 0)
    ]

    for p in portals:
        cursor.execute("""
            INSERT OR REPLACE INTO portals (id, lat, lon, faction, owner, portal_name)
            VALUES (?, ?, ?, ?, ?, ?)
        """, p)

    for p in players:
        cursor.execute("""
            INSERT OR REPLACE INTO players (id, name, player_faction, energy, experience)
            VALUES (?, ?, ?, ?, ?)
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
        INSERT OR REPLACE INTO portals (id, lat, lon, faction, owner)
        VALUES (?, ?, ?, 'neutral', NULL)
    """, (portal_id, lat, lon))

    conn.commit()

    return {
        "portal_id": portal_id,
        "message": "portal created"
    }
    return {
        "portal_id": portal_id,
        "lat": lat,
        "lon": lon,
        "message": "portal created"
    }
    
@app.get("/state")
def state():
    cursor.execute("SELECT id, lat, lon, faction, owner, portal_name FROM portals")
    rows = cursor.fetchall()

    return {
        "portals": [
            {
                "id": r[0],
                "lat": r[1],
                "lon": r[2],
                "controlled_by": r[3],
                "portal_owner": r[4],
                "portal_name": r[5]
            }
            for r in rows
        ]
    }

