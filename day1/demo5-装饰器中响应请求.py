from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/html", response_class=HTMLResponse)
async def html():
    return """
    <html>
        <head>
            <title>HTML Response</title>
        </head>
        <body>
            <h1>Hello, World!</h1>
        </body>
    </html>
    """