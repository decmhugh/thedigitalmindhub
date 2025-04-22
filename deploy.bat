@echo off
echo Deploying the Serverless API Stack...
sam deploy -t serverless-api-stack.yaml --stack-name dmh-serverless-voice-stack --region eu-west-1 --capabilities CAPABILITY_NAMED_IAM
if %ERRORLEVEL% NEQ 0 (
    echo Deployment failed.
    exit /b %ERRORLEVEL%
)
echo Deployment succeeded.
pause
