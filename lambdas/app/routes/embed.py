import os
from enum import Enum
from random import randint

import boto3
from botocore.exceptions import ClientError
from fastapi import APIRouter, BackgroundTasks, FastAPI
from pydantic import BaseModel

import sys
sys.path.append("../")
from embedding.embed import get_embedding

INPUT_DIR = "/ip/txts"
OUT_DIR = "/op/db"

class EmbeddingRequest(BaseModel):
    bucket: str
    key: str
    # chunk_size: int
    # chunk_overlap: int


class Status(Enum):
    """The above class defines an enumeration for different status values."""

    DOWNLOADING = "downloading"
    DOWNLOADED = "downloaded"
    INITIATED = "Embedding generation initiated"
    CONVERTING = "Generating Embeddings"
    CONVERTED = "Generated Embeddings"
    UPLOADING = "uploading"
    UPLOADED = "uploaded"
    DOWNLOAD_ERROR = "download error"
    CONVERT_ERROR = "Embedding error"
    UPLOAD_ERROR = "upload error"
    ERROR = "error"


class Embedding:
    """Progress class to track progress of conversion"""

    def download(self, bucket: str, key: str):
        os.makedirs(INPUT_DIR, exist_ok=True)
        name = key.split("/")[-1].split(".")[0]
        files_to_process = []
        response = s3.list_objects_v2(Bucket=bucket,Key = key)

        # Loop through the objects and download each file
        for obj in response.get("Contents", []):
            key_ = obj["Key"]
            local_file_path = os.path.join(INPUT_DIR, key_)
            files_to_process.append(local_file_path)
            s3.download_file(bucket, key_, local_file_path)

        print("Downloaded")

        return files_to_process

    def embed(self):
        os.makedirs(OUT_DIR, exist_ok=True)
        vector_db = get_embedding(INPUT_DIR, 500, 200, OUT_DIR)
        vector_db.persist()
        print("Embedded!")

        return vector_db

    def upload(self, bucket: str, key: str):
        for root, _, files in os.walk(OUT_DIR):
            for file in files:
                local_file_path = os.path.join(root, file)
                s3_key = os.path.join(
                    key, os.path.relpath(local_file_path, OUT_DIR)
                )
                s3.upload_file(local_file_path, bucket, s3_key)

        return True


class Progress:
    def __init__(self) -> None:
        self.progress = {}

    def update_progress(self, progress_id: str, status: Status):
        self.progress[progress_id] = status

    def get_progress(self, progress_id: str) -> Status:
        return self.progress.get(progress_id, "Invalid progress id")


router = FastAPI()
s3 = boto3.client("s3")
progress = Progress()


def perform_task(bucket: str, key: str, progress_id: str):
    """Performs task"""

    conversion = Embedding()

    progress.update_progress(progress_id, Status.DOWNLOADING)
    try:
        files_to_process = conversion.download(bucket, key)
    except ClientError:
        progress.update_progress(progress_id, Status.DOWNLOAD_ERROR)
        return False

    progress.update_progress(progress_id, Status.DOWNLOADED)

    progress.update_progress(progress_id, Status.CONVERTING)
    try:
        db = conversion.embed()
    except Exception:
        progress.update_progress(progress_id, Status.CONVERT_ERROR)
        return False

    progress.update_progress(progress_id, Status.CONVERTED)

    progress.update_progress(progress_id, Status.UPLOADING)
    try:
        conversion.upload(bucket, "embedding-db")
    except Exception:
        progress.update_progress(progress_id, Status.UPLOAD_ERROR)
        return False

    progress.update_progress(progress_id, Status.UPLOADED)

    return True


@router.post("/embed")
def embed(body: EmbeddingRequest, background_tasks: BackgroundTasks):
    """embed api"""

    progress_id = randint(-100000, 1000000)

    background_tasks.add_task(
        perform_task,
        progress_id,
        body.bucket,
        body.key,
        # body.chunk_size,
        # body.chunk_overlap,
    )


@router.get("/progress/{progress_id}")
def get_progress(progress_id: str):
    """get progress"""

    status = progress.get_progress(progress_id)

    return {"progress_id": progress_id, "progress": status.value}
