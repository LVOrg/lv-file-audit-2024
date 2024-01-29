import sys

sys.path.append("/app")
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World from FastAPI!"}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("cy_hello_world.server:app", host="0.0.0.0", port=8000)