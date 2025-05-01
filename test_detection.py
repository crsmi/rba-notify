"""
Test script for verifying new observation detection

This script helps verify that the EBirdFetcher correctly identifies new observations
by simulating a scenario with known observations and then adding "new" ones.
"""
import os
import json
import time
import logging
from datetime import datetime
import shutil
import argparse
import sys

# Add parent directory to path so we can import our modules
sys.path.append(os.path.dirname(__file__))

from src.ebird_fetcher import EBirdFetcher
from config.config import COUNTIES

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("observation_test")

# Test data directory
TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'test_data')
TEST_STORAGE_FILE = os.path.join(TEST_DATA_DIR, 'test_observations.json')

# Sample observations for testing
SAMPLE_OBSERVATIONS = [
    {
        'id': '1001',
        'species': 'Common Yellowthroat',
        'scientificName': 'Geothlypis trichas',
        'count': '1',
        'date': 'Apr 25, 2025 10:00',
        'location': 'Test Location 1',
        'observer': 'Test Observer 1',
        'checklistUrl': 'https://ebird.org/checklist/S111111111'
    },
    {
        'id': '1002',
        'species': 'Golden-winged Warbler',
        'scientificName': 'Vermivora chrysoptera',
        'count': '2',
        'date': 'Apr 25, 2025 11:00',
        'location': 'Test Location 2',
        'observer': 'Test Observer 2',
        'checklistUrl': 'https://ebird.org/checklist/S222222222'
    }
]

# New observations to be "detected"
NEW_OBSERVATIONS = [
    {
        'id': '1003',
        'species': 'Cerulean Warbler',
        'scientificName': 'Setophaga cerulea',
        'count': '1',
        'date': 'Apr 25, 2025 12:00',
        'location': 'Test Location 3',
        'observer': 'Test Observer 3',
        'checklistUrl': 'https://ebird.org/checklist/S333333333'
    },
    {
        'id': '1004',
        'species': 'Connecticut Warbler',
        'scientificName': 'Oporornis agilis',
        'count': '1',
        'date': 'Apr 25, 2025 13:00',
        'location': 'Test Location 4',
        'observer': 'Test Observer 4',
        'checklistUrl': 'https://ebird.org/checklist/S444444444'
    }
]

class TestEBirdFetcher(EBirdFetcher):
    """Test version of EBirdFetcher that simulates fetching data"""
    
    def __init__(self, data_storage_file, observations=None):
        """Initialize with optional predefined observations"""
        super().__init__(data_storage_file)
        self.test_observations = observations or []
        
    def fetch_alerts(self, county):
        """Return predefined test observations instead of fetching from eBird"""
        print(f"Simulating fetch for {county['name']} County")
        return self.test_observations

def setup_test_environment():
    """Set up the test environment with clean data"""
    print("\n==================================================")
    print("SETTING UP TEST ENVIRONMENT")
    print("==================================================")
    
    # Create test data directory if it doesn't exist
    os.makedirs(TEST_DATA_DIR, exist_ok=True)
    
    # Remove any existing test storage file
    if os.path.exists(TEST_STORAGE_FILE):
        os.remove(TEST_STORAGE_FILE)
        print(f"Removed existing test storage file: {TEST_STORAGE_FILE}")
    
    print("Test environment ready")

def run_initial_detection_test():
    """Run an initial test to establish baseline data"""
    print("\n==================================================")
    print("TEST PHASE 1: INITIAL DETECTION")
    print("==================================================")
    
    # Create fetcher with initial observations
    fetcher = TestEBirdFetcher(TEST_STORAGE_FILE, SAMPLE_OBSERVATIONS)
    
    # Process the first county (doesn't matter which one for testing)
    county = COUNTIES[0]
    print(f"Testing with {county['name']} County")
    print(f"Initial observation set: {len(SAMPLE_OBSERVATIONS)} observations")
    
    # Get new alerts (should include all initial observations)
    new_alerts = fetcher.get_new_alerts(county)
    
    # Verify results
    print(f"\nRESULTS: Found {len(new_alerts)} new observations")
    for alert in new_alerts:
        print(f"  - {alert['species']} (ID: {alert['id']})")
    
    # Verify the storage file was created
    if os.path.exists(TEST_STORAGE_FILE):
        with open(TEST_STORAGE_FILE, 'r') as f:
            stored_data = json.load(f)
        print(f"Storage file created with {len(stored_data.get(county['alert_id'], []))} tracked observation IDs")
    
    return fetcher

def run_new_observation_test(fetcher):
    """Run a second test with new observations added"""
    print("\n==================================================")
    print("TEST PHASE 2: NEW OBSERVATION DETECTION")
    print("==================================================")
    
    # Add new observations to the test set
    combined_observations = SAMPLE_OBSERVATIONS + NEW_OBSERVATIONS
    fetcher.test_observations = combined_observations
    
    # Process the first county again
    county = COUNTIES[0]
    print(f"Testing with {county['name']} County")
    print(f"Combined observation set: {len(combined_observations)} observations")
    print("Added these new observations:")
    for obs in NEW_OBSERVATIONS:
        print(f"  - {obs['species']} (ID: {obs['id']})")
    
    # Get new alerts (should only include NEW_OBSERVATIONS)
    new_alerts = fetcher.get_new_alerts(county)
    
    # Verify results
    print(f"\nRESULTS: Detected {len(new_alerts)} new observations")
    for alert in new_alerts:
        print(f"  - {alert['species']} (ID: {alert['id']})")
    
    # Verify the IDs of the newly detected observations match NEW_OBSERVATIONS
    new_ids = [alert['id'] for alert in new_alerts]
    expected_ids = [obs['id'] for obs in NEW_OBSERVATIONS]
    
    missing_ids = [id for id in expected_ids if id not in new_ids]
    extra_ids = [id for id in new_ids if id not in expected_ids]
    
    if len(missing_ids) == 0 and len(extra_ids) == 0:
        print("\nSUCCESS: Correctly identified only the new observations!")
    else:
        print("\nTEST FAILED: Detection issues found")
        if missing_ids:
            print(f"Missing expected IDs: {missing_ids}")
        if extra_ids:
            print(f"Unexpected extra IDs: {extra_ids}")
    
    return len(missing_ids) == 0 and len(extra_ids) == 0

def run_no_new_observations_test(fetcher):
    """Run a third test with no new observations"""
    print("\n==================================================")
    print("TEST PHASE 3: NO NEW OBSERVATION DETECTION")
    print("==================================================")
    
    # Keep the same observation set (nothing new)
    combined_observations = SAMPLE_OBSERVATIONS + NEW_OBSERVATIONS
    fetcher.test_observations = combined_observations
    
    # Process the first county again
    county = COUNTIES[0]
    print(f"Testing with {county['name']} County")
    print(f"Same observation set: {len(combined_observations)} observations")
    print("No new observations added")
    
    # Get new alerts (should be empty)
    new_alerts = fetcher.get_new_alerts(county)
    
    # Verify results
    print(f"\nRESULTS: Detected {len(new_alerts)} new observations")
    
    if len(new_alerts) == 0:
        print("SUCCESS: Correctly identified no new observations!")
        return True
    else:
        print("TEST FAILED: Incorrectly detected new observations when none were added")
        for alert in new_alerts:
            print(f"  - {alert['species']} (ID: {alert['id']}) was incorrectly flagged as new")
        return False

def main():
    """Main test function"""
    print("\n==================================================")
    print("EBIRD RARE BIRD ALERT - NEW OBSERVATION DETECTION TEST")
    print("==================================================")
    
    setup_test_environment()
    
    try:
        # Run the three test phases
        fetcher = run_initial_detection_test()
        test_result_1 = run_new_observation_test(fetcher)
        test_result_2 = run_no_new_observations_test(fetcher)
        
        # Report overall results
        print("\n==================================================")
        print("TEST SUMMARY")
        print("==================================================")
        
        if test_result_1 and test_result_2:
            print("✅ ALL TESTS PASSED SUCCESSFULLY!")
            print("The new observation detection system is working correctly.")
        else:
            print("❌ SOME TESTS FAILED!")
            print("The new observation detection system needs attention.")
    finally:
        # Optional cleanup - uncomment if you want to remove test data after running
        # if os.path.exists(TEST_DATA_DIR):
        #     shutil.rmtree(TEST_DATA_DIR)
        #     print(f"Removed test directory: {TEST_DATA_DIR}")
        pass
    
    print("\n==================================================")

if __name__ == "__main__":
    main()