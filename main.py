from fastapi import FastAPI, UploadFile, Request, Header
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import bcrypt
import os
import zipfile
import shutil
import io

from visualizer import imageGenerator, Weights

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

HASH = b'$2y$10$CA0SbcKrSW/vMu.9JN0W0uP5MJpVyz1vD6YbeScJmNhAuQAmjTBQG'
HOSTNAMES = {"ryulrudaga.com", "fs.hyunfit.life", "localhost", '127.0.0.1'}
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif'}


def create_directory(path: str):
    os.makedirs(path, exist_ok=True)


def delete_directory(path: str):
    shutil.rmtree(path)


def get_filename(file: UploadFile):
    return os.path.splitext(file.filename)[0]


def invalid_token(token: str | bytes):
    if type(token) == str:
        token = token.encode("UTF-8")
    return (token is None or not bcrypt.checkpw(token, HASH))


def unzip_uploadfile_to(file: UploadFile, destination: str):
    """unzip zip file

    Args:
        zip (UploadFile): UploadFile object that is zip file type.
        destination (str): destination directory. 
    """

    try:
        with zipfile.ZipFile(file.file, 'r') as zf:
            for info in zf.infolist():
                info.filename = info.filename.encode('cp437').decode('euc-kr')
                zf.extract(info, destination)
    except Exception as e:
        print(e)


@app.middleware("http")
async def security_middleware(request: Request, call_next):
    if (request.base_url.hostname not in HOSTNAMES):
        return JSONResponse(content="Forbidden", status_code=403)
    try:
        return await call_next(request)
    except Exception as e:
        return JSONResponse({"result": "failed",
                             "message": f"Server Error: {e}"
                             }, status_code=500)


@app.post("/api/{team}/file")
async def upload_file(
        team: str,
        file: UploadFile,
        token: str = Header(None)):

    if (invalid_token(token)):
        return JSONResponse(content="Unauthorized", status_code=401)

    file_path = f"files/{team}/{file.filename}"
    if os.path.isfile(file_path):
        return JSONResponse(content={
            "result": "failed",
            "message": "같은 이름의 파일이 이미 있습니다."
        }, status_code=406)

    create_directory(f"files/{team}")

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    return JSONResponse({"result": "successful",
                         "message": "파일을 성공적으로 업로드하였습니다.",
                         "filename": file.filename
                         }, status_code=200)


@app.post("/api/{team}/model", tags=["teachable model"])
async def upload_teachable_model(
        team: str,
        file: UploadFile,
        modelname: Optional[str] = None,
        token: str = Header(None)):
    """
    모델 업로드 API. zip 파일 확장자만 가능

    Parameters:
    - team (str): 팀스페이스명
    - modelname (Optional[str]): AI 모델명. 기본값은 파일명
    - file (UploadFile): 업로드할 모델 파일
    - token (str, optional): API 토큰.
    """
    if (invalid_token(token)):
        return JSONResponse(content="Unauthorized", status_code=401)
    if not file:
        return JSONResponse(content={
            "result": "failed",
            "message": "file이 없습니다."
        }, status_code=406)

    if file.content_type not in ["application/x-zip-compressed", "application/zip"]:
        return JSONResponse(content={
            "result": "failed",
            "message": ".zip 형식의 파일만 업로드 할 수 있습니다.",
            "filename": file.filename,
            "filetype": file.content_type
        }, status_code=406)

    if modelname is None:
        modelname = get_filename(file)
    directory = f"files/{team}/{modelname}"

    if os.path.isdir(directory):
        return JSONResponse(content={
            "result": "failed",
            "message": "같은 이름의 폴더가 이미 있습니다.",
            "filename": f"{directory}"
        }, status_code=406)

    create_directory(directory)

    unzip_uploadfile_to(file, directory)

    return JSONResponse({"result": "successful",
                         "message": "파일을 성공적으로 업로드하였습니다.",
                         "filename": file.filename
                         }, status_code=200)


@app.get("/api/{team}/model/{modelname}/{filename}", response_class=FileResponse, tags=["teachable model"])
async def download_model(team: str, modelname: str, filename: str):
    file_path = f"files/{team}/{modelname}/{filename}"
    if not os.path.isfile(file_path):
        return JSONResponse({"result": "failed",
                             "message": "파일이 존재하지 않습니다.",
                             "filename": file_path
                             }, status_code=404)
    return FileResponse(file_path, status_code=200)


@app.get("/api/{team}/file/{filename}", response_class=FileResponse)
async def download_file(team: str, filename: str):
    file_path = f"files/{team}/{filename}"
    if not os.path.isfile(file_path):
        return JSONResponse({"result": "failed",
                             "message": "파일이 존재하지 않습니다."
                             }, status_code=404)

    file_extension = os.path.splitext(file_path)[1]

    if file_extension and file_extension in IMAGE_EXTENSIONS:
        media_type = f"image/{file_extension[1:]}"
        return FileResponse(file_path, media_type=media_type, status_code=200)
    else:
        return FileResponse(file_path, status_code=200)


@app.delete("/api/{team}/model/{modelname}", tags=["teachable model"])
async def delete_teachable_model(team: str, modelname: str, token: str = Header(None)):
    if (invalid_token(token)):
        return JSONResponse(content="Unauthorized", status_code=401)

    path = f"files/{team}/{modelname}"

    if not os.path.exists(path):
        return JSONResponse({"result": "failed",
                             "message": "폴더가 존재하지 않습니다.",
                             "filename": f"{path}"
                             }, status_code=404)

    delete_directory(path)

    return JSONResponse({"result": "successful",
                         "message": "폴더가 성공적으로 삭제되었습니다.",
                         "filename": f"{path}"
                         }, status_code=200)


@app.delete("/api/{team}")
async def delete_teamspace(team: str, token: str = Header(None)):
    if (invalid_token(token)):
        return JSONResponse(content="Unauthorized", status_code=401)

    path = f"files/{team}"

    if not os.path.exists(path):
        return JSONResponse({"result": "failed",
                             "message": "폴더가 존재하지 않습니다.",
                             "filename": f"{path}"
                             }, status_code=404)

    delete_directory(path)

    return JSONResponse({"result": "successful",
                         "message": "팀스페이스가 성공적으로 삭제되었습니다.",
                         "filename": f"{path}"
                         }, status_code=200)


@app.post("/api/report/image", response_class=StreamingResponse, tags=["visualizer"])
async def generate_image(weights: Weights):
    image = imageGenerator.generate(weights)
    image_bytes = io.BytesIO()
    image.save(image_bytes, format="PNG")
    image_bytes.seek(0)
    return StreamingResponse(image_bytes, media_type="image/png")
