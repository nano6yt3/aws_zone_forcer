import boto3

def delete_all_route53_zones():
    # Create a Route 53 client
    client = boto3.client('route53')

    # List all hosted zones
    response = client.list_hosted_zones()

    # Extract the hosted zones
    hosted_zones = response['HostedZones']

    # Iterate over the hosted zones and delete them
    for zone in hosted_zones:
        zone_id = zone['Id']
        zone_name = zone['Name']

        # Delete the hosted zone
        client.delete_hosted_zone(Id=zone_id)

        print(f"Deleted zone: {zone_name}")

# Call the function to delete all DNS zones
delete_all_route53_zones()
