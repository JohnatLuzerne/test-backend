from fastapi import FastAPI

portals = {}
app = FastAPI()

@app.get("/ping")
def ping():
    return {"message": "alive"}

@app.get("/echo")
def echo(value: str):
    return {"you_sent": value}

@app.get("/capture")
def capture(portal_id: int, faction: str):
    portals[portal_id] = faction
    return {"portal_id": portal_id, "controlled_by": faction}
