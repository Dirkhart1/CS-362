from flask import Flask, render_template, request, redirect, session, flash
from auth import register_user, login_user, logout_user, is_logged_in, get_current_user
from inventory import add_product, get_inventory, delete_product, update_product
from file_handler import allowed_sales_file, process_sales_file
from restocking import get_low_stock_items, restock_item, alert_user_on_low_stock
from database import init_db
from dotenv import load_dotenv
from collections import defaultdict
import os
import json
import math

# Setup
load_dotenv()
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace in production

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize DB
init_db()

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

    alert_user_on_low_stock(user_id)
    items = get_inventory(user_id)

    # Compute totals
    totals = defaultdict(int)
    for item in items:
        totals[item[1]] += item[2]

    return render_template('inventory.html', items=items, totals=totals)

@app.route('/update_quantity', methods=['POST'])
def update_quantity():
    user_id = get_current_user()
    if not user_id:
        return redirect('/login')

    product_id = request.form.get('product_id')
    direction = request.form.get('direction')

    items = get_inventory(user_id)
    for item in items:
        if str(item[0]) == product_id:
            current_quantity = item[2]
            new_quantity = current_quantity + 1 if direction == 'up' else max(0, current_quantity - 1)
            update_product(product_id, user_id, quantity=new_quantity)
            break

    return redirect('/inventory')

@app.route('/update_threshold', methods=['POST'])
def update_threshold():
    user_id = get_current_user()
    if not user_id:
        return redirect('/login')

    product_id = request.form.get('product_id')
    direction = request.form.get('direction')

    items = get_inventory(user_id)
    for item in items:
        if str(item[0]) == product_id:
            current_threshold = item[3]
            new_threshold = current_threshold + 1 if direction == 'up' else max(0, current_threshold - 1)
            update_product(product_id, user_id, threshold=new_threshold)
            break

    return redirect('/inventory')

@app.route('/delete', methods=['POST'])
def delete():
    user_id = get_current_user()
    if not user_id:
        return redirect('/login')

    product_id = request.form.get('product_id')
    if product_id:
        delete_product(product_id, user_id)
        flash("Product deleted.")
    return redirect('/inventory')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    user_id = get_current_user()
    if not user_id:
        return redirect('/login')

    if request.method == 'POST':
        file = request.files.get('file')
        if file and allowed_sales_file(file.filename):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            success, msg, data = process_sales_file(filepath)
            if success:
                flash(msg)
                return render_template('confirm_sales.html', products=data['products'])
            else:
                flash(msg)
                return redirect('/upload')
        flash("Invalid file type. Please upload .csv, .xlsx, or .json")
    return render_template('upload.html')

@app.route('/confirm', methods=['POST'])
def confirm():
    user_id = get_current_user()
    if not user_id:
        return redirect('/login')

    num_products = len([key for key in request.form.keys() if key.startswith('product_name_')])

    for i in range(num_products):
        name = request.form[f'product_name_{i}']
        quantity = int(request.form[f'quantity_{i}'])
        sale_total = float(request.form[f'sale_total_{i}'])
        threshold = math.ceil(sale_total * 0.25)
        add_product(user_id, name, quantity, threshold)

    flash("Products successfully added to inventory.")
    return redirect('/inventory')

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

if __name__ == '__main__':
    app.run(debug=True)
