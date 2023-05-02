import uuid

from fastapi import APIRouter, File, UploadFile
from typing_extensions import Annotated
import os

router = APIRouter()

@router.post("/files/")
async def create_note(file: Annotated[bytes, File()]):
    return {"file_size": len(file)}

@router.post("/note/set")
async def set_note(file: UploadFile):
    UPLOAD_DIR = "./notes"
    content = await file.read()
    filename = f"{str(uuid.uuid4())}.md"
    with open(os.path.join(UPLOAD_DIR, filename), "wb") as fn:
        fn.write(content)

    return {"filename": file.filename}

# @router.get("/note/get/{note_id}")
# async def get_note(note_id: int, db: Session = Depends(get_db))