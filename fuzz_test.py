import requests   # I use this library to send HTTP requests directly to my Flask app
import random     # Used to randomly pick a payload for fuzz testing
import string     # I keep this for future payload generation if needed


# "▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄"▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄"▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄"▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
#                                  -->  SQL / XSS ATTACK PAYLOADS  <--
# "▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄"▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄"▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄

def generate_fuzz_payload():   # This function gives me one random attack-style string to test my app
    """Return one random payload used for fuzz testing."""   # Quick description of what the function does

    payloads = [   # List of different malicious-style inputs that attackers commonly try
        "' OR 1='1",                           # Classic SQL injection trick to bypass login logic
        "' UNION SELECT 1,2,3--",              # Tries to force the database to return extra data
        "; DROP TABLE users--",                # Dangerous SQL injection that tries to delete the users table
        "<script>alert('xss')</script>",       # Basic XSS attempt to execute JavaScript
        "<img src=x onerror=alert(1)>",        # XSS using an image tag with an error event
        "../../../../../etc/passwd",           # Path traversal attempt to reach system files
        "; ls -la",                            # Command injection test to list server files
        "A" * 1000,                            # Very long string to test buffer handling or crashing
        "\x00" * 50,                           # Null bytes to test unusual character handling
        "{{7*7}}",                             # Template injection test (Jinja2 style)
        "${7*7}",                              # Another template/code evaluation attempt
    ]

    return random.choice(payloads)   # Pick one payload randomly for each fuzz test run


# "▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄"▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄"▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄"▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
#                                  -->  CHECKING ALL ENDPOINTS  <--
# "▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄"▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄"▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄"▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄

def fuzz_endpoints():   # This tests if each page of my Flask app loads correctly
    BASE_URL = "http://localhost:5000"   # Address where my Flask app is running

    endpoints = [   # List of routes I want to test
        "/register",   # Registration page
        "/login",      # Login page
        "/dashboard",  # Dashboard that requires login
        "/input_test", # Input validation page
        "/xss_demo",   # XSS demonstration page
    ]

    print("Starting endpoint fuzz testing...")   # Let me know the process started
    print("=" * 50)                              # Simple visual separator

    for endpoint in endpoints:   # Loop through each endpoint
        print(f"\nTesting endpoint: {endpoint}")   # Show the current page being tested

        try:   # Attempt to send a GET request
            response = requests.get(url=f"{BASE_URL}{endpoint}", timeout=5)  # Try loading the page
            print(f"Status: {response.status_code}")  # Print the status code (200 means OK)
        except Exception as e:   # If something fails
            print(f"Error while testing {endpoint}: {e}")   # Print the error to help debugging


# "▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄"▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄"▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄"▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
#                                -->  SQLi AND XSS PAYLOAD TESTING  <--
# "▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄"▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄"▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄"▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄

def fuzz_forms():   # This tests if form inputs correctly handle malicious-style inputs
    BASE_URL = "http://localhost:5000"   # Path to my running Flask app

    print("\nFuzzing form inputs with malicious-style data...")   # Notify test start
    print("=" * 50)                                               # Separator line

    # SQL injection-style payload for the register form
    test_data = {
        "username": "admin' OR '1'='1",   # SQL trick attempting to bypass validation
        "email": "test@test.com",         # Normal email value
        "password": "password123",        # Normal password
        "confirm": "password123"          # Confirm password matches
    }

    try:   # Try to submit the form
        response = requests.post(f"{BASE_URL}/register", data=test_data, timeout=5)  # Send POST request
        print(f"SQL injection test on /register - Status: {response.status_code}")   # Show response code

        # Check if the response contains words that indicate a backend failure
        if "error" in response.text.lower() or "exception" in response.text.lower():
            print("Possible SQL injection issue detected.")   # Warn about potential vulnerability

    except Exception as e:   # Catch request-level errors
        print(f"Error during SQL injection-style test: {e}")  # Print the error for troubleshooting

    # XSS-style payload for input_test route
    xss_data = {"user_input": "<script>alert('XSS')</script>"}   # Attempted script injection

    try:   # Try sending the XSS input
        response = requests.post(f"{BASE_URL}/input_test", data=xss_data, timeout=5)  # Send POST request
        print(f"XSS test on /input_test - Status: {response.status_code}")            # Print status code

        # If the word “blocked” is missing, maybe the script wasn't caught
        if "blocked" not in response.text.lower():
            print("Possible XSS issue detected.")   # Warn about suspicious behaviour

    except Exception as e:   # If the request itself fails
        print(f"Error during XSS-style test: {e}")  # Print the error message


# "▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄"▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄"▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄"▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄
#                           -->  MAIN EXECUTION FOR THE FUZZ SCRIPT  <--
# "▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄"▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄"▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄"▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄▄

if __name__ == "__main__":   # Run this block only when the script is executed directly
    print("NOTE: Make sure your Flask app is running on http://localhost:5000")   # Reminder to start Flask
    input("Press Enter to start fuzzing...")   # Pause so I can confirm everything is ready

    fuzz_endpoints()   # First check if all pages load normally
    fuzz_forms()       # Then test forms with SQLi and XSS-style inputs

    print("\n" + "=" * 50)     # Spacer line for clean output
    print("Fuzz testing completed.")   # Let me know the script finished
