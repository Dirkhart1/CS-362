# restocking.py
from database import get_db_connection
from email_alert import send_low_stock_alert
from auth import get_user_email

# Get all items where quantity is below threshold
def get_low_stock_items(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT id, product_name, quantity, threshold
        FROM inventory
        WHERE user_id = ? AND quantity < threshold
    ''', (user_id,))
    items = cur.fetchall()
    conn.close()
    return items

# Restock one item by setting its quantity to the threshold
def restock_item(item_id, user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        UPDATE inventory
        SET quantity = threshold
        WHERE id = ? AND user_id = ?
    ''', (item_id, user_id))
    conn.commit()
    conn.close()

# OPTIONAL: Email the user when items are low
def alert_user_on_low_stock(user_id):
    low_items = get_low_stock_items(user_id)
    user_email = get_user_email(user_id)
    
    for item in low_items:
        send_low_stock_alert(
            user_email,
            product_name=item[1],
            quantity=item[2],
            threshold=item[3]
        )
