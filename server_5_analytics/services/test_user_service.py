import sys
from services.user_service import fetch_user_data


def test_user_service():
    test_user_id = 'uid1'  # From seeded data
    print(f"Testing fetch_user_data for user_id: {test_user_id}")
    try:
        user_data = fetch_user_data(test_user_id)
        print("fetched successfully")
        print("User Data:")
        print(f"User ID: {user_data['user_id']}")
        print(f"Super Balance: AUD {user_data['super_balance']:.2f}")
        print("Stock Holdings:")
        for holding in user_data['stock_holdings']:
            print(
                f"  Stock: {holding['stock']}, Quantity: {holding['quantity']}, Current Price: AUD {holding['currentPrice']:.2f}")
            print(f"  Historical Data (last 5 entries):")
            print(holding['historical_data'].tail(5)[
                  ['ds', 'y']].to_string(index=False))
    except Exception as e:
        print(f"Test failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    test_user_service()
