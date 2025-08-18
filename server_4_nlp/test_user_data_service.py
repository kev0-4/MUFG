import firebase_admin
from firebase_admin import credentials, firestore
import sys

# Firebase configuration (update with your service account key path)
FIREBASE_CREDENTIALS_PATH = 'serviceAccountKey.json'

# Initialize Firebase Admin SDK
try:
    cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
    firebase_admin.initialize_app(cred)
except Exception as e:
    print(f"Error initializing Firebase: {e}")
    sys.exit(1)

db = firestore.client()

def fetch_user_data(user_id: str) -> dict:
    """
    Fetch user data from Firebase Firestore for testing.

    Args:
        user_id (str): Unique user identifier.

    Returns:
        dict: User data including name, email, super_balance, and stock_holdings.

    Raises:
        Exception: If fetch fails.
    """
    try:
        if not user_id:
            raise ValueError("User ID must be a non-empty string")

        # Fetch user document
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()
        if not user_doc.exists:
            raise ValueError(f"User {user_id} not found")

        user_data = user_doc.to_dict()

        # Fetch portfolios
        portfolio_query = db.collection('portfolios').where('userId', '==', user_id)
        portfolios = portfolio_query.get()
        super_balance = sum(portfolio.to_dict()['totalValue'] for portfolio in portfolios)

        # Fetch holdings
        holdings_query = db.collection('holdings').where('userId', '==', user_id)
        holdings = holdings_query.get()
        stock_holdings = [
            {
                'symbol': holding.to_dict()['symbol'],
                'quantity': holding.to_dict()['quantity'],
                'currentPrice': holding.to_dict()['currentPrice']
            }
            for holding in holdings
            if holding.to_dict()['assetType'] == 'stock'
        ]

        # Construct response
        result = {
            'name': user_data.get('name', ''),
            'email': user_data.get('email', ''),
            'super_balance': super_balance,
            'stock_holdings': stock_holdings
        }

        return result

    except Exception as e:
        print(f"Error fetching user data: {e}")
        raise

# Test the function
def main():
    test_user_id = 'uid1'  # From seeded data
    print(f"Testing fetch_user_data for user_id: {test_user_id}")
    try:
        user_data = fetch_user_data(test_user_id)
        print("User Data:")
        print(f"Name: {user_data['name']}")
        print(f"Email: {user_data['email']}")
        print(f"Super Balance: AUD {user_data['super_balance']:.2f}")
        print("Stock Holdings:")
        for holding in user_data['stock_holdings']:
            print(f"  Symbol: {holding['symbol']}, Quantity: {holding['quantity']}, Current Price: AUD {holding['currentPrice']:.2f}")
    except Exception as e:
        print(f"Test failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()