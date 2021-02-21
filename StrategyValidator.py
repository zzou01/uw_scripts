from datetime import datetime

def chooseYourStrategy():
    choice = input("\nChoose one of following stategies: \n"+ 
                    "1- OptimizedOne: IV<=4 | vol_oi>=5 | bid-ask spread <=vega | call with 5%diff or put with 10%diff | expiry <=60 days \n")
    return choice


def validateAlert(alert, choice):
    if (choice == "1") :
        return validateOptimizedOne(alert)
    else :
        return False;


def validateOptimizedOne(alert):
    if (float(alert['implied_volatility']) <= 4.0 
        and ((float(alert['volume'])/float(alert['open_interest']) >= 5.0))
        and ((float(alert['ask'])-float(alert['bid']))<=float(alert['vega']))
        and (((float(alert['strike_price'])/float(alert['stock_price']) >= 1.05) and alert['option_type'] == 'call')
            or ((float(alert['strike_price'])/float(alert['stock_price']) <= 0.90) and alert['option_type'] == 'put'))
        and (datetime.strptime(alert['expires_at'], '%Y-%m-%d').date() - datetime.strptime(alert['timestamp'], '%Y-%m-%dT%H:%M:%SZ').date()).days <= 60
        ):
        return True
    else:
        return False
