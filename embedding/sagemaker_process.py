import json
import embed
import boto3
import os
from enum import Enum
from fastapi import FastAPI, APIRouter
from pydantic import BaseModel
from configs import ACCESS_KEY_ID, SECRET_ACCESS_KEY


class ConvertRequestBody(BaseModel):
    """Convert Request Body"""

    bucket: str
    key: str


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



class Progress:
    def __init__(self) -> None:
        self.progress = {}

    def update_progress(self, progress_id: str, status: Status):
        self.progress[progress_id] = status

    def get_progress(self, progress_id: str) -> Status:
        return self.progress.get(progress_id, "Invalid progress id")


router = APIRouter()
progress = Progress()
s3 = boto3.client(
    "s3",
    region_name="us-east-1",
    aws_access_key_id=ACCESS_KEY_ID,
    aws_secret_access_key=SECRET_ACCESS_KEY,
)


class Conversion:
    """Progress class to track progress of conversion"""

    def __init__(self, progress_id) -> None:
        self.progress_id = progress_id

    def download(self, bucket: str, key: str):
        os.makedirs("/tmp/txts", exist_ok=True)
        name = key.split("/")[-1].split(".")[0]
        files_to_process = []
        response = s3.list_objects_v2(Bucket=bucket)

        # Loop through the objects and download each file
        for obj in response.get('Contents', []):
            key = obj['Key']
            local_file_path = os.path.join("/tmp/txts", key)
            files_to_process.append(local_file_path)
            s3.download_file(bucket, key, local_file_path)
        
        print("Downloaded")

        return files_to_process

    def _embed(self):
        os.makedirs("/tmp/db", exist_ok=True)
        db = embed.get_embedding("/tmp/txts", 500, 200, "/tmp/db")
        db.persist()
        print("Embedded!")

        return db

    def upload(self, bucket: str, key: str):
        
        for root, dirs, files in os.walk("/tmp/db"):
            for file in files:
                local_file_path = os.path.join(root, file)
                s3_key = os.path.join(key, os.path.relpath(local_file_path, "/tmp/db"))
                s3.upload_file(local_file_path, bucket, s3_key)

        return True
    


def perform_task(bucket: str, key: str, progress_id: str):
    """Performs task"""

    conversion = Conversion(progress_id)

    progress.update_progress(progress_id, Status.DOWNLOADING)
    try:
        files_to_process = conversion.download(bucket, key)
    except ClientError:
        progress.update_progress(progress_id, Status.DOWNLOAD_ERROR)
        return False

    progress.update_progress(progress_id, Status.DOWNLOADED)

    progress.update_progress(progress_id, Status.CONVERTING)
    try:
        db = conversion._embed()
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
