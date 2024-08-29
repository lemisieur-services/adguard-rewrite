import json
import requests
import os
import sys
import warnings
from urllib3.exceptions import InsecureRequestWarning

# Suppress only the single InsecureRequestWarning from urllib3 needed for disabling SSL verification
warnings.simplefilter('ignore', InsecureRequestWarning)

def get_existing_dns_entries(session, instance_url):
    response = session.get(f"{instance_url}/control/rewrite/list", verify=False)
    if response.status_code in [401, 403]:
        print("Error: Authentication failed or access forbidden. Please check your AdGuard credentials, and permissions.")
        sys.exit(1)
    elif response.status_code != 200:
        print(f"Failed to fetch existing DNS entries from {instance_url}: {response.text}")
        sys.exit(1)
    return response.json()

def add_dns_entry(session, instance_url, domain, answer):
    payload = {"domain": domain, "answer": answer}
    response = session.post(f"{instance_url}/control/rewrite/add", json=payload, verify=False)
    if response.status_code != 200:
        print(f"Failed to add {domain} on {instance_url}: {response.text}")
    else:
        print(f"ADD - {domain} on {instance_url}")

def remove_dns_entry(session, instance_url, domain, answer):
    payload = {"answer": answer, "domain": domain}
    response = session.post(f"{instance_url}/control/rewrite/delete", json=payload, verify=False)
    if response.status_code != 200:
        print(f"Failed to remove {domain} on {instance_url}: {response.text}")
    else:
        print(f"REMOVE - {domain} on {instance_url}")

def update_dns(instance_url, username, password, dns_entries):
    session = requests.Session()
    session.auth = (username, password)
    
    existing_entries = get_existing_dns_entries(session, instance_url)
    existing_domains = {entry['domain']: entry['answer'] for entry in existing_entries}
    new_domains = {entry['domain']: entry['answer'] for entry in dns_entries}

    # Add new entries or update existing ones
    for entry in dns_entries:
        domain = entry['domain']
        answer = entry['answer']
        if domain in existing_domains:
            if existing_domains[domain] != answer:
                print(f"UPDATE - {domain} exists with a different answer, removing and re-adding entry.")
                remove_dns_entry(session, instance_url, domain, answer)
                add_dns_entry(session, instance_url, domain, answer)
            else:
                print(f"SKIP - {domain} already exists with the same answer, skipping.")
        else:
            add_dns_entry(session, instance_url, domain, answer)

    # Remove old entries that are not in the new list
    for domain, answer in existing_domains.items():
        if domain not in new_domains:
            remove_dns_entry(session, instance_url, domain, answer)

if __name__ == "__main__":
    required_vars = ['ADGUARD_INSTANCE', 'DNS_JSON_FILE', 'ADGUARD_USERNAME', 'ADGUARD_PASSWORD']
    env_vars = {var: os.getenv(var) for var in required_vars}
    
    # Check if all required environment variables are provided
    missing_vars = [var for var, value in env_vars.items() if not value]

    if missing_vars:
        print(f"Error: The following required environment variables are missing: {', '.join(missing_vars)}")
        print("Please set the missing environment variables and try again.")
        sys.exit(1)

    adguard_instance = env_vars['ADGUARD_INSTANCE']
    dns_json_file = env_vars['DNS_JSON_FILE']
    adguard_username = env_vars['ADGUARD_USERNAME']
    adguard_password = env_vars['ADGUARD_PASSWORD']

    print(f"Starting DNS update...\nADGUARD_INSTANCE: {adguard_instance}\nDNS JSON file: {dns_json_file}\n---------\n")

    try:
        with open(dns_json_file) as f:
            dns_entries = json.load(f)
    except FileNotFoundError:
        print(f"Error: DNS JSON file '{dns_json_file}' not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: DNS JSON file '{dns_json_file}' is not a valid JSON.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: Failed to read DNS JSON file: {e}")
        sys.exit(1)

    update_dns(adguard_instance, adguard_username, adguard_password, dns_entries)