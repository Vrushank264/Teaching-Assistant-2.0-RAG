import json
import boto3

def lambda_handler(event, context):
    
    sns = boto3.client('sns')
    print(event)
    
    email_body = event['email']
    print(email_body)
    
    response1 = sns.subscribe(
        TopicArn='arn:aws:sns:us-east-1:357054887258:processing-complete',
        Protocol='email',
        Endpoint=email_body,
        
        ReturnSubscriptionArn=True
    )
    response =  {
        'statusCode': 200,
        'body': json.dumps('Email sent successfully!')
    }
    
    response["headers"] = {
        "Access-Control-Allow-Origin": "*",  
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "OPTIONS,POST,GET"  
    }
    
    return response;
