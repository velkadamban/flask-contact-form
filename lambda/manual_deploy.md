# Manual Lambda Deployment Steps

## Prerequisites
1. Configure AWS CLI:
```cmd
aws configure
```
Enter your:
- AWS Access Key ID
- AWS Secret Access Key  
- Default region (e.g., us-east-1)
- Output format: json

## Step 1: Create IAM Role
```cmd
aws iam create-role --role-name SecurityGroupMonitorRole --assume-role-policy-document file://trust-policy.json
aws iam put-role-policy --role-name SecurityGroupMonitorRole --policy-name SecurityGroupMonitorPolicy --policy-document file://lambda_policy.json
```

## Step 2: Create Lambda Package
```cmd
py -c "import zipfile; z=zipfile.ZipFile('function.zip','w'); z.write('security_group_monitor.py'); z.close()"
```

## Step 3: Deploy Lambda Function
```cmd
aws lambda create-function --function-name SecurityGroupMonitor --runtime python3.9 --role arn:aws:iam::YOUR_ACCOUNT_ID:role/SecurityGroupMonitorRole --handler security_group_monitor.lambda_handler --zip-file fileb://function.zip
```

## Step 4: Create EventBridge Rule
```cmd
aws events put-rule --name SecurityGroupMonitorDaily --schedule-expression "rate(1 day)"
aws events put-targets --rule SecurityGroupMonitorDaily --targets "Id"="1","Arn"="arn:aws:lambda:YOUR_REGION:YOUR_ACCOUNT_ID:function:SecurityGroupMonitor"
aws lambda add-permission --function-name SecurityGroupMonitor --statement-id AllowEventBridge --action lambda:InvokeFunction --principal events.amazonaws.com
```

## Test Lambda
```cmd
aws lambda invoke --function-name SecurityGroupMonitor output.json
```