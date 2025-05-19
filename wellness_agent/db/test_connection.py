#!/usr/bin/env python
"""Test database connections for the Wellness Agent."""

import os
import sys
import datetime
from typing import Dict, List, Tuple, Any
from dotenv import load_dotenv

# Add the project root to the path to allow importing the module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from wellness_agent.db.firestore import FirestoreClient
from wellness_agent.db.bigquery import BigQueryClient

def test_firestore_connection():
    """Test the connection to Firestore."""
    print("Testing Firestore connection...")
    
    # Get project ID from environment
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    
    print(f"Project ID: {project_id}")
    print(f"Credentials path: {os.path.basename(credentials_path) if credentials_path else 'None'}")
    
    try:
        # Initialize the client
        client = FirestoreClient(project_id)
        
        # Create a test document
        collection = "test_connection"
        doc_id = f"test_{datetime.datetime.now().timestamp()}"
        
        test_data = {
            "test_message": "Hello from the wellness agent!",
            "timestamp": datetime.datetime.now()
        }
        
        # Write the document
        doc_ref = client.db.collection(collection).document(doc_id)
        doc_ref.set(test_data)
        
        # Read the document
        doc = doc_ref.get()
        
        if doc.exists:
            print("✅ Successfully connected to Firestore!")
            print("✅ Successfully wrote and read a test document")
            print(f"Test document data: {doc.to_dict()}")
            
            # Clean up
            doc_ref.delete()
            print("✅ Successfully deleted the test document")
            return True
        else:
            print("❌ Failed to read the test document")
            return False
            
    except Exception as e:
        print(f"❌ Firestore connection failed: {e}")
        return False

def test_bigquery_connection():
    """Test the connection to BigQuery."""
    print("\nTesting BigQuery connection...")
    
    # Get project ID from environment
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    
    print(f"Project ID: {project_id}")
    print(f"Credentials path: {os.path.basename(credentials_path) if credentials_path else 'None'}")
    
    try:
        # Initialize the client
        client = BigQueryClient(project_id)
        
        # Make sure the dataset exists
        client._ensure_dataset_exists()
        print("✅ Successfully created or verified the BigQuery dataset!")
        
        # Make sure the table exists
        client._ensure_metrics_table_exists()
        print("✅ Successfully created or verified the metrics table!")
        
        # Try to execute a simple query
        query = f"SELECT 1 AS test_value"
        query_job = client.client.query(query)
        result = list(query_job)[0]
        
        if result.test_value == 1:
            print("✅ Successfully executed a test query!")
            return True
        else:
            print("❌ Query executed but returned unexpected results")
            return False
            
    except Exception as e:
        print(f"❌ BigQuery connection failed: {e}")
        return False

def test_all_connections() -> Dict[str, Any]:
    """Test all database connections and return results in API-friendly format.
    
    Returns:
        Dictionary with test results and details
    """
    # Load environment variables
    load_dotenv()
    
    # Test connections
    firestore_success = test_firestore_connection()
    bigquery_success = test_bigquery_connection()
    
    # Build result object
    results = {
        "success": firestore_success and bigquery_success,
        "timestamp": datetime.datetime.now().isoformat(),
        "tests": {
            "firestore": {
                "success": firestore_success,
                "project_id": os.getenv("GOOGLE_CLOUD_PROJECT"),
                "message": "Successfully connected to Firestore" if firestore_success else "Failed to connect to Firestore"
            },
            "bigquery": {
                "success": bigquery_success,
                "project_id": os.getenv("GOOGLE_CLOUD_PROJECT"),
                "message": "Successfully connected to BigQuery" if bigquery_success else "Failed to connect to BigQuery"
            }
        }
    }
    
    return results

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    # Test connections
    firestore_success = test_firestore_connection()
    bigquery_success = test_bigquery_connection()
    
    # Report summary
    print("\nConnection Test Summary:")
    print(f"Firestore: {'✅ Connected' if firestore_success else '❌ Failed'}")
    print(f"BigQuery: {'✅ Connected' if bigquery_success else '❌ Failed'}")
    
    if firestore_success and bigquery_success:
        print("\n🎉 All database connections successful!")
        sys.exit(0)
    else:
        print("\n❌ One or more database connections failed. Please check your configuration.")
        sys.exit(1) 