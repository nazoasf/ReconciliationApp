import pandas as pd
from io import BytesIO
import smtplib
from email.message import EmailMessage

# Load CSV files
df_internal = pd.read_csv("internal.csv")
df_bank = pd.read_csv("bank.csv")

# Reconciliation logic
def reconcile_data(df_internal, df_bank):
    df = pd.merge(df_internal, df_bank, on='transaction_id', how='outer', suffixes=('_int', '_bank'))
    def get_status(row):
        if pd.isna(row['amount_int']):
            return 'Missing in Internal'
        elif pd.isna(row['amount_bank']):
            return 'Missing in Bank'
        elif abs(row['amount_int'] - row['amount_bank']) < 0.01:
            return 'Match'
        else:
            return 'Mismatch'
    df['status'] = df.apply(get_status, axis=1)
    return df

result_df = reconcile_data(df_internal, df_bank)

# Convert to Excel
def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Reconciliation')
    writer.close()
    return output.getvalue()

excel_bytes = to_excel(result_df)

# Send email
def send_email_report(to_email, subject, body, attachment_bytes, filename):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = "your_email@gmail.com"
    msg['To'] = to_email
    msg.set_content(body)
    msg.add_attachment(attachment_bytes, maintype='application', subtype='octet-stream', filename=filename)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login("your_email@gmail.com", "your_app_password")
        smtp.send_message(msg)

send_email_report("receiver_email@gmail.com", "Automated Reconciliation", "See attached.", excel_bytes, "reconciliation.xlsx")
