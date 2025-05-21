#!/usr/bin/env python3
"""
Script to check Google Cloud Storage authentication on startup.
This will verify that the service account credentials are valid.
"""

import os
import sys
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
            url = blob.generate_signed_url(
                version="v4",
                expiration=300,  # 5 minutes
                method="GET"
            )
            print(f"Successfully generated signed URL for {test_file}")
            print(f"URL: {url}")
        
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
