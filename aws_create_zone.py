import argparse
import boto3

def create_dns_zone(zone_name):
    client = boto3.client('route53')
    
    # Create a new hosted zone
    response = client.create_hosted_zone(
        Name=zone_name,
        CallerReference=str(hash(zone_name)),
        HostedZoneConfig={
            'Comment': 'Created by Boto3'
        }
    )
    
    # Extract the zone ID from the response
    zone_id = response['HostedZone']['Id']
    
    print(f"Created DNS zone '{zone_name}' with ID '{zone_id}'")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create a DNS zone in AWS Route 53 using Boto3')
    parser.add_argument('-d', '--domain', type=str, required=True, help='Domain name for the DNS zone')
    
    args = parser.parse_args()
    
    # Call the function with the provided domain name
    create_dns_zone(args.domain)
