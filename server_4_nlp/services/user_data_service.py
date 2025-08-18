import firebase_admin
from firebase_admin import credentials, firestore
from typing import Dict
from config.settings import FIREBASE_CREDENTIALS_PATH
from utils.logger import log_metadata

# Initialize Firebase Admin SDK (only once)
if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
    firebase_admin.initialize_app(cred)
db = firestore.client()

def fetch_user_data(user_id: str) -> Dict[str, any]:
    """
    Fetch user data from Firebase Firestore.

    Args:
        user_id (str): Unique user identifier.

    Returns:
        Dict[str, any]: User data including name, email, super_balance, and stock_holdings.

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
            if holding.to_dict()['assetType'] == 'stock'  # Only include stocks
        ]

        # Construct response
        result = {
            'name': user_data.get('name', ''),
            'email': user_data.get('email', ''),
            'super_balance': super_balance,
            'stock_holdings': stock_holdings
        }

        log_metadata({
            'service': 'user_service',
            'user_id': user_id,
            'status': 'success',
            'result': result
        })
        return result

    except ValueError as ve:
        log_metadata({
            'service': 'user_service',
            'user_id': user_id,
            'error': str(ve),
            'status': 'error'
        })
        raise Exception(f"Failed to fetch user data: {str(ve)}")
    except Exception as e:
        log_metadata({
            'service': 'user_service',
            'user_id': user_id,
            'error': str(e),
            'status': 'error'
        })
        raise Exception(f"Unexpected error fetching user data: {str(e)}")













# import requests
# from typing import Dict
# from config.settings import AUTH_API
# from utils.logger import log_metadata


# def fetch_user_data(user_id: str) -> Dict[str, any]:
#     """
#     Fetch user data from the Authentication Server.
    
#     Args:
#         user_id (str): Unique user identifier.
    
#     Returns:
#         Dict[str, any]: User data (e.g., {"age": 40, "income": 100000, "risk_tolerance": "balanced"}).
    
#     Raises:
#         Exception: If fetch fails.
#     """
#     try:
#         # Mock data for local development (replace with real API call in production)
#         mock_data = {
#             "age": 40,
#             "income": 100000,
#             "risk_tolerance": "balanced",
#             "super_balance": 150000
#         }
#         log_metadata({
#             "service": "user_service",
#             "user_id": user_id,
#             "status": "success (mock)"
#         })
#         return mock_data

#         # Production code (uncomment when Auth Server is available)
#         # url = f"{AUTH_API}/user/{user_id}"
#         # response = requests.get(url, timeout=5)
#         # response.raise_for_status()
#         # user_data = response.json()
#         # log_metadata({
#         #     "service": "user_service",
#         #     "user_id": user_id,
#         #     "status": "success"
#         # })
#         # return user_data
    
#     except requests.RequestException as re:
#         log_metadata({
#             "service": "user_service",
#             "user_id": user_id,
#             "error": str(re),
#             "status": "error"
#         })
#         raise Exception(f"Failed to fetch user data: {str(re)}")
#     except Exception as e:
#         log_metadata({
#             "service": "user_service",
#             "user_id": user_id,
#             "error": str(e),
#             "status": "error"
#         })
#         raise Exception(f"Unexpected error fetching user data: {str(e)}")