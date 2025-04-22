# Serverless API Stack Deployment

This project contains a serverless API stack defined in `serverless-api-stack.yaml`. Follow the steps below to deploy the stack using AWS SAM CLI.

## Prerequisites

- AWS CLI installed and configured.
- AWS SAM CLI installed.
- Proper IAM permissions to deploy resources.

## Deployment

Run the following command to deploy the stack:

```bash
sam deploy -t serverless-api-stack.yaml --stack-name dmh-serverless-voice-stack --region eu-west-1 --capabilities CAPABILITY_NAMED_IAM --resolve-s3
```

## Parameters

- **`--stack-name`**: The name of the CloudFormation stack.
- **`--region`**: The AWS region where the stack will be deployed.
- **`--capabilities`**: Required to create IAM roles.
- **`--resolve-s3`**: Automatically manages S3 bucket for deployment artifacts.

## Notes

- Ensure the `serverless-api-stack.yaml` file is up-to-date before deploying.
- Check the AWS Management Console for the status of the stack after deployment.
