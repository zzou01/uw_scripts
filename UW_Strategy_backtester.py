import requests
from datetime import datetime

##__Utility Functions_________________________
def getDate(Start):
    if Start:
        date = input("Enter Start Date in format YYYY-MM-DD: ")
        try:
            return int(datetime.timestamp(datetime.strptime(date,"%Y-%m-%d"))*1000)
        except:
            print("Wrong entry please try again!")
            return getDate(True)
    else:
        date = input("Enter End Date in format YYYY-MM-DD: ")
        try:
            return int(datetime.timestamp(datetime.strptime(date,"%Y-%m-%d"))*1000)
        except:
            print("Wrong entry please try again!")
            return getDate(False)

###___________________________________________

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

## enter login info below
user = input("User email: ")
password = input("Password: ")

start_date = getDate(True)
end_date = getDate(False)

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

datajson = []

print("\n\nStarting Back Test at: ", datetime.now())
page = 0
count = 0
total_count = 0
count_10 = 0
count_20 = 0
count_30 = 0
count_0_10 = 0

while True:
    offset = page * 100
    data = s.get(f'https://phx.unusualwhales.com/api/option_quotes?offset={offset}&sort=timestamp&search=&sector=&tag=&end_date={end_date}&start_date={start_date}&expiry_start_date=1592179200000&expiry_end_date=1686787200000&min_ask=0&max_ask=25&volume_direction=desc&expiry_direction=desc&alerted_direction=desc&oi_direction=desc&normal=true', headers=APIHEADERS)
    alerts = data.json()
    if len(alerts) == 0:
            break
    total_count += len(alerts)
    for alert in alerts:
            if validateAlert(alert):
                max_return = float(alert['max_ask'])/float(alert['ask'])
                max_return = (max_return - 1.0) * 100
                count += 1
                if max_return >= 10 : count_10 +=1
                if max_return >= 20 : count_20 +=1
                if max_return >= 30 : count_30 +=1
                if max_return > 0.0 and max_return <= 10 : count_0_10 +=1
    page += 1

#Print results
print("RESULTS:___________________________________________________")
per = format((count/total_count) * 100, '.2f')
print(f'Valid Alerts: {count} represents: {per}% of {total_count} alerts verified')
per_10 = format((count_10/count) * 100, '.2f')
print(f'Nbr alert with 10% return: {count_10} represents: {per_10}%')
per_20 = format((count_20/count) * 100, '.2f')
print(f'Nbr alert with 20% return: {count_20} represents: {per_20}%')
per_30 = format((count_30/count) * 100, '.2f')
print(f'Nbr alert with 30% return: {count_30} represents: {per_30}%')
per_0_10 = format((count_0_10/count) * 100, '.2f')
print(f'Nbr alert with 0-10% return: {count_0_10} represents: {per_0_10}%')
count0 = count - count_0_10 - count_10
per0 = format((count0/count) * 100, '.2f')
print(f'Nbr alert with negative return: {count0} represents: {per0}%')
print("__________________________________________________________\n")
print("Ending Back Test at: ", datetime.now())
print("\n\n")