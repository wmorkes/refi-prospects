import streamlit as st
import pandas as pd
from datetime import datetime

st.title("🏠 ReFi / Sale Prospects Analyzer")
st.write("Upload **PropertyLoans.xlsx** (preferred) or .csv")

uploaded_file = st.file_uploader("Drag & drop your file", type=["xlsx", "xls", "csv"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.lower().endswith(('.xlsx', '.xls')):
            df = pd.read_excel(uploaded_file, engine='openpyxl')
        else:
            df = pd.read_csv(uploaded_file, encoding='utf-8')
    except Exception as e:
        try:
            # Fallbacks
            if uploaded_file.name.lower().endswith(('.xlsx', '.xls')):
                df = pd.read_excel(uploaded_file)
            else:
                df = pd.read_csv(uploaded_file, encoding='latin1')
        except:
            st.error("Could not read the file. Please save as CSV and try again.")
            st.stop()
    
    # Data cleaning
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
                           'Loan Maturity Date', 'Months to Maturity']], use_container_width=True)
    
    st.subheader("✅ Formatted List by Owner (Copy-Paste Ready)")
    
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
    
    st.text_area("Copy the entire list below:", output_text, height=400)
    
    csv = prospects.to_csv(index=False)
    st.download_button("📥 Download Prospects as CSV", csv, 
                       f"refi_prospects_{today.strftime('%Y-%m-%d')}.csv", "text/csv")

else:
    st.info("👆 Upload your PropertyLoans file (Excel preferred)")
