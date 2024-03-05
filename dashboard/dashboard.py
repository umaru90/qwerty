import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
from babel.numbers import format_currency

# Import custom functions
from eda import create_monthly_orders_df, create_order_sales_items_df, create_byregion_df, create_pay_type_byregion_df
from rfm import create_rfm_df, create_rfm_df_quantile, customer_segment, create_rfm_segment_distribution

st.sidebar.success("Ini Merupakan sebuah Final Project Data Analytics")

st.title("Brazilian E-Commerce Public Dashboard :sparkles:") 
st.header('Brazilian E-Commerce EDA', divider='rainbow')
st.subheader('Orderan Harian')

# Dapatkan direktori saat ini
path = os.path.dirname(__file__)

# Ganti jalur file sesuai dengan direktori saat ini
data_source = os.path.join(path, 'main_data_eda.csv')
all_data = pd.read_csv(data_source)

# Ganti jalur file sesuai dengan direktori saat ini
location = os.path.join(path, 'main_data_rfm.csv')
rfm_df_score = pd.read_csv(location)

datetime_columns = ["order_purchase_timestamp", "order_purchase_date", "order_estimated_delivery_date", "order_delivered_date"]
all_data.sort_values(by="order_purchase_date", inplace=True)
all_data.reset_index(inplace=True)
for column in datetime_columns:
    all_data[column] = pd.to_datetime(all_data[column])

min_date = all_data["order_purchase_date"].min()
max_date = all_data["order_purchase_date"].max()

group_columns = ['order_date_year', 'order_date_month', 'month-year']
year_monthly_order = all_data.groupby(group_columns)['order_id'].nunique().reset_index()

year_monthly_order_2017 = year_monthly_order[year_monthly_order['order_date_year'] == 2017]
year_monthly_order_2018 = year_monthly_order[year_monthly_order['order_date_year'] == 2018]

year_monthly_order_2017.rename(columns={
    "order_id": "total_order",
    "order_date_month": "month",
}, inplace=True)

year_monthly_order_2018.rename(columns={
    "order_id": "total_order",
    "order_date_month": "month",
}, inplace=True)

with st.sidebar:
    start_date, end_date = st.date_input(
        label='Date Range',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

main_df = all_data[(all_data["order_purchase_date"] >= str(start_date)) & 
            (all_data["order_purchase_date"] <= str(end_date))]

monthly_orders_df = create_monthly_orders_df(main_df)
order_sales_items_df = create_order_sales_items_df(main_df)
byregion_df = create_byregion_df(main_df)
pay_type_byregion_df = create_pay_type_byregion_df(main_df)

col1_left, col2_right = st.columns(2)

with col1_left:
    total_orders = monthly_orders_df.order_count.sum()
    st.metric("Total Order", value=total_orders)

with col2_right:
    total_sales = format_currency(monthly_orders_df.sales.sum(), "$", locale='es_CO') 
    st.metric("Total Sales", value=total_sales)


st.markdown("")
st.subheader('Orderan Bulanan')
col1_line_chart, col2_line_chart = st.columns(2)

with col1_line_chart:
    colors = ["#D3D3D3"]
    st.write("##### Total Pesanan Toko Pada Tahun 2017")
    st.line_chart(
        year_monthly_order_2017, 
        x="month", 
        y="total_order", 
        color=colors
    )

with col2_line_chart:
    colors = ["#90CAF9"]
    st.write("##### Total Pesanan Toko pada Tahun 2018")
    st.line_chart(
        year_monthly_order_2018, 
        x="month", 
        y="total_order", 
        color=colors
    )

st.markdown("")
st.subheader('Kinerja Produk berdasarkan Total Pesanan')
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(35, 25))
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
sns.barplot(x="order_count", y="category_name", data=order_sales_items_df.head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Number of Order", fontsize=35)
ax[0].set_title("5 Category from Top by Order", loc="center", fontsize=50)
ax[0].tick_params(axis='y', labelsize=35)
ax[0].tick_params(axis='x', labelsize=30)

sns.barplot(x="order_count", y="category_name", data=order_sales_items_df.sort_values(by="order_count", ascending=True).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Number of Order", fontsize=35)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("5 Category from Bottom by Order", loc="center", fontsize=50)
ax[1].tick_params(axis='y', labelsize=35)
ax[1].tick_params(axis='x', labelsize=35)

st.pyplot(fig)

st.markdown("")
st.subheader('Demografi Pelanggan')
fig, ax = plt.subplots(figsize=(20, 10))
colors = ["#90CAF9", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
sns.barplot(
    x="num_of_customer", 
    y="region",
    data=byregion_df.sort_values(by="num_of_customer", ascending=False),
    palette=colors,
    ax=ax
)
ax.set_title("Number of Customer by Region", loc="center", fontsize=30)
ax.set_ylabel(None)
ax.set_xlabel("customer_count", fontsize=25)
ax.tick_params(axis='y', labelsize=25)
ax.tick_params(axis='x', labelsize=20)

st.pyplot(fig)

st.markdown("")
st.subheader('Transaksi Customer berdasarkan Jenis Pembayaran')
fig, ax = plt.subplots(figsize=(14, 6))
labels = pay_type_byregion_df['payment_type']
ax.pie(pay_type_byregion_df['num_of_order'], labels=labels, autopct='%1.1f%%')
ax.axis('equal')

st.pyplot(fig)

# st.markdown("")
# st.subheader('Distribusi Penjual berdasarkan Negara Bagian')
# fig, ax = plt.subplots(figsize=(10, 6))
# seller_df = pd.read_csv("C:/Users/Umaru/Documents/ya/data/olist_sellers_dataset.csv")
# sns.countplot(data=seller_df, x='seller_state', order=seller_df['seller_state'].value_counts().index)
# ax.set_xlabel("State", fontsize=12)
# ax.set_ylabel("Number of Sellers", fontsize=12)
# ax.tick_params(axis='x', labelrotation=90)
# st.pyplot(fig)

st.markdown("")
st.subheader('Alasan Utama Ulasan Negatif')
plt.figure(figsize=(10, 6))
# Memuat data alasan-alasan utama ulasan negatif
top_negative_reasons = pd.DataFrame({
    'reason': ['Tidak direkomendasikan', 'Buruk', 'Tidak direkomendasikan', 'Produk salah', 'Belum menerima produk', 'Produk cacat', 'Produk tidak terkirim', 'Mengerikan',  'Mengerikan', 'Belum menerima'],
    'count': [50, 45, 40, 35, 33, 30, 30, 15, 14, 13]
})
# Menampilkan grafik untuk alasan-alasan utama ulasan negatif
sns.barplot(data=top_negative_reasons, x='reason', y='count', color='coral')
plt.title('Top Reasons for Negative Reviews')
plt.xlabel('Reason')
plt.ylabel('Number of Reviews')
plt.xticks(rotation=45)
st.pyplot(plt)

# Memuat data kategori produk yang telah diterjemahkan
product_category_translation_df = pd.read_csv("C:/Users/Umaru/Documents/ya/data/product_category_name_translation.csv")

# Menampilkan grafik untuk distribusi kategori berdasarkan terjemahan
st.markdown("")
st.subheader('Distribusi Kategori Berdasarkan Translasi')
plt.figure(figsize=(10, 6))
sns.countplot(data=product_category_translation_df, y='product_category_name', order=product_category_translation_df['product_category_name'].value_counts().index)
plt.title('Distribution of Categories by Translation')
plt.xlabel('Number of Categories')
plt.ylabel('Category')
st.pyplot(plt)

st.markdown("")
st.markdown("Copyright (c) - Created by Umaru90 - 2024")
