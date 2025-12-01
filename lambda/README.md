# Security Group Monitor Lambda

Automatically monitors and secures EC2 security groups by closing open-to-world (0.0.0.0/0) rules.

## Features
- Scans all security groups daily
- Replaces 0.0.0.0/0 rules with dummy IP (192.0.2.1/32)
- Scheduled execution via EventBridge
- Comprehensive logging

## Deployment

1. Configure AWS credentials:
```bash
aws configure
```

2. Deploy the Lambda function:
```bash
cd lambda
python deploy.py
```

## What it does
- Finds security groups with 0.0.0.0/0 inbound rules
- Revokes the open rules
- Adds replacement rules with dummy IP
- Logs all changes for audit

## Manual Testing
```bash
aws lambda invoke --function-name SecurityGroupMonitor output.json
```