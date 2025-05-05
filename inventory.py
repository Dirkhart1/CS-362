# inventory.py
from database import get_db_connection
from datetime import datetime

# Add a new product for a specific user
def add_product(user_id, product_name, quantity, threshold):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO inventory (user_id, product_name, quantity, threshold)
        VALUES (?, ?, ?, ?)
    ''', (user_id, product_name, quantity, threshold))
    conn.commit()
    conn.close()

# Get all products for the current user
def get_inventory(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        SELECT id, product_name, quantity, threshold, last_updated
        FROM inventory
        WHERE user_id = ?
        ORDER BY product_name
    ''', (user_id,))
    items = cur.fetchall()
    conn.close()
    return items

# Update a product's quantity and/or threshold
def update_product(product_id, user_id, quantity=None, threshold=None):
    conn = get_db_connection()
    cur = conn.cursor()

    if quantity is not None:
        cur.execute('''
            UPDATE inventory
            SET quantity = ?, last_updated = ?
            WHERE id = ? AND user_id = ?
        ''', (quantity, datetime.now(), product_id, user_id))

    if threshold is not None:
        cur.execute('''
            UPDATE inventory
            SET threshold = ?, last_updated = ?
            WHERE id = ? AND user_id = ?
        ''', (threshold, datetime.now(), product_id, user_id))

    conn.commit()
    conn.close()

# Delete a product by ID
def delete_product(product_id, user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM inventory WHERE id = ? AND user_id = ?', (product_id, user_id))
    conn.commit()
    conn.close()
