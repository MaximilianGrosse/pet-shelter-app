import streamlit as st
import pandas as pd
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError

# ---- AUTH ----
creds_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
creds = service_account.Credentials.from_service_account_info(creds_dict)
sheets_service = build('sheets', 'v4', credentials=creds)
drive_service = build('drive', 'v3', credentials=creds)

# ---- CONFIG ----
SHEET_ID = 'YOUR_GOOGLE_SHEET_ID'  # Replace with your actual sheet ID
DRIVE_FOLDER_ID = 'YOUR_GOOGLE_DRIVE_FOLDER_ID'  # Replace with your Drive folder ID

st.title("🐾 Pet Shelter Web App")

# ---- FUNCTIONS ----
def read_sheet(sheet_name):
    try:
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=SHEET_ID,
            range=sheet_name
        ).execute()
        data = result.get('values', [])
        if not data:
            return pd.DataFrame()
        return pd.DataFrame(data[1:], columns=data[0])
    except HttpError as error:
        st.error(f"Error reading {sheet_name} sheet: {error}")
        return pd.DataFrame()

def list_drive_images(folder_id):
    try:
        results = drive_service.files().list(
            q=f"'{folder_id}' in parents and mimeType contains 'image/' and trashed = false",
            fields="files(id, name, thumbnailLink)"
        ).execute()
        return results.get('files', [])
    except HttpError as error:
        st.error(f"Error retrieving images from Drive: {error}")
        return []

# ---- LOAD DATA ----
st.header("Pets Sheet Data")
pets_df = read_sheet("Pets")
st.dataframe(pets_df)

st.header("Adopters Sheet Data")
adopters_df = read_sheet("Adopters")
st.dataframe(adopters_df)

st.header("Shelters Sheet Data")
shelters_df = read_sheet("Shelters")
st.dataframe(shelters_df)

st.header("🐶 Pet Images from Drive")
images = list_drive_images(DRIVE_FOLDER_ID)

if images:
    for image in images:
        st.image(image["thumbnailLink"], caption=image["name"], width=150)
else:
    st.write("No images found in the Drive folder.")
