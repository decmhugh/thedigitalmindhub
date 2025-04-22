import os
def lambda_handler(event, context):
    print("GET event:", event)
    return {
        "statusCode": 200,
        "body": "GET request successful."
    }
