import os

def lambda_handler(event, context):
    print("POST event:", event)
    return {
        "statusCode": 200,
        "body": "POST request successful."
    }
