import streamlit as st
import pandas as pd
from datetime import datetime

st.title("🏠 ReFi / Sale Prospects Analyzer")
st.write("Upload the latest **PropertyLoans.csv** file")

uploaded_file = st.file_uploader("Upload PropertyLoans.csv", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    df['Loan Amount (MM)'] = pd.to_numeric(df['Loan Amount (MM)'], errors='coerce')
    df['Loan Maturity Date'] = pd.to_datetime(df['Loan Maturity Date'], errors='coerce')
    
    today = datetime.today()
    df['Months to Maturity'] = ((df['Loan Maturity Date'] - today).dt.days / 30.42).round(1)
    
    prospects = df[
        (df['Loan Amount (MM)'] > 5) & 
        (df['Months to Maturity'] > 0) & 
        (df['Months to Maturity'] <= 24)
    ].copy()
    
    prospects = prospects.sort_values(by=['Owner', 'Loan Maturity Date'])
    
    st.success(f"Found **{len(prospects)}** good prospects")
    
    st.subheader("Top Prospects")
    st.dataframe(prospects[['Property Name', 'City', 'Owner', 'Loan Amount (MM)', 
                           'Loan Maturity Date', 'Months to Maturity']], 
                 use_container_width=True)
    
    # Grouped Formatted List
    st.subheader("✅ Formatted List by Owner (Copy-Paste Ready)")
    
    output_text = ""
    for owner, group in prospects.groupby('Owner'):
        st.write(f"**{owner}**")
        output_text += f"**{owner}**\n"
        sorted_group = group.sort_values('Loan Maturity Date')
        for _, row in sorted_group.iterrows():
            date_str = row['Loan Maturity Date'].strftime('%m/%d/%Y') if pd.notnull(row['Loan Maturity Date']) else "N/A"
            line = f"• {row['Property Name']} ({row.get('City', '')}): ${row['Loan Amount (MM)']:.2f}M, {row['Months to Maturity']} months ({date_str})"
            st.write(line)
            output_text += line + "\n"
        output_text += "\n"
    
    # Copy button for formatted text
    st.text_area("Copy the entire list below:", output_text, height=400)
    
    # Download CSV
    csv = prospects.to_csv(index=False)
    st.download_button("📥 Download Full Prospects as CSV", csv, 
                       f"refi_prospects_{today.strftime('%Y-%m-%d')}.csv", "text/csv")

else:
    st.info("👆 Upload your PropertyLoans.csv file")
