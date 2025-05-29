import streamlit as st
import pandas as pd
import smtplib
from io import BytesIO
from datetime import datetime
from email.message import EmailMessage
st.title("🧾 Bank Reconciliation Tool")

# Upload internal and bank CSV files
internal_file = st.file_uploader("Upload Internal Transactions File", type="csv")
bank_file = st.file_uploader("Upload Bank Transactions File", type="csv")

def reconcile_data(internal_df, bank_df):
    merged = pd.merge(internal_df, bank_df, on="transaction_id", how="outer", suffixes=('_int', '_bank'))

    def get_status(row):
        if pd.isna(row['amount_int']) or pd.isna(row['amount_bank']):
            return 'Missing Transaction'
        elif row['amount_int'] == row['amount_bank']:
            return 'Matched'
        else:
            return 'Amount Mismatch'

    merged['status'] = merged.apply(get_status, axis=1)
    return merged

if internal_file and bank_file:
    internal_df = pd.read_csv(internal_file)
    bank_df = pd.read_csv(bank_file)

    st.success("✅ Files uploaded successfully!")
    
    # Run reconciliation
    result_df = reconcile_data(internal_df, bank_df)

    st.subheader("🔍 Reconciliation Results")
    st.dataframe(result_df)

    # Download link
    def to_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        return output.getvalue()

    st.download_button(
        label="📥 Download Report as Excel",
        data=to_excel(result_df),
        file_name=f"reconciliation_report_{datetime.now().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


def send_email_report(to_email, subject, body, attachment_bytes, filename):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = "your_email@gmail.com"
    msg['To'] = to_email
    msg.set_content(body)
    
    msg.add_attachment(attachment_bytes, maintype='application', subtype='vnd.openxmlformats-officedocument.spreadsheetml.sheet', filename=filename)
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login("asfournazik4@gmail.com", "nazik123")
        smtp.send_message(msg)


# Input fields (must be placed outside the button logic)
to = st.text_input("Enter recipient email")

# Show the button AFTER the input
if st.button("📤 Send Report by Email"):
    if to:
        send_email_report(
            to,
            "Reconciliation Report",
            "Attached is your reconciliation report.",
            to_excel(result_df),
            "report.xlsx"
        )
        st.success("✅ Email sent successfully!")
    else:
        st.warning("⚠️ Please enter a valid email address.")

