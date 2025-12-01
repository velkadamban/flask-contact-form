import boto3
import json
from datetime import datetime

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')
    
    try:
        # Get all security groups
        response = ec2.describe_security_groups()
        
        modified_groups = []
        
        for sg in response['SecurityGroups']:
            sg_id = sg['GroupId']
            sg_name = sg['GroupName']
            
            # Skip default VPC security group to avoid issues
            if sg_name == 'default':
                continue
            
            rules_to_revoke = []
            rules_to_add = []
            
            # Check inbound rules
            for rule in sg['IpPermissions']:
                for ip_range in rule.get('IpRanges', []):
                    if ip_range.get('CidrIp') == '0.0.0.0/0':
                        # Found open-to-world rule
                        rules_to_revoke.append(rule)
                        
                        # Create replacement rule with dummy IP
                        new_rule = rule.copy()
                        new_rule['IpRanges'] = [{'CidrIp': '192.0.2.1/32', 'Description': 'Secured by Lambda - was 0.0.0.0/0'}]
                        rules_to_add.append(new_rule)
                        break
            
            # Apply changes if needed
            if rules_to_revoke:
                # Revoke open rules
                ec2.revoke_security_group_ingress(
                    GroupId=sg_id,
                    IpPermissions=rules_to_revoke
                )
                
                # Add secured rules
                ec2.authorize_security_group_ingress(
                    GroupId=sg_id,
                    IpPermissions=rules_to_add
                )
                
                modified_groups.append({
                    'SecurityGroupId': sg_id,
                    'SecurityGroupName': sg_name,
                    'RulesModified': len(rules_to_revoke)
                })
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Security group scan completed at {datetime.now().isoformat()}',
                'modifiedGroups': modified_groups,
                'totalModified': len(modified_groups)
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'message': 'Failed to process security groups'
            })
        }