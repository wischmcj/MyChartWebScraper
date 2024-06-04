import os.path
import pandas as pd
import os
import pickle

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Health Reports

##/MyChart-prd/inside.asp?mode=fshreport&amp;fshid=103&amp;fromlist=1

# <a href="/MyChart-prd/inside.asp?mode=fshreport&amp;fshid=23&amp;fromlist=1" class="nolinelist">Vitals</a>
# <a href="/MyChart-prd/inside.asp?mode=fshreport&amp;fshid=1400000004&amp;fromlist=1" class="nolinelist">MyChart Peak Flow Flowsheet</a>
# <a href="/MyChart-prd/inside.asp?mode=fshreport&amp;fshid=1400000003&amp;fromlist=1" class="nolinelist">MyChart Weight Flowsheet</a>
# <a href="/MyChart-prd/inside.asp?mode=fshreport&amp;fshid=1400000005&amp;fromlist=1" class="nolinelist">MyChart Exercise Flowsheet</a>
# <a href="/MyChart-prd/inside.asp?mode=fshreport&amp;fshid=1400000006&amp;fromlist=1" class="nolinelist">MyChart CHF Flowsheet</a>
# <a href="/MyChart-prd/inside.asp?mode=fshreport&amp;fshid=1400000001&amp;fromlist=1" class="nolinelist">Glucose Monitoring Device</a>
# <a href="/MyChart-prd/inside.asp?mode=fshreport&amp;fshid=98&amp;fromlist=1" class="nolinelist">MyChart Glucose Monitoring Flowsheet</a>
# <a href="/MyChart-prd/inside.asp?mode=fshreport&amp;fshid=1400000000&amp;fromlist=1" class="nolinelist">Blood Pressure Monitoring Device</a>
# <a href="/MyChart-prd/inside.asp?mode=fshreport&amp;fshid=99&amp;fromlist=1" class="nolinelist">MyChart Blood Pressure Flowsheet</a>
# <a href="/MyChart-prd/inside.asp?mode=fshreport&amp;fshid=21002&amp;fromlist=1" class="nolinelist">Lipids</a>

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = "1t82EC6UBoc11llvrllULYu_iXhpBrJuXqNJzk1ATKEs"
med_range = "MedData!A:F"
dose_range = "DoseData!A:F"
dose_range = "DoseData!A:F"

def main():
  """Shows basic usage of the Sheets API.
  Prints values from a sample spreadsheet.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("sheets", "v4", credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = (
      
        sheet.values()
        .get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME)
        .execute()
    )
    values = result.get("values", [])

    if not values:
      print("No data found.")
      return

    print("Name, Major:")
    for row in values:
      # Print columns A and E, which correspond to indices 0 and 4.
      print(f"{row[0]}, {row[1]}")
  except HttpError as err:
    print(err)


def create_service(client_secret_file, api_service_name, api_version, *scopes):
    global service
    SCOPES = [scope for scope in scopes[0]]
    #print(SCOPES)
    
    cred = None

    if os.path.exists('token_write.pickle'):
        with open('token_write.pickle', 'rb') as token:
            cred = pickle.load(token)

    if not cred or not cred.valid:
        if cred and cred.expired and cred.refresh_token:
            cred.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secret_file, SCOPES)
            cred = flow.run_local_server()

        with open('token_write.pickle', 'wb') as token:
            pickle.dump(cred, token)

    try:
        service = build(api_service_name, api_version, credentials=cred)
        print(api_service_name, 'service created successfully')
        #return service
    except Exception as e:
        print(e)
        #return None
        
# change 'my_json_file.json' by your downloaded JSON file.
    
def gsheets_export(data, sheet_range):
    to_write  = [d.__dict__ for d in data ]
    
    df=pd.DataFrame(to_write)
    # gsheetId ='1hB1J4AzrK70ZNeZjOPMX7zNGq3UZQIYfDnyzyXj5SfM' #dev
    gsheetId = '1t82EC6UBoc11llvrllULYu_iXhpBrJuXqNJzk1ATKEs' #prod
    response_date = service.spreadsheets().values().append(
        spreadsheetId=gsheetId,
        valueInputOption='RAW',
        range=sheet_range,
        body=dict(
            majorDimension='ROWS',
            values=df.values.tolist())
    ).execute()

    print('Sheet successfully Updated')

create_service('credentials.json', 'sheets', 'v4',['https://www.googleapis.com/auth/spreadsheets'])

# if __name__ == "__main__":
#   main()