# app.py
from flask import Flask, render_template, request, redirect, session, flash
from auth import register_user, login_user, logout_user, is_logged_in, get_current_user
from inventory import add_product, get_inventory
from file_handler import allowed_file, process_inventory_file
from restocking import get_low_stock_items, restock_item, alert_user_on_low_stock
from database import init_db
from dotenv import load_dotenv
import os

# Setup
load_dotenv()
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace in production

# Upload config
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize database
init_db()

# ---------- AUTH ROUTES ----------

@app.route('/')
def index():
    return redirect('/inventory') if is_logged_in() else redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        success = register_user(
            request.form['username'],
            request.form['email'],
            request.form['password']
        )
        if success:
            flash("Registration successful!")
            return redirect('/login')
        flash("Email or username already exists.")
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if login_user(request.form['email'], request.form['password']):
            return redirect('/inventory')
        flash("Invalid email or password.")
    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/login')

# ---------- INVENTORY ROUTE ----------

@app.route('/inventory', methods=['GET', 'POST'])
def inventory():
    user_id = get_current_user()
    if not user_id:
        return redirect('/login')

    if request.method == 'POST':
        add_product(
            user_id,
            request.form['product_name'],
            int(request.form['quantity']),
            int(request.form['threshold'])
        )
        flash("Product added.")
        return redirect('/inventory')

    alert_user_on_low_stock(user_id)  # Optional: trigger email alerts
    items = get_inventory(user_id)
    return render_template('inventory.html', items=items)

# ---------- UPLOAD ROUTE ----------

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    user_id = get_current_user()
    if not user_id:
        return redirect('/login')

    if request.method == 'POST':
        file = request.files.get('file')
        if file and allowed_file(file.filename):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            success, msg = process_inventory_file(filepath, user_id)
            flash(msg)
            alert_user_on_low_stock(user_id)  # Optional: trigger email alerts
            return redirect('/inventory')
        flash("Invalid file type. Please upload a .csv or .xlsx.")
    return render_template('upload.html')

# ---------- RESTOCK ROUTE ----------

@app.route('/restock', methods=['GET', 'POST'])
def restock():
    user_id = get_current_user()
    if not user_id:
        return redirect('/login')

    if request.method == 'POST':
        item_id = request.form.get('item_id')
        restock_item(item_id, user_id)
        flash("Item restocked.")
        return redirect('/restock')

    items = get_low_stock_items(user_id)
    return render_template('restock.html', items=items)

# ---------- START SERVER ----------

if __name__ == '__main__':
    app.run(debug=True)
