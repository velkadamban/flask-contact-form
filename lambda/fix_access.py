import boto3
import requests

def get_my_ip():
    """Get your current public IP"""
    try:
        response = requests.get('https://ipinfo.io/ip', timeout=5)
        return response.text.strip()
    except:
        return None

def restore_access():
    """Replace dummy IPs with your actual IP for access"""
    ec2 = boto3.client('ec2')
    my_ip = get_my_ip()
    
    if not my_ip:
        print("Could not get your public IP. Please check internet connection.")
        return
    
    print(f"Your public IP: {my_ip}")
    my_cidr = f"{my_ip}/32"
    
    # Get security groups with dummy IPs
    response = ec2.describe_security_groups()
    
    for sg in response['SecurityGroups']:
        sg_id = sg['GroupId']
        sg_name = sg['GroupName']
        
        # Skip EKS internal security groups
        if any(x in sg_name.lower() for x in ['eks', 'k8s-elb', 'guardduty']):
            continue
            
        rules_to_update = []
        
        for rule in sg['IpPermissions']:
            for ip_range in rule.get('IpRanges', []):
                if ip_range.get('CidrIp') == '192.0.2.1/32':
                    # Found dummy IP rule
                    rules_to_update.append({
                        'old_rule': rule,
                        'new_cidr': my_cidr,
                        'description': ip_range.get('Description', '')
                    })
        
        # Update rules
        for update in rules_to_update:
            old_rule = update['old_rule']
            
            try:
                # Remove dummy rule
                ec2.revoke_security_group_ingress(
                    GroupId=sg_id,
                    IpPermissions=[old_rule]
                )
                
                # Add rule with your IP
                new_rule = old_rule.copy()
                new_rule['IpRanges'] = [{
                    'CidrIp': my_cidr,
                    'Description': f'Your IP access - was dummy IP'
                }]
                
                ec2.authorize_security_group_ingress(
                    GroupId=sg_id,
                    IpPermissions=[new_rule]
                )
                
                port_info = f"Port {old_rule.get('FromPort', 'All')}"
                print(f"Updated {sg_name}: {port_info} now allows {my_cidr}")
                
            except Exception as e:
                print(f"Error updating {sg_name}: {e}")

if __name__ == '__main__':
    print("=== RESTORING ACCESS TO YOUR EC2 INSTANCES ===")
    restore_access()
    print("\nAccess restored! You can now connect to your EC2 instances.")