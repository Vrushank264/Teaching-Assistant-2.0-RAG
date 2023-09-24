from fastapi import APIRouter, WebSocket, WebSocketDisconnect, FastAPI
import os
import boto3
from glob import glob
import time

from infer import create_chain, load_llm, process_llm_response
from configs import ACCESS_KEY_ID, SECRET_ACCESS_KEY

router = FastAPI()

s3_client = boto3.client('s3', 
                        region_name="us-east-1",
                        aws_access_key_id=ACCESS_KEY_ID,
                        aws_secret_access_key=SECRET_ACCESS_KEY)

bucket_name = 'cloud-project-csci-5409'
folder_key = 'embedding-db'
local_dir = 'db_dir/'

if not os.path.exists(local_dir):
    os.makedirs(local_dir, exist_ok = True)


LLM_MODEL_NAME = "TheBloke/wizardLM-7B-HF"
DB_DIR = "db_dir/"

while len(glob(f"{DB_DIR}/*")) == 0:
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=folder_key)

    if 'Contents' in response:
        print("Found Embedding db, starting inference...")

        for obj in response['Contents']:
        
            object_key = obj['Key']
            file_name = os.path.basename(object_key)
            local_file_path = os.path.join(local_dir, file_name)
            s3_client.download_file(bucket_name, object_key, local_file_path)

    time.sleep(5) 

llm = load_llm(LLM_MODEL_NAME)
print("Creating QA Chain")
qa_chain = create_chain(DB_DIR, llm)
print("QA Chain Created!")
print("Start Chatting now!")

@router.websocket("/chat")
async def chat(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            message = await websocket.receive_text()

            llm_response = qa_chain(message)
            json_response = process_llm_response(llm_response)

            await websocket.send_json(json_response)
    except WebSocketDisconnect:
        await websocket.close()
    except Exception as err:
        websocket.send_text(str(err))
        await websocket.close()
