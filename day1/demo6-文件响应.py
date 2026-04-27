from fastapi import FastAPI
from fastapi.responses import FileResponse
app = FastAPI()
@app.get("/file")
async def get_file():
    path = "./1.jpeg"
    return FileResponse(path)