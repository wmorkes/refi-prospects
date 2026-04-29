import streamlit as st
import pandas as pd
from datetime import datetime

st.title("🏠 ReFi / Sale Prospects Analyzer")
st.write("Upload the latest **PropertyLoans.csv** file")

uploaded_file = st.file_uploader("Upload PropertyLoans.csv", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    # Clean and prepare data
    df['Loan Amount (MM)'] = pd.to_numeric(df['Loan Amount (MM)'], errors='coerce')
    df['Loan Maturity Date'] = pd.to_datetime(df['Loan Maturity Date'], errors='coerce')
    
    today = datetime.today()
    
    # Calculate months to maturity
    df['Months to Maturity'] = ((df['Loan Maturity Date'] - today).dt.days / 30.42).round(1)
    
    # Filter good prospects
    prospects = df[
        (df['Loan Amount (MM)'] > 5) & 
        (df['Months to Maturity'] > 0) & 
        (df['Months to Maturity'] <= 24)
    ].copy()
    
    # Sort by maturity (soonest first)
    prospects = prospects.sort_values(by='Months to Maturity')
    
    # Select key columns
    display_cols = ['Property Name', 'City', 'Owner', 'Loan Amount (MM)', 
                    'Loan Maturity Date', 'Months to Maturity', 'Loan Status']
    
    st.success(f"Found {len(prospects)} good prospects")
    
    # Display clean table
    st.subheader("Top ReFi / Sale Prospects")
    st.dataframe(prospects[display_cols], use_container_width=True)
    
    # Download button
    csv = prospects[display_cols].to_csv(index=False)
    st.download_button(
        label="📥 Download Prospects as CSV",
        data=csv,
        file_name=f"refi_prospects_{today.strftime('%Y-%m-%d')}.csv",
        mime="text/csv"
    )
    
    # Simple formatted list for quick copy
    st.subheader("Formatted List (Copy-Paste)")
    for _, row in prospects.iterrows():
        st.write(f"**{row['Property Name']} ({row['City']}):** {row['Owner']}, "
                 f"${row['Loan Amount (MM)']}M, {row['Months to Maturity']} months "
                 f"({row['Loan Maturity Date'].date()})")

else:
    st.info("👆 Upload the PropertyLoans.csv file to generate the list")