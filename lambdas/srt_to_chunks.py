import boto3
import os
from preprocess.process_srt import process_srt_file

s3 = boto3.client("s3")


def lambda_handler(event, context):
    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = event["Records"][0]["s3"]["object"]["key"]

    out_bucket = ""
    out_dir = ""

    s3.download_file(bucket, key, "/tmp/" + key)

    # Convert srt to chunks of text files
    if not os.path.exists("/tmp/outputs"):
        os.mkdir(
            "/tmp/outputs",
        )
    process_srt_file(0, "/tmp/" + key, "/tmp/outputs")

    for file in os.listdir("/tmp/outputs"):
        s3.upload_file(
            "/tmp/outputs/" + file,
            out_bucket,
            out_dir + "/" + file,
        )

    os.remove("/tmp/" + key)
    os.remove("/tmp/outputs")

    return {"statusCode": 200, "body": "SRT to chunks completed successfully."}
