#!/usr/bin/env python3
"""
Script to check Google Cloud Storage authentication on startup.
This will verify that the service account credentials are valid.
"""

import os
import sys
import datetime
from google.cloud import storage

def check_gcs_auth():
    """Check Google Cloud Storage authentication"""
    print("Checking Google Cloud Storage authentication...")
    
    # Check environment variables
    env_vars = {
        "GOOGLE_CLOUD_PROJECT": os.environ.get("GOOGLE_CLOUD_PROJECT"),
        "GOOGLE_CLOUD_STORAGE_BUCKET": os.environ.get("GOOGLE_CLOUD_STORAGE_BUCKET"),
        "GOOGLE_APPLICATION_CREDENTIALS": os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    }
    
    for var_name, var_value in env_vars.items():
        if not var_value:
            print(f"ERROR: {var_name} environment variable is not set.")
            return False
        print(f"  {var_name}: {var_value}")
    
    # Check if credentials file exists
    creds_path = env_vars["GOOGLE_APPLICATION_CREDENTIALS"]
    if not os.path.exists(creds_path):
        print(f"ERROR: Service account credentials file not found at: {creds_path}")
        return False
    
    bucket_name = env_vars["GOOGLE_CLOUD_STORAGE_BUCKET"]
    
    # Test connection to Cloud Storage
    try:
        storage_client = storage.Client()
        print(f"Successfully created storage client with project: {storage_client.project}")
        
        # Check credentials expiration
        credentials = storage_client._credentials
        if hasattr(credentials, 'expiry'):
            if credentials.expiry:
                now = datetime.datetime.now(datetime.timezone.utc)
                time_until_expiry = credentials.expiry - now
                print(f"Credentials expiry: {credentials.expiry}")
                print(f"Time until credentials expire: {time_until_expiry}")
                if time_until_expiry.total_seconds() < 300:  # Less than 5 minutes
                    print("WARNING: Credentials will expire soon!")
            else:
                print("Credentials do not have an expiry set")
        else:
            print("Credentials do not have expiry information")
        
        bucket = storage_client.bucket(bucket_name)
        
        if not bucket.exists():
            print(f"ERROR: Bucket {bucket_name} doesn't exist or is not accessible.")
            return False
        
        print(f"Successfully connected to bucket: {bucket_name}")
        
        # Test generating a signed URL
        test_file = "wellness_guides/mental_health/mental_health_guide.md"
        blob = bucket.blob(test_file)
        
        if not blob.exists():
            print(f"WARNING: Test file {test_file} doesn't exist. Skipping signed URL test.")
        else:
            # Test with standard expiration
            try:
                url = blob.generate_signed_url(
                    version="v4",
                    expiration=300,  # 5 minutes
                    method="GET"
                )
                print(f"Successfully generated signed URL (5 min expiration) for {test_file}")
                print(f"URL: {url}")
            except Exception as e:
                print(f"ERROR: Failed to generate standard signed URL: {str(e)}")
            
            # Test with longer expiration
            try:
                long_url = blob.generate_signed_url(
                    version="v4",
                    expiration=7200,  # 2 hours
                    method="GET",
                    credentials=storage_client._credentials
                )
                print(f"Successfully generated signed URL (2 hour expiration) for {test_file}")
                print(f"Long URL: {long_url}")
            except Exception as e:
                print(f"ERROR: Failed to generate long-expiration signed URL: {str(e)}")
        
        return True
    except Exception as e:
        print(f"ERROR: Failed to access Google Cloud Storage: {str(e)}")
        return False

if __name__ == "__main__":
    if check_gcs_auth():
        print("Google Cloud Storage authentication is working correctly.")
        sys.exit(0)
    else:
        print("Google Cloud Storage authentication check failed.")
        sys.exit(1)
