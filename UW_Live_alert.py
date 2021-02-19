import requests
import json
import websocket
import time
from datetime import datetime
import webbrowser as wb
try:
    import thread
except ImportError:
    import _thread as thread


def validateAlert(alert):
    if (float(alert['implied_volatility']) <= 4.0 
        and ((float(alert['volume'])/float(alert['open_interest']) >= 5.0))
        and ((float(alert['ask'])-float(alert['bid']))<=0.15)
        and (((float(alert['strike_price'])/float(alert['stock_price']) >= 1.05) and alert['option_type'] == 'call')
            or ((float(alert['strike_price'])/float(alert['stock_price']) <= 0.90) and alert['option_type'] == 'put'))
        and (datetime.strptime(alert['expires_at'], '%Y-%m-%d').date() - datetime.strptime(alert['timestamp'], '%Y-%m-%dT%H:%M:%SZ').date()).days <= 60
        ):
        return True
    else:
        return False

def processMessage(message):
    event = message['event']
    if (event == "new_msg"):
        alert = message['payload']['data']
        if validateAlert(alert):
            wb.open('https://unusualwhales.com/alerts/'+alert['id'], new=2)
            print("Valid Alert: ")
            print('Ticker: '+ alert['ticker_symbol']+' Option: '+alert['option_symbol']+' Tags: '+ ' '.join([str(elem) for elem in alert['tags']]) +' TimeStamp: '+alert['timestamp']+ ' Link: ' +'https://unusualwhales.com/alerts/'+alert['id']+'\n')
            print("Details: \n", json.dumps(alert, indent=4, sort_keys=True), "\n")
        else:
            print("Not valid alert: \n", json.dumps(alert, indent=4, sort_keys=True), "\n")
    elif ((int(message['ref'])-1)%20 == 0):
        print(f"Connected since: {int((int(message['ref'])-1)/2)} min")
         

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36', 'origin': 'https://unusualwhales.com', 'referer': 'https://unusualwhales.com/'}

s = requests.session()

## enter login info below, or make your own py and reference your login info
user = input("User email: ")
password = input("Password: ")

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

session = login_req.json()

token = session['session']['token']

def on_message(ws, message):
    processMessage(json.loads(message))

def on_error(ws, error):
    err = error
    print("Error: ",err)

def on_close(ws):
    now = datetime.now()
    print("Closing at: ", now)
    print("### closed ###")

def on_open(ws):
    def run(*args):
        channel = json.dumps({
            "event": "phx_join",
            "payload": {},
            "ref": "",
            "topic": "alert_results"
        })
        count = 1
        channel = json.dumps({
            "event": "phx_join",
            "payload": {},
            "ref": f"{count}",
            "topic": "alert_results"})
        ws.send(channel)
        
        while True:
            count += 1
            channel = json.dumps({
                "event": "heartbeat",
                "payload": {},
                "ref": f"{count}",
                "topic": "phoenix"})
            ws.send(channel)
            time.sleep(30)
        ws.close()
        print("thread terminating...")
    thread.start_new_thread(run, ())


if __name__ == "__main__":
    #websocket.enableTrace(True)
    ws = websocket.WebSocketApp(f"wss://ws.unusualwhales.com/socket/websocket?token={token}",
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close)
    ws.on_open = on_open
    ws.run_forever()