# Import the libraries and load the API Keys
import time, logging, os
import pandas as pd
import krakenex
from pykrakenapi import KrakenAPI
import json

api = krakenex.API()
kraken = KrakenAPI(api)

api.load_key('KrakenPass.txt')

# Load config file
with open('config.json', 'r') as file:
    config = json.load(file)

track_ticker = config['ticker_to_track']
trade_ticker = config['ticker_to_trade']
logname = config['my_log_name']


# Set up the logging
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)


logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(levelname)s: %(message)s', 
                    filename=logname, filemode='a')
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s: %(levelname)s: %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

# Create the main script logic
while True:
    logging.info('--------- Start of current 5 minute period ---------')
    logging.info(pd.Timestamp.now())
    
    try:
        BTC_old = float((kraken.get_ticker_information(track_ticker))['b'].iloc[0][0])
    except Exception as e:
        logging.warning('Error obtaining data')

    time.sleep(300)
    
    try:
        BTC_new = float((kraken.get_ticker_information(track_ticker))['b'].iloc[0][0])
    except Exception as e:
        logging.warning('Error obtaining data')
    
    percent = ((BTC_new - BTC_old)*100) / BTC_old
    
    logging.info(f'BTC moved {percent:.2f}% over the last 5 minutes')
    
    if percent >= 5:
        
        try:
            ETH = float((kraken.get_ticker_information(trade_ticker))['a'].iloc[0][0]) + 2 
        except Exception as e:
            logging.warning('Error obtaining data')
        
        try:
            response = kraken.add_standard_order(pair=trade_ticker, type='buy', ordertype='limit', 
                                                 volume='0.007', price=ETH, validate=False)
        except Exception as e:
            logging.warning('Error placing order')
            
        logging.info(f'Order details:\n{response}')
        
        time.sleep(2)
        
        try:
            check_order = kraken.query_orders_info(response['txid'][0])
        except Exception as e:
            logging.warning('Error checking order')
    
        if check_order['status'][0] == 'open' or 'closed':
            logging.info('Order completed sucessfully')
            break
        else:
            logging.info('Order rejected')
            break
    else:
        logging.info('--------- End of current 5 minute period ---------')