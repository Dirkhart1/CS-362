import math

def generate_order(inventory_data, sales_data, forecast_days=7, safety_stock=0):
    order_output = {}

    for item in sales_data:
        recent_sales = sales_data[item]
        if not recent_sales:
            continue  # skip items with no sales history

        avg_daily_sales = sum(recent_sales) / len(recent_sales)
        predicted_demand = avg_daily_sales * forecast_days

        current_stock = inventory_data.get(item, 0)
        reorder_qty = math.ceil(predicted_demand - current_stock + safety_stock)

        if reorder_qty > 0:
            order_output[item] = reorder_qty

    return order_output
