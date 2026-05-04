from fastapi import FastAPI

app = FastAPI()

@app.get("/ping")
def ping():
    return {"message": "alive"}

@app.get("/echo")
def echo(value: str):
    return {"you_sent": value}
