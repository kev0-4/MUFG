from typing import Dict, Any
from datetime import datetime, timedelta
import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
from config.settings import FIREBASE_CREDENTIALS_PATH

# Initialize Firebase Admin SDK (only once)
if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
    firebase_admin.initialize_app(cred)
db = firestore.client()


def fetch_user_data(user_id: str) -> Dict[str, Any]:
    """
    Fetch user data from Firebase Firestore, including stock holdings.

    Args:
        user_id (str): Unique user identifier.

    Returns:
        Dict[str, Any]: User data with user_id, super_balance, and stock_holdings.

    Raises:
        ValueError: If user_id is invalid or user not found.
        Exception: For other Firestore errors.
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
        portfolio_query = db.collection(
            'portfolios').where('userId', '==', user_id)
        portfolios = portfolio_query.get()
        super_balance = sum(portfolio.to_dict()[
                            'totalValue'] for portfolio in portfolios)

        # Fetch holdings
        holdings_query = db.collection(
            'holdings').where('userId', '==', user_id)
        holdings = holdings_query.get()
        stock_holdings = [
            {
                'stock': holding.to_dict()['symbol'],
                'quantity': holding.to_dict()['quantity'],
                'currentPrice': holding.to_dict()['currentPrice']
                # Note: historical_data not included (requires external API or schema update)
            }
            for holding in holdings
            if holding.to_dict()['assetType'] == 'stock'
        ]

        # Construct response
        result = {
            'user_id': user_id,
            'super_balance': super_balance,
            'stock_holdings': stock_holdings
            # Note: age, risk_tolerance, historical_return not in schema
        }
        print(result)
        return result

    except ValueError as ve:
        raise ValueError(f"Failed to fetch user data: {str(ve)}")
    except Exception as e:
        raise Exception(f"Unexpected error fetching user data: {str(e)}")
