import boto3
import json
from configs import TOPIC_ARN

def lambda_handler(event, context):
 
    sns_client = boto3.client('sns')
    
    topic_arn = TOPIC_ARN

    try:
        notification = "Your data has been processed! You can chat now!"
        response = sns_client.publish(TopicArn=topic_arn, Message = json.dumps({'default': notification}),  MessageStructure = 'json')
        
    except Exception as e:
        print(f"Error sending SNS message: {e}")

    return {
        'statusCode': 200,
        'body': f'SNS message sent successfully.'
    }
