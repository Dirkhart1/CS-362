import os
import pandas as pd
import json
from flask import flash

# Allowed file types
ALLOWED_SALES_EXTENSIONS = {'csv', 'xlsx', 'json'}

def allowed_sales_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_SALES_EXTENSIONS

def process_sales_file(filepath):
    try:
        extension = filepath.rsplit('.', 1)[1].lower()

        if extension == 'csv':
            df = pd.read_csv(filepath)
        elif extension == 'xlsx':
            df = pd.read_excel(filepath)
        elif extension == 'json':
            with open(filepath, 'r') as f:
                data = json.load(f)
                if 'products' in data:
                    return True, "Upload successful", data
                else:
                    return False, "Invalid JSON structure", None
        else:
            return False, "Unsupported file format", None

        # Normalize columns
        df.columns = df.columns.str.lower()
        required = {'productname', 'date', 'saletotal'}
        if not required.issubset(df.columns):
            return False, "Missing one or more required columns: productname, date, saleTotal", None

        # Build output JSON
        records = []
        for _, row in df.iterrows():
            records.append({
                'productname': str(row['productname']),
                'date': str(row['date']),
                'saleTotal': float(row['saletotal'])
            })

        output = { 'products': records }

        # Save to standard location
        output_path = os.path.join('uploads', 'processed_sales.json')
        with open(output_path, 'w') as f:
            json.dump(output, f, indent=4)

        return True, "Sales file successfully processed and converted to JSON", output
    except Exception as e:
        return False, f"Error processing sales file: {e}", None
