import boto3
import json

def check_security_groups():
    """Check current security groups for open rules"""
    ec2 = boto3.client('ec2')
    
    response = ec2.describe_security_groups()
    
    print("=== SECURITY GROUP ANALYSIS ===")
    open_groups = []
    
    for sg in response['SecurityGroups']:
        sg_id = sg['GroupId']
        sg_name = sg['GroupName']
        
        print(f"\nSecurity Group: {sg_name} ({sg_id})")
        
        # Check inbound rules
        for rule in sg['IpPermissions']:
            for ip_range in rule.get('IpRanges', []):
                cidr = ip_range.get('CidrIp', '')
                if cidr == '0.0.0.0/0':
                    port_info = f"Port {rule.get('FromPort', 'All')}"
                    if rule.get('ToPort') != rule.get('FromPort'):
                        port_info = f"Ports {rule.get('FromPort')}-{rule.get('ToPort')}"
                    
                    print(f"  WARNING OPEN TO WORLD: {port_info} Protocol: {rule.get('IpProtocol')}")
                    open_groups.append({
                        'GroupId': sg_id,
                        'GroupName': sg_name,
                        'Port': port_info,
                        'Protocol': rule.get('IpProtocol')
                    })
                else:
                    print(f"  OK Restricted: {cidr}")
    
    print(f"\n=== SUMMARY ===")
    print(f"Total Security Groups: {len(response['SecurityGroups'])}")
    print(f"Open to World: {len(open_groups)}")
    
    if open_groups:
        print("\nSECURITY RISK FOUND:")
        for group in open_groups:
            print(f"  - {group['GroupName']}: {group['Port']} {group['Protocol']}")
    else:
        print("\nAll security groups are properly secured!")

def check_lambda_logs():
    """Get latest Lambda execution logs"""
    logs = boto3.client('logs')
    
    try:
        # Get log streams
        streams = logs.describe_log_streams(
            logGroupName='/aws/lambda/SecurityGroupMonitor',
            orderBy='LastEventTime',
            descending=True,
            limit=1
        )
        
        if streams['logStreams']:
            stream_name = streams['logStreams'][0]['logStreamName']
            
            # Get log events
            events = logs.get_log_events(
                logGroupName='/aws/lambda/SecurityGroupMonitor',
                logStreamName=stream_name
            )
            
            print("\n=== LATEST LAMBDA EXECUTION ===")
            for event in events['events']:
                message = event['message'].strip()
                if not message.startswith(('START', 'END', 'REPORT')):
                    print(message)
        
    except Exception as e:
        print(f"Could not retrieve logs: {e}")

if __name__ == '__main__':
    check_security_groups()
    check_lambda_logs()