# file_handler.py
import pandas as pd
from inventory import add_product

# Allow only .csv and .xlsx files
ALLOWED_EXTENSIONS = {'xlsx', 'csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Parse and process uploaded file into user's inventory
def process_inventory_file(filepath, user_id):
    try:
        # Load file depending on extension
        if filepath.endswith('.csv'):
            df = pd.read_csv(filepath)
        else:
            df = pd.read_excel(filepath)

        # Validate required columns
        required_columns = {'product_name', 'quantity', 'threshold'}
        if not required_columns.issubset(df.columns.str.lower()):
            return False, "Missing required columns: product_name, quantity, threshold"

        # Normalize columns
        df.columns = df.columns.str.lower()

        # Insert each row into the database
        for _, row in df.iterrows():
            name = str(row['product_name']).strip()
            quantity = int(row['quantity'])
            threshold = int(row['threshold'])
            add_product(user_id, name, quantity, threshold)

        return True, "Upload successful"
    except Exception as e:
        return False, f"Error processing file: {e}"
