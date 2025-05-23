import os

def lambda_handler(event, context):
    token = event['headers'].get('Authorization', '')
    if token != "valid-token":
        return {
            "principalId": "user",
            "policyDocument": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Action": "execute-api:Invoke",
                        "Effect": "Allow",
                        "Resource": event["methodArn"]
                    }
                ]
            }
        }
    else:
        raise Exception("Unauthorized")