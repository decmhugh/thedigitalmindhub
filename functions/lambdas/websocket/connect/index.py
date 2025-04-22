import json

def lambda_handler(event, context):
    # Log the connect event
    print(f"Connect event: {json.dumps(event)}")
    
    # Perform any initialization or resource allocation logic here
    connection_id = event['requestContext']['connectionId']
    print(f"Connected connection ID: {connection_id}")
    
    return {
        "statusCode": 200,
        "body": "Connected successfully."
    }
