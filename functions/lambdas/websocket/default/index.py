import boto3
import base64
import json

kinesis = boto3.client('kinesis')

def lambda_handler(event, context):
    try:
        print(event)
        connection_id = event['requestContext']['connectionId']
        body = json.loads(event.get('body', '{}'))
        audio_data = body.get('data')
        audio_base64 = base64.b64decode(audio_data)
        payload = {
            "session_id": connection_id,
            "audio": audio_data
        }
        print(audio_base64)

        print(f"Received audio data for connection ID: {connection_id}")
        kinesis.put_record(
            StreamName='AudioStream',
            Data=audio_base64,
            PartitionKey=connection_id
        )
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Audio data processed successfully"})
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Failed to process audio data", "details": str(e)})
        }
