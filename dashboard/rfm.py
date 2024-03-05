import pandas as pd
import datetime as dt

# --- Multi-purpose Function ---
def create_rfm_df(df):
    rfm_df_r = df.groupby(by="customer_id", as_index=False).agg({
        "order_purchase_timestamp": "max", #mengambil tanggal order terakhir
        "order_id": "nunique",
        "payment_value": "sum"
    })
    
    last_date = rfm_df_r["order_purchase_timestamp"].max()
    current_date = last_date + dt.timedelta(days=1)
    rfm_df_r["recency"] = rfm_df_r["order_purchase_timestamp"].apply(lambda x: (current_date - x).days)
    
    rfm_df_fm = rfm_df_r.groupby('customer_id').agg(
        frequency=pd.NamedAgg(column='order_id', aggfunc='count'),
        monetary=pd.NamedAgg(column='payment_value', aggfunc='sum')
    ).reset_index()
    
    rfm_df = rfm_df_r.merge(rfm_df_fm, on='customer_id')
    rfm_df['short_id'] = rfm_df['customer_id'].str[29:]
    
    return rfm_df

def create_rfm_df_quantile(df):
    # Periksa tipe data kolom
    print("Data Types:")
    print(df.dtypes)

    # Periksa nilai unik dalam kolom
    print("Unique values in 'recency' column:")
    print(df['recency'].unique())
    print("Unique values in 'frequency' column:")
    print(df['frequency'].unique())
    print("Unique values in 'monetary' column:")
    print(df['monetary'].unique())
    
    # Bersihkan nilai non-numerik dari kolom
    df['recency'] = pd.to_numeric(df['recency'], errors='coerce')
    df['frequency'] = pd.to_numeric(df['frequency'], errors='coerce')
    df['monetary'] = pd.to_numeric(df['monetary'], errors='coerce')
    
    # Hapus baris dengan nilai non-numerik
    df = df.dropna(subset=['recency', 'frequency', 'monetary'])
    
    # Pastikan dataframe tidak memiliki nilai null atau non-numerik lagi
    if df.isnull().values.any():
        print("DataFrame contains null values. Please clean the data before proceeding.")
        return None
    
    # Lakukan perhitungan quantile setelah membersihkan data
    quantiles = df.quantile(q=[0.20, 0.40, 0.60, 0.80])
    quantiles = quantiles.to_dict()

    rfm_df_score = df.copy().astype(float)

    rfm_df_score['recency_quartile'] = rfm_df_score['recency'].apply(RScore, args=('recency', quantiles,))
    rfm_df_score['frequency_quartile'] = rfm_df_score['frequency'].apply(FMScore, args=('frequency', quantiles,))
    rfm_df_score['monetary_quartile'] = rfm_df_score['monetary'].apply(FMScore, args=('monetary', quantiles,))

    rfm_df_output = 'C:/Users/Umaru/Documents/ya/data/main_data_rfm.csv'  # Ubah jalur lengkap

    rfm_df_score.to_csv(rfm_df_output, index=False)

    return rfm_df_score


def RScore(x,p,d):
     if x <= d[p][0.20]:
         return 5
     elif x <= d[p][0.40]:
         return 4
     elif x <= d[p][0.60]:
         return 3
     elif x<=d[p][0.80]:
         return 2
     else:
         return 1


def FMScore(x, p, d):
    if x <= d[p][0.20]:
        return 1
    elif x <= d[p][0.40]:
        return 2
    elif x <= d[p][0.60]:
        return 3
    elif x<=d[p][0.80]:
        return 4
    else:
        return 5


def customer_segment(df):
    label = {
        r'111|112|121|131|141|151': 'Lost customers',
        r'332|322|233|232|223|222|132|123|122|212|211': 'Hibernating customers',
        r'155|154|144|214|215|115|114|113': 'Cannot Lose Them',
        r'255|254|245|244|253|252|243|242|235|234|225|224|153|152|145|143|142|135|134|133|125|124': 'At Risk',
        r'331|321|312|221|213|231|241|251': 'About To Sleep',
        r'535|534|443|434|343|334|325|324': 'Need Attention',
        r'525|524|523|522|521|515|514|513|425|424|413|414|415|315|314|313': 'Promising',
        r'512|511|422|421|412|411|311': 'New Customers',
        r'553|551|552|541|542|533|532|531|452|451|442|441|431|453|433|432|423|353|352|351|342|341|333|323': 'Potential Loyalist',
        r'543|444|435|355|354|345|344|335': 'Loyal',
        r'555|554|544|545|454|455|445': 'Champions'
    }
    # Copy existing dataFrame into new dataFrame
    df_cp = df.copy()
    # Replace all instances of RFM score
    df_cp['segments'] = df_cp['rfm_score'].replace(label, regex=True)
    # Count all instrument in segments column
    df_cp['segments'].value_counts()
    
    return df_cp
    
def create_rfm_segment_distribution(df):
    rfm_segment_count = df[["segments", "recency", "frequency", "monetary"]].groupby("segments").agg(['count'])
    rfm_segment_count["percentage"] = (100 * rfm_segment_count['recency']["count"]/rfm_segment_count['recency']["count"].sum()).round(2)  
    rfm_segment_count.reset_index()
    
    return rfm_segment_count
