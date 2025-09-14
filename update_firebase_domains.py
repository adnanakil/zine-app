#!/usr/bin/env python3
"""
Script to add archgest.com to Firebase authorized domains
"""
import json
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def get_access_token():
    """Get access token using service account key"""
    try:
        import firebase_admin
        from firebase_admin import credentials

        # Initialize Firebase Admin with service account
        if not firebase_admin._apps:
            cred = credentials.Certificate('serviceAccountKey.json')
            firebase_admin.initialize_app(cred)

        # Get access token
        access_token = cred.get_access_token()
        return access_token.access_token
    except Exception as e:
        print(f"Error getting access token: {e}")
        return None

def add_authorized_domain(project_id, domain):
    """Add domain to Firebase authorized domains"""
    access_token = get_access_token()
    if not access_token:
        print("Failed to get access token")
        return False

    # Get current configuration
    url = f"https://identitytoolkit.googleapis.com/admin/v2/projects/{project_id}/config"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    try:
        # Get current config
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to get config: {response.status_code} - {response.text}")
            return False

        config = response.json()

        # Add domain to authorized domains if not already present
        authorized_domains = config.get('authorizedDomains', [])
        if domain not in authorized_domains:
            authorized_domains.append(domain)
            config['authorizedDomains'] = authorized_domains

            # Update configuration
            update_response = requests.patch(url, headers=headers, json=config)
            if update_response.status_code == 200:
                print(f"Successfully added {domain} to authorized domains")
                return True
            else:
                print(f"Failed to update config: {update_response.status_code} - {update_response.text}")
                return False
        else:
            print(f"{domain} already in authorized domains")
            return True

    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    project_id = os.getenv('FIREBASE_PROJECT_ID', 'archgest-20638')
    domain = 'archgest.com'

    print(f"Adding {domain} to Firebase project {project_id}")
    success = add_authorized_domain(project_id, domain)

    if success:
        print("✅ Domain added successfully!")
    else:
        print("❌ Failed to add domain")