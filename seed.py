import requests
import random
import uuid
from datetime import datetime
import sys

# ---------------------------------------
# CONFIGURATION
# ---------------------------------------
API_BASE = "http://localhost:8000"  # ← change if hosted elsewhere
YEARS = [2023, 2024, 2025]
CATEGORIES_PER_YEAR = 10
TRANSACTIONS_PER_CATEGORY = 10

CATEGORY_NAMES = [
    "Food", "Transport", "Entertainment", "Utilities", "Shopping",
    "Health", "Education", "Travel", "Gifts", "Miscellaneous"
]
PAYMENT_METHODS = ["credit card", "bank transfer", "cash", "upi"]
ACCOUNTS = ["savings", "checking", "business", "investment"]
TRANSACTION_TYPES = ["income", "expense", "transfer", "refund"]

USERS = [
    {
        "first_name": "Alice",
        "last_name": "Johnson",
        "email": "alice@example.com",
        "password": "Password123!"
    },
    {
        "first_name": "Bob",
        "last_name": "Smith",
        "email": "bob@example.com",
        "password": "Password123!"
    }
]


# ---------------------------------------
# AUTH HELPERS
# ---------------------------------------
def signup_user(user):
    print(f"Signing up user: {user['email']}")
    try:
        resp = requests.post(f"{API_BASE}/auth/signup/", json=user, timeout=10)
        if resp.status_code == 201:  # 201 Created is the correct status for user creation
            print(f"SUCCESS: User {user['email']} signed up successfully")
            return True
        elif resp.status_code == 200:  # Also accept 200 OK
            print(f"SUCCESS: User {user['email']} signed up successfully")
            return True
        elif resp.status_code == 400 and ("already exists" in resp.text.lower() or "already registered" in resp.text.lower()):
            print(f"INFO: User {user['email']} already exists, continuing with existing user")
            return True
        else:
            print(f"ERROR: Failed to signup user {user['email']}")
            print(f"       Status Code: {resp.status_code}")
            print(f"       Response: {resp.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Network error during signup for {user['email']}")
        print(f"       Details: {str(e)}")
        return False


def login_user(user):
    print(f"Logging in user: {user['email']}")
    try:
        resp = requests.post(f"{API_BASE}/auth/login/", json={
            "email": user["email"],
            "password": user["password"]
        }, timeout=10)

        if resp.status_code == 200:
            body = resp.json()
            token = None

            # check multiple possible token locations
            if "access_token" in body:
                token = body["access_token"]
            elif "data" in body and isinstance(body["data"], dict):
                token = body["data"].get("access_token")

            if token:
                print(f"SUCCESS: User {user['email']} logged in successfully")
                return token
            else:
                print(f"ERROR: Login successful but no access token found in response")
                print(f"       Response body: {body}")
                return None

        print(f"ERROR: Failed to login user {user['email']}")
        print(f"       Status Code: {resp.status_code}")
        print(f"       Response: {resp.text}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Network error during login for {user['email']}")
        print(f"       Details: {str(e)}")
        return None


# ---------------------------------------
# CATEGORY + TRANSACTION CREATION
# ---------------------------------------
def create_category(headers, name, description=None):
    data = {"name": name, "description": description or f"{name} related expenses"}
    try:
        resp = requests.post(f"{API_BASE}/categories", json=data, headers=headers, timeout=10)
        if resp.status_code == 201:  # Category endpoint returns 201 Created
            result = resp.json()
            # The response has a "data" field with the category info
            if "data" in result and "id" in result["data"]:
                category_id = result["data"]["id"]
                print(f"SUCCESS: Created category '{name}' with ID: {category_id}")
                return category_id
            else:
                print(f"ERROR: Category '{name}' created but unexpected response format")
                print(f"       Response: {result}")
                return None
        elif resp.status_code == 409:
            print(f"INFO: Category '{name}' already exists, attempting to retrieve existing category")
            # Try to get existing categories to find the ID
            get_resp = requests.get(f"{API_BASE}/categories", headers=headers, timeout=10)
            if get_resp.status_code == 200:
                categories_data = get_resp.json()
                categories = categories_data.get("categories", [])
                for cat in categories:
                    if cat["name"] == name:
                        print(f"SUCCESS: Using existing category '{name}' with ID: {cat['id']}")
                        return cat["id"]
                print(f"ERROR: Category '{name}' exists but could not retrieve its ID")
                return None
            else:
                print(f"ERROR: Failed to retrieve existing categories")
                print(f"       Status Code: {get_resp.status_code}")
                return None
        else:
            print(f"ERROR: Failed to create category '{name}'")
            print(f"       Status Code: {resp.status_code}")
            print(f"       Response: {resp.text}")
            print(f"       Request Data: {data}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Network error while creating category '{name}'")
        print(f"       Details: {str(e)}")
        return None


def create_transaction(headers, category_id, year):
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    date = datetime(year, month, day, 12, 0, 0)
    transaction_type = random.choice(TRANSACTION_TYPES)
    payment_method = random.choice(PAYMENT_METHODS)
    account = random.choice(ACCOUNTS)
    amount = round(random.uniform(10, 500), 2)

    data = {
        "name": f"{transaction_type.capitalize()} on {date.strftime('%b %d')}",
        "description": f"Auto-generated {transaction_type} transaction",
        "amount": amount,
        "transaction_date": date.isoformat(),
        "transaction_type": transaction_type,
        "payment_method": payment_method,
        "account": account,
        "category_id": str(category_id)  # Ensure category_id is string
    }

    try:
        resp = requests.post(f"{API_BASE}/transactions", json=data, headers=headers, timeout=10)
        if resp.status_code == 200:
            print(f"  SUCCESS: Created transaction '{data['name']}' (Amount: ${amount})")
        else:
            print(f"  ERROR: Failed to create transaction '{data['name']}'")
            print(f"         Status Code: {resp.status_code}")
            print(f"         Response: {resp.text}")
            print(f"         Request Data: {data}")

            # Parse and display specific error details if available
            try:
                error_data = resp.json()
                if "detail" in error_data:
                    print(f"         Error Detail: {error_data['detail']}")
            except:
                pass

    except requests.exceptions.RequestException as e:
        print(f"  ERROR: Network error while creating transaction '{data['name']}'")
        print(f"         Details: {str(e)}")
        print(f"         Request Data: {data}")


def create_transaction_with_result(headers, category_id, year):
    """Create transaction and return True/False for success tracking"""
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    date = datetime(year, month, day, 12, 0, 0)
    transaction_type = random.choice(TRANSACTION_TYPES)
    payment_method = random.choice(PAYMENT_METHODS)
    account = random.choice(ACCOUNTS)
    amount = round(random.uniform(10, 500), 2)

    data = {
        "name": f"{transaction_type.capitalize()} on {date.strftime('%b %d')}",
        "description": f"Auto-generated {transaction_type} transaction",
        "amount": amount,
        "transaction_date": date.isoformat(),
        "transaction_type": transaction_type,
        "payment_method": payment_method,
        "account": account,
        "category_id": str(category_id)
    }

    try:
        resp = requests.post(f"{API_BASE}/transactions", json=data, headers=headers, timeout=10)
        if resp.status_code == 200:
            print(f"  SUCCESS: Created transaction '{data['name']}' (Amount: ${amount})")
            return True
        else:
            print(f"  ERROR: Failed to create transaction '{data['name']}'")
            print(f"         Status Code: {resp.status_code}")
            print(f"         Response: {resp.text}")

            try:
                error_data = resp.json()
                if "detail" in error_data:
                    print(f"         Error Detail: {error_data['detail']}")
            except:
                pass
            return False

    except requests.exceptions.RequestException as e:
        print(f"  ERROR: Network error while creating transaction '{data['name']}'")
        print(f"         Details: {str(e)}")
        return False


# ---------------------------------------
# MAIN SEEDING FUNCTION
# ---------------------------------------
def seed_data_for_user(user):
    token = login_user(user)
    if not token:
        print(f"SKIPPING: Cannot seed data for {user['email']} due to login failure")
        return

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Create categories once (without dates)
    print(f"\nCreating categories for user: {user['email']}")
    category_ids = []
    failed_categories = []

    for cat_name in CATEGORY_NAMES:
        cat_id = create_category(headers, cat_name)
        if cat_id:
            category_ids.append(cat_id)
        else:
            failed_categories.append(cat_name)

    if failed_categories:
        print(f"WARNING: Failed to create {len(failed_categories)} categories: {', '.join(failed_categories)}")

    if not category_ids:
        print(f"ERROR: No categories available for user {user['email']}, skipping transaction creation")
        return

    print(f"INFO: Successfully created/retrieved {len(category_ids)} categories")

    # Create transactions for each year using existing categories
    total_transactions_created = 0
    total_transactions_failed = 0

    for year in YEARS:
        print(f"\nCreating transactions for user: {user['email']} - Year: {year}")
        year_transactions_created = 0

        for cat_id in category_ids:
            for _ in range(TRANSACTIONS_PER_CATEGORY):
                # Count transactions by checking if creation was successful
                # We'll modify create_transaction to return success/failure
                success = create_transaction_with_result(headers, cat_id, year)
                if success:
                    year_transactions_created += 1
                    total_transactions_created += 1
                else:
                    total_transactions_failed += 1

        print(f"  INFO: Created {year_transactions_created} transactions for year {year}")

    print(f"SUMMARY for {user['email']}:")
    print(f"  Categories: {len(category_ids)} successful, {len(failed_categories)} failed")
    print(f"  Transactions: {total_transactions_created} successful, {total_transactions_failed} failed")


# ---------------------------------------
# API HEALTH CHECK
# ---------------------------------------
def check_api_health():
    try:
        resp = requests.get(f"{API_BASE}/", timeout=5)
        return resp.status_code == 200
    except requests.exceptions.RequestException:
        return False


# ---------------------------------------
# RUN EVERYTHING
# ---------------------------------------
def main():
    print("Starting data seeding process...")
    print(f"Target API: {API_BASE}")

    # # Check if API is running
    # if not check_api_health():
    #     print(f"ERROR: API is not running at {API_BASE}")
    #     print("Please start your FastAPI server first with: uvicorn main:app --reload")
    #     sys.exit(1)

    print(f"SUCCESS: API is running at {API_BASE}")

    # Create / signup users
    print("\n" + "=" * 50)
    print("PHASE 1: Creating users")
    print("=" * 50)

    successful_users = []
    failed_users = []

    for user in USERS:
        if signup_user(user):
            successful_users.append(user)
        else:
            failed_users.append(user)
            print(f"SKIPPING: Will not seed data for {user['email']} due to signup failure")

    print(f"\nUser creation summary: {len(successful_users)} successful, {len(failed_users)} failed")

    # Seed data for each user
    print("\n" + "=" * 50)
    print("PHASE 2: Seeding transaction data")
    print("=" * 50)

    for user in successful_users:
        seed_data_for_user(user)

    print("\n" + "=" * 50)
    print("Data seeding process completed!")
    print("=" * 50)


if __name__ == "__main__":
    main()
