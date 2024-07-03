import uvicorn
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def health_check():
    return {"status_code": 200, "detail": "ok", "result": "working"}


if __name__ == "__main__":
    # uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
    uvicorn.run(app, host="127.0.0.1", port=8000)
