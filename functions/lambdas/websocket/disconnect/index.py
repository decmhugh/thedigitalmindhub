import json

def lambda_handler(event, context):
    # Log the disconnect event
    print(f"Disconnect event: {json.dumps(event)}")
    
    # Perform any cleanup or resource release logic here
    connection_id = event['requestContext']['connectionId']
    print(f"Disconnected connection ID: {connection_id}")
    
    return {
        "statusCode": 200,
        "body": "Disconnected successfully."
    }
