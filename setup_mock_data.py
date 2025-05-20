#!/usr/bin/env python3
"""
Master script to set up all mock data for the wellness agent.
This will populate Firestore with employee data and Cloud Storage with wellness resources.
"""

import os
import sys
import subprocess
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_setup_script(script_path):
    """Run a setup script and check for errors"""
    logger.info(f"Running setup script: {script_path}")
    
    try:
        # Run the script as a subprocess
        result = subprocess.run(
            [sys.executable, script_path],
            check=True,
            capture_output=True,
            text=True
        )
        
        # Log the output
        for line in result.stdout.splitlines():
            logger.info(line)
        
        logger.info(f"Successfully completed: {script_path}")
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running {script_path}: {e}")
        logger.error(f"STDOUT: {e.stdout}")
        logger.error(f"STDERR: {e.stderr}")
        return False

def main():
    """Run all setup scripts"""
    logger.info("Starting mock data setup process")
    
    # Define the setup scripts
    setup_scripts = [
        os.path.join("mock_db", "setup_firestore.py"),
        os.path.join("mock_db", "setup_storage.py")
    ]
    
    # Run each setup script
    success = True
    for script in setup_scripts:
        if not run_setup_script(script):
            success = False
    
    if success:
        logger.info("All mock data setup completed successfully!")
        logger.info("You can now test the wellness agent with sample data.")
    else:
        logger.error("One or more setup scripts failed. Please check the logs.")
        sys.exit(1)

if __name__ == "__main__":
    main() 