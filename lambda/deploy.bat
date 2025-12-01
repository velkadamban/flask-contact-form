@echo off
echo Installing required dependencies...
py -m pip install boto3

echo.
echo Deploying Security Group Monitor Lambda...
py deploy.py

echo.
echo Deployment completed!
pause