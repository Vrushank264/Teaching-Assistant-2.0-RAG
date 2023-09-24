import boto3

def lambda_handler(event, context):
   
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    transcribe_client = boto3.client('transcribe')
    name = key.split("/")[-1].split(".")[0]
    job_name = name
    job_uri = f's3://{bucket}/{key}'
    print(job_uri, job_name)
    
    transcribe_client.start_transcription_job(
        TranscriptionJobName=job_name,
        Media = {'MediaFileUri': job_uri},
        MediaFormat = 'mp3',
        LanguageCode ='en-US',  
        OutputBucketName = bucket,
        OutputKey = "srts/",
        Subtitles={'Formats': [ 'srt']}
    )
    
    return {
        'statusCode': 200,
        'body': 'Transcription job started successfully!!'
    }

