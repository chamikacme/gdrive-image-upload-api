from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from functions import upload, clear

app = FastAPI()

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return JSONResponse(content={"message": "Hello, World!"})

@app.post("/upload")
async def upload_base64(data: dict):
    try:
        upload(data.get('data'), data.get('filename'))
    except Exception as error:
        return JSONResponse(content={"message": f"An error occurred: {error}"}, status_code=500)
    return JSONResponse(content={"message": "File uploaded successfully."})

@app.post("/clear")
async def clear_data():
    try:
        clear()
    except Exception as error:
        return JSONResponse(content={"message": f"An error occurred: {error}"}, status_code=500)
    return JSONResponse(content={"message": "Folder and sheet cleared successfully."})