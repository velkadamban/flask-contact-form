import boto3
import json
import zipfile
import os
from datetime import datetime

def create_lambda_package():
    """Create deployment package for Lambda function"""
    with zipfile.ZipFile('security_monitor.zip', 'w') as zip_file:
        zip_file.write('security_group_monitor.py')
    print("Lambda package created")

def create_iam_role():
    """Create IAM role for Lambda function"""
    iam = boto3.client('iam')
    
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "lambda.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }
        ]
    }
    
    try:
        role_response = iam.create_role(
            RoleName='SecurityGroupMonitorRole',
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description='Role for Security Group Monitor Lambda'
        )
        
        # Attach policies
        with open('lambda_policy.json', 'r') as f:
            policy_doc = f.read()
        
        iam.put_role_policy(
            RoleName='SecurityGroupMonitorRole',
            PolicyName='SecurityGroupMonitorPolicy',
            PolicyDocument=policy_doc
        )
        
        print("IAM role created")
        return role_response['Role']['Arn']
        
    except iam.exceptions.EntityAlreadyExistsException:
        role = iam.get_role(RoleName='SecurityGroupMonitorRole')
        print("IAM role already exists")
        return role['Role']['Arn']

def deploy_lambda_function(role_arn):
    """Deploy Lambda function"""
    lambda_client = boto3.client('lambda')
    
    with open('security_monitor.zip', 'rb') as zip_file:
        zip_content = zip_file.read()
    
    try:
        response = lambda_client.create_function(
            FunctionName='SecurityGroupMonitor',
            Runtime='python3.9',
            Role=role_arn,
            Handler='security_group_monitor.lambda_handler',
            Code={'ZipFile': zip_content},
            Description='Monitors and secures EC2 security groups',
            Timeout=60
        )
        print("Lambda function created")
        return response['FunctionArn']
        
    except lambda_client.exceptions.ResourceConflictException:
        lambda_client.update_function_code(
            FunctionName='SecurityGroupMonitor',
            ZipFile=zip_content
        )
        response = lambda_client.get_function(FunctionName='SecurityGroupMonitor')
        print("Lambda function updated")
        return response['Configuration']['FunctionArn']

def create_eventbridge_rule(lambda_arn):
    """Create EventBridge rule for daily execution"""
    events = boto3.client('events')
    lambda_client = boto3.client('lambda')
    
    # Create rule
    rule_response = events.put_rule(
        Name='SecurityGroupMonitorDaily',
        ScheduleExpression='rate(1 day)',
        Description='Daily security group monitoring',
        State='ENABLED'
    )
    
    # Add Lambda target
    events.put_targets(
        Rule='SecurityGroupMonitorDaily',
        Targets=[
            {
                'Id': '1',
                'Arn': lambda_arn
            }
        ]
    )
    
    # Add permission for EventBridge to invoke Lambda
    try:
        lambda_client.add_permission(
            FunctionName='SecurityGroupMonitor',
            StatementId='AllowEventBridge',
            Action='lambda:InvokeFunction',
            Principal='events.amazonaws.com',
            SourceArn=rule_response['RuleArn']
        )
    except lambda_client.exceptions.ResourceConflictException:
        pass  # Permission already exists
    
    print("EventBridge rule created for daily execution")

def main():
    print("Deploying Security Group Monitor...")
    
    # Change to lambda directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Deploy components
    create_lambda_package()
    role_arn = create_iam_role()
    
    # Wait a moment for role propagation
    import time
    time.sleep(10)
    
    lambda_arn = deploy_lambda_function(role_arn)
    create_eventbridge_rule(lambda_arn)
    
    # Cleanup
    if os.path.exists('security_monitor.zip'):
        os.remove('security_monitor.zip')
    
    print("Deployment completed successfully!")
    print(f"Lambda function will run daily to monitor security groups")

if __name__ == '__main__':
    main()