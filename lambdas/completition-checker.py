import boto3
import json
import time
import requests

def lambda_handler(event, context):
    
    s3_client = boto3.client('s3')
    bucket_name = 'cloud-project-csci-5409'
    file_key = 'mp3s/expected_files.json'
    
    local_file_path = '/tmp/expected_files.json'
    s3_client.download_file(bucket_name, file_key, local_file_path)

    with open(local_file_path, "r") as file:
        json_data = json.load(file)
    print(json_data)
    
    expected_files = list(json_data["files"])
    print(f"Expected files: {expected_files}")
    
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix = "srts/")
    file_names = [obj['Key'].replace("srts/", "") for obj in response.get('Contents', [])]
    print(f"Files in srts: {file_names}")
    API_URL = "http://192.18.130.154:8000/embed"
    payload = {
        "bucket": bucket_name,
        "key": "txts"
    }
    if all(expected_file in file_names for expected_file in expected_files):
        print("Here!")
        time.sleep(5)
        response = requests.post(API_URL, data = json.dumps(payload))

        return {
           'statusCode': 200,
           'body': 'Embedding process has started!'
        }
    
    else:
        return {
           'statusCode': 200,
           'body': 'Processing in progress! Please wait!'
        }
        

    
