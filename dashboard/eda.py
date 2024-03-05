import pandas as pd
import seaborn as sns

sns.set(style='dark')

# --- Multi-purpose Function ---

def create_monthly_orders_df(df):
    # Resampling and Aggregation the dataFrame based on order_date ('D' indicates day)
    monthly_orders_df = df.resample(rule='D', on='order_purchase_date').agg({
        "order_id": "nunique", # Count the number of unique order IDs per day
        "payment_value": "sum", # Sum the total price of orders per day
    })
    # resetting index
    monthly_orders_df = monthly_orders_df.reset_index()
    # rename the column
    monthly_orders_df.rename(columns={
        "order_id": "order_count",
        "payment_value": "sales",
    }, inplace=True)
    
    return monthly_orders_df

def create_order_sales_items_df(df):
    # Group the data by product_category_name, count total order_id column, and sum payment_value column
    order_sales_items_df = df.groupby("product_category_name").agg(
    num_of_order=pd.NamedAgg(column='order_id', aggfunc='nunique'),
    total_value=pd.NamedAgg(column='payment_value', aggfunc='sum')
    ).reset_index()
    # resetting index
    order_sales_items_df = order_sales_items_df.reset_index()
    # rename the column
    order_sales_items_df.rename(columns={
        "product_category_name": "category_name",
        "num_of_order": "order_count",
        "total_value": "sales"
    }, inplace=True)
    
    return order_sales_items_df

def create_byregion_df(df):
    # Group the data by state, count the number of unique customer IDs, and resetting index
    byregion_df = df.groupby("customer_Region").agg(
    customer_count=pd.NamedAgg(column='customer_id', aggfunc='nunique'),
    order_count=pd.NamedAgg(column='order_id', aggfunc='nunique')
    ).reset_index()
    # rename the column
    byregion_df.rename(columns={
        "customer_Region": "region",
        "customer_count": "num_of_customer",
        "order_count": "num_of_order"
    }, inplace=True)
    
    return byregion_df

def create_pay_type_byregion_df(df):
    # Group the data by payment_type, count the number of unique order IDs, and resetting index
    pay_type_byregion_df = df.groupby("payment_type").agg(
    customer_count=pd.NamedAgg(column='customer_id', aggfunc='nunique'),
    order_count=pd.NamedAgg(column='order_id', aggfunc='nunique')
    ).reset_index()
    # rename the column
    pay_type_byregion_df.rename(columns={
        "customer_count": "num_of_customer",
        "order_count": "num_of_order"
    }, inplace=True)
    
    return pay_type_byregion_df