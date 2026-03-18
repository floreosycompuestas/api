"""
Test script for bird update endpoint with band_id support.

This script demonstrates how to update a bird using father_band_id and mother_band_id
instead of father_id and mother_id. Parent birds are automatically created if they don't exist.
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/birds"

# Test credentials (adjust as needed)
USERNAME = "testuser"
PASSWORD = "testpass"

def get_auth_token():
    """Get authentication token"""
    response = requests.post(
        f"{BASE_URL}/login",
        data={"username": USERNAME, "password": PASSWORD}
    )
    if response.status_code == 200:
        return response.cookies.get("access_token")
    else:
        print(f"Login failed: {response.status_code} - {response.text}")
        return None

def test_update_bird_with_band_ids(bird_id: int, auth_token: str):
    """
    Test updating a bird using father_band_id and mother_band_id.

    Example scenarios:
    1. Update with existing parent band_ids
    2. Update with non-existing parent band_ids (auto-create)
    3. Clear parents by passing empty strings
    """

    cookies = {"access_token": auth_token}

    # Test 1: Update bird with new parent band IDs (will auto-create if not exist)
    print("\n=== Test 1: Update bird with parent band IDs ===")
    update_data = {
        "name": "Updated Bird Name",
        "father_band_id": "BR001-2023-01",  # Will be created if doesn't exist
        "mother_band_id": "BR001-2023-02"   # Will be created if doesn't exist
    }

    response = requests.put(
        f"{API_URL}/{bird_id}",
        json=update_data,
        cookies=cookies
    )

    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        bird = response.json()
        print(f"Updated bird: {json.dumps(bird, indent=2)}")
        print(f"Father ID: {bird.get('father_id')}")
        print(f"Mother ID: {bird.get('mother_id')}")
    else:
        print(f"Error: {response.text}")

    # Test 2: Update only mother_band_id
    print("\n=== Test 2: Update only mother_band_id ===")
    update_data = {
        "mother_band_id": "BR001-2023-03"
    }

    response = requests.put(
        f"{API_URL}/{bird_id}",
        json=update_data,
        cookies=cookies
    )

    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        bird = response.json()
        print(f"Mother ID: {bird.get('mother_id')}")
    else:
        print(f"Error: {response.text}")

    # Test 3: Clear father by passing empty string
    print("\n=== Test 3: Clear father (empty string) ===")
    update_data = {
        "father_band_id": ""
    }

    response = requests.put(
        f"{API_URL}/{bird_id}",
        json=update_data,
        cookies=cookies
    )

    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        bird = response.json()
        print(f"Father ID after clearing: {bird.get('father_id')}")
    else:
        print(f"Error: {response.text}")

    # Test 4: Verify auto-created parent birds
    print("\n=== Test 4: Verify auto-created parent birds ===")

    # Check if father bird was created
    response = requests.get(
        f"{API_URL}/band/BR001-2023-01",
        cookies=cookies
    )
    if response.status_code == 200:
        father = response.json()
        print(f"Father bird created: {json.dumps(father, indent=2)}")
        print(f"Sex: {father.get('sex')} (should be 'M')")

    # Check if mother bird was created
    response = requests.get(
        f"{API_URL}/band/BR001-2023-03",
        cookies=cookies
    )
    if response.status_code == 200:
        mother = response.json()
        print(f"Mother bird created: {json.dumps(mother, indent=2)}")
        print(f"Sex: {mother.get('sex')} (should be 'F')")


if __name__ == "__main__":
    print("Bird Update Test with Band IDs")
    print("=" * 50)

    # Get authentication token
    auth_token = get_auth_token()
    if not auth_token:
        print("Failed to authenticate. Exiting.")
        exit(1)

    # Specify the bird ID to update (you need to change this)
    bird_id = 1  # Change this to an actual bird ID in your database

    # Run tests
    test_update_bird_with_band_ids(bird_id, auth_token)

    print("\n" + "=" * 50)
    print("Test completed!")

