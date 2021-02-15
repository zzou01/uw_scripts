import requests
import webbrowser as wb
from datetime import datetime
import time

##Utility Functions
def getAlertMax(alertQuotes):
    max = float(alertQuotes[0]['ask'])
    for quote in alertQuotes:
        if float(quote['ask']) > max : max = float(quote['ask'])
    return max

###---------------------------------------------

##___Strategy validator_______________________
def validateAlert(alert):
    if (float(alert['implied_volatility']) <= 4.0 
        and ((float(alert['volume'])/float(alert['open_interest']) >= 5.0))
        and ((float(alert['ask'])-float(alert['bid']))<=0.15)
        and ((float(alert['strike_price'])/float(alert['stock_price']) >= 1.05) and alert['option_type'] == 'call')
        and (datetime.strptime(alert['expires_at'], '%Y-%m-%d').date() - datetime.strptime(alert['timestamp'], '%Y-%m-%dT%H:%M:%SZ').date()).days <= 60
        ):
        return True
    else:
        return False

###__________________________________________


HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36', 'origin': 'https://unusualwhales.com', 'referer': 'https://unusualwhales.com/'}

s = requests.session()

## enter login info below, or make your own py and reference your login info
user = input("User email: ")
password = input("Password: ")
frequency = int(input("frequency check in minutes: "))

login_payload = {
		'email': '',
		'password': '',
		}
login_payload['email'] = user
login_payload['password'] = password

login_req = s.post('https://phx.unusualwhales.com/api/users/login', headers=HEADERS, data=login_payload)

if login_req.status_code != 200:
    print("Login error: ",login_req.status_code, " : Check your credentials!")
    exit()

now = datetime.now()

session = login_req.json()

token = session['session']['token']

APIHEADERS = {'Content-Type': 'application/json','Authorization': '', 'Accept': 'application/json'}

APIHEADERS['Authorization'] = 'Bearer ' + token

firstcall = True

datajson = []
while True:
    print("Starting verification at: ", datetime.now())
    page = 0
    count = 0
    total_count = 0
    start_date = (int(datetime.timestamp(datetime.today())*1000)-(frequency * 60 * 1000)) if firstcall else end_date
    end_date = int(datetime.timestamp(datetime.now())*1000)
    while True:
        offset = page * 100
        data = s.get(f'https://phx.unusualwhales.com/api/option_quotes?offset={offset}&sort=timestamp&search=&sector=&tag=&end_date={end_date}&start_date={start_date}&expiry_start_date=1592179200000&expiry_end_date=1686787200000&min_ask=0&max_ask=25&volume_direction=desc&expiry_direction=desc&alerted_direction=desc&oi_direction=desc&normal=true', headers=APIHEADERS)
        alerts = data.json()
        if len(alerts) == 0:
                break
        total_count += len(alerts)
        for alert in alerts:
                if validateAlert(alert):
                    wb.open('https://unusualwhales.com/alerts/'+alert['id'], new=2)
                    print('Ticker: '+ alert['ticker_symbol']+' Option: '+alert['option_symbol']+f' Max Return: {max_return}' +' Tags: '+ ' '.join([str(elem) for elem in alert['tags']]) +' TimeStamp: '+alert['timestamp']+ ' Link: ' +'https://unusualwhales.com/alerts/'+alert['id']+'\n')
                    count += 1
        page += 1

    print(f'\nValid alerts: {count}')
    print(f'Alerts verified: {total_count}')
    print("Ending verification at: ", datetime.now())
    print(f'\nTo exit hit Ctrl+c \nWaiting for {frequency} minute(s) ...\n')
    time.sleep(60*frequency)
    firstcall = False