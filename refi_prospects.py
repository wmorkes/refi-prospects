import streamlit as st
import pandas as pd
from datetime import datetime

st.title("🏠 ReFi / Sale Prospects Analyzer")
st.write("Upload the latest **PropertyLoans.csv** file")

uploaded_file = st.file_uploader("Upload PropertyLoans.csv", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    # Improved cleaning
    df['Loan Amount (MM)'] = pd.to_numeric(df['Loan Amount (MM)'], errors='coerce')
    
    # Better date parsing
    df['Loan Maturity Date'] = pd.to_datetime(df['Loan Maturity Date'], 
                                              errors='coerce', 
                                              format='%m/%d/%Y')
    
    today = datetime.today().date()
    
    # Calculate months
    df['Months to Maturity'] = ((df['Loan Maturity Date'].dt.date - today).apply(
        lambda x: x.days / 30.42 if pd.notnull(x) else None)).round(1)
    
    # Filter
    prospects = df[
        (df['Loan Amount (MM)'] > 5) & 
        (df['Months to Maturity'] > 0) & 
        (df['Months to Maturity'] <= 24)
    ].copy()
    
    prospects = prospects.sort_values(by='Months to Maturity')
    
    display_cols = ['Property Name', 'City', 'Owner', 'Loan Amount (MM)', 
                    'Loan Maturity Date', 'Months to Maturity', 'Loan Status']
    
    st.success(f"Found {len(prospects)} good prospects")
    
    st.subheader("Top ReFi / Sale Prospects")
    st.dataframe(prospects[display_cols], use_container_width=True)
    
    # Download
    csv = prospects[display_cols].to_csv(index=False)
    st.download_button(
        label="📥 Download Prospects as CSV",
        data=csv,
        file_name=f"refi_prospects_{datetime.today().strftime('%Y-%m-%d')}.csv",
        mime="text/csv"
    )
    
    # Formatted list
    st.subheader("Formatted List (Copy-Paste)")
    for _, row in prospects.iterrows():
        mat_date = row['Loan Maturity Date'].strftime('%m/%d/%Y') if pd.notnull(row['Loan Maturity Date']) else "N/A"
        st.write(f"**{row['Property Name']} ({row['City']}):** {row['Owner']}, "
                 f"${row['Loan Amount (MM)']:.2f}M, {row['Months to Maturity']} months "
                 f"({mat_date})")

else:
    st.info("👆 Upload the PropertyLoans.csv file")