from fastapi import APIRouter, WebSocket, WebSocketDisconnect, FastAPI
import os
import boto3
import time

from inference_code.infer import create_chain, load_llm, process_llm_response

router = APIRouter()

s3_client = boto3.client('s3')

bucket_name = 'cloud-project-csci-5409'
folder_key = 'embedding-db/'
local_dir = 'db_dir/'

if not os.path.exists(local_dir):
    os.makedirs(local_dir, exist_ok = True)

response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=folder_key)

if 'Contents' in response:

    for obj in response['Contents']:
      
        object_key = obj['Key']
        file_name = os.path.basename(object_key)
        local_file_path = os.path.join(local_dir, file_name)
        s3_client.download_file(bucket_name, object_key, local_file_path)

else:
    time.sleep(10)


LLM_MODEL_NAME = "TheBloke/wizardLM-7B-HF"
DB_DIR = "db_dir/"

llm = load_llm(LLM_MODEL_NAME)
qa_chain = create_chain(DB_DIR, llm)

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
