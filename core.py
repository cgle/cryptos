import kucoin.client
import ujson
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
config_path = os.path.join(dir_path, 'keys.config')
start_balance_path = os.path.join(dir_path, 'balance.config')

class BotBase(object):

    default_currency = 'USD'

    def __init__(self):
        self.config = ujson.loads(open(config_path, 'r').read())
        self.start_balance = ujson.loads(open(start_balance_path, 'r').read())

        self.client = kucoin.client.Client(
            self.config['kucoin']['key'], 
            self.config['kucoin']['secret']
        )

        #self.client.set_default_currency(self.default_currency)

    def pnl(self):
        start_currencies = self.start_balance.keys()
        currencies = self.client.get_currencies(list(start_currencies))
        
        start_balance = 0
        for k,v in self.start_balance.items():
            start_balance += v * currencies['rates'][k]['USD']

        coins = self.client.get_trading_symbols()
        coins_btc = {c['coinType']:c for c in coins if c['coinTypePair'] == 'BTC'}

        current_assets = self.client.get_all_balances()
        current_balance = 0
        for asset in current_assets:
            if asset['balance'] <= 0:
                continue
            coinType = asset['coinType']
            cvp = 1 if coinType == 'BTC' else coins_btc[coinType]['lastDealPrice']
            current_balance += (asset['balance'] + asset['freezeBalance']) * cvp * currencies['rates']['BTC']['USD']

        pnl =  current_balance - start_balance

        print('START', start_balance)
        print('CURRENT', current_balance)
        print('PNL', pnl)
        return pnl
