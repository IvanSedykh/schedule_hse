from convert import convert
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os.path
import pickle
import requests
import datetime
import urllib3


urllib3.disable_warnings()

base_url = 'https://ruz.hse.ru/api/schedule/'
student_id = 219426

today = datetime.datetime.today()
delta1 = datetime.timedelta(days=4)  # to launch on thursdays
delta2 = datetime.timedelta(days=10)  # to set 1 week interval

start = (today + delta1).strftime('%Y.%m.%d')
finish = (today + delta2).strftime('%Y.%m.%d')

print(start, finish)

link = base_url + 'student/{id}.ics?start={start}&finish={finish}&lng=1'.format(
    id=student_id, start=start, finish=finish)
print(link)

sched = requests.get(link, verify=False)

file_name = './schedule_from{start}_to{finish}.ics'.format(
    start=start, finish=finish)
open(file_name, 'wb').write(sched.content)


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']


def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    events = convert(fname=file_name)
    cal_ID = 'pfpnvfml64gehhn8sn34bacfno@group.calendar.google.com'

    for event in events:
        lect = service.events().insert(calendarId=cal_ID, body=event).execute()
        print('Event created: %s' % (lect.get('htmlLink')))


if __name__ == '__main__':
    main()
