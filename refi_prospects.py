import streamlit as st
import pandas as pd
from datetime import datetime

st.title("🏠 ReFi / Sale Prospects Analyzer")

st.markdown("""
**How to use (2 simple steps):**
1. Open your PropertyLoans file in Excel
2. File → Save As → Choose **CSV UTF-8** → Save
3. Drag the .csv file here
""")

uploaded_file = st.file_uploader("Upload PropertyLoans.csv", type=["csv"])

if uploaded_file is not None:
    # Robust reading with multiple encoding fallbacks
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8')
    except:
        try:
            df = pd.read_csv(uploaded_file, encoding='latin1')
        except:
            df = pd.read_csv(uploaded_file, encoding='cp1252')
    
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
    
    st.subheader("Formatted List by Owner")
    output_text = ""
    for owner, group in prospects.groupby('Owner'):
        st.write(f"**{owner}**")
        output_text += f"**{owner}**\n"
        for _, row in group.sort_values('Loan Maturity Date').iterrows():
            date_str = row['Loan Maturity Date'].strftime('%m/%d/%Y') if pd.notnull(row['Loan Maturity Date']) else "N/A"
            line = f"• {row['Property Name']} ({row.get('City', '')}): ${row['Loan Amount (MM)']:.2f}M, {row['Months to Maturity']} months ({date_str})"
            st.write(line)
            output_text += line + "\n"
        output_text += "\n"
    
    st.text_area("Copy this list:", output_text, height=500)
    
    csv = prospects.to_csv(index=False)
    st.download_button("📥 Download as CSV", csv, f"prospects_{today.strftime('%Y-%m-%d')}.csv", "text/csv")

else:
    st.info("👆 Upload the CSV file after saving from Excel as 'CSV UTF-8'")
