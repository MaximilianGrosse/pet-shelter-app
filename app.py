import streamlit as st
import gspread
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

# Define the required scopes
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive.readonly"
]

# Load service account credentials
creds = Credentials.from_service_account_file('credentials.json', scopes=SCOPES)

# Authorize with gspread
gc = gspread.authorize(creds)

# ---- Google Sheet IDs ----
sheet_ids = {
    'Pets': '1Y-BZPULn4PK9qNaR_2mRTXod6IlUfmXUNb6UIwzbsh4',
    'Adopters': '158Q5MLKoMzXm8EmTQeaMcD75EPzm7WrqOKeTBMpLXv8',
    'Shelters': '1zyIx53JlA9ljWbFEv7Nfpk0o69wKYhBB8ut8HZIqdLs'
}

# ---- Streamlit Interface ----
st.title("🐾 Pet Shelter Web App")

# Read and display data from each sheet
for sheet_name, sheet_id in sheet_ids.items():
    st.header(f"{sheet_name} Sheet Data")
    try:
        worksheet = gc.open_by_key(sheet_id).sheet1
        data = worksheet.get_all_records()
        st.dataframe(data)
    except Exception as e:
        st.error(f"Error reading {sheet_name} sheet: {e}")

# ---- Google Drive API ----
drive_service = build('drive', 'v3', credentials=creds)

# PetImages folder ID
folder_id = '1Mmru8EOhgGva_JzUdAHOJhTXqDEtRRY4'

# List image files in the folder
try:
    query = f"'{folder_id}' in parents and mimeType contains 'image/' and trashed = false"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    items = results.get('files', [])

    st.header("📸 Pet Images from Google Drive")
    if not items:
        st.write("No images found.")
    else:
        for item in items:
            image_url = f"https://drive.google.com/uc?id={item['id']}"
            st.image(image_url, caption=item['name'], width=200)

except Exception as e:
    st.error(f"Error retrieving images from Drive: {e}")
