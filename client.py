from classes.neo import neo
import sys
import re
import random
import time
import datetime
import json

class client:
    def __init__(self):
        self.neo = neo()

    def doLogin(self):
        with open('settings/settings.txt', 'r') as f:
            settings = f.read().rstrip()
        account = self.neo.GetBetween(settings, '[account]', '[/account]')
        account = account.split('\n')[1:-1]
        username = account[0].split(';')[1].strip()
        password = account[1].split(';')[1].strip()
        proxy = account[2].split(';')[1].strip()
        if proxy != 'ip:port':
            self.neo.proxy(proxy)
        resp = self.neo.post('login.phtml', {'destination': '', 'username': username, 'password': password}, 'http://www.neopets.com/login/')
        if resp.find('id=\'npanchor\'') > 1:
            self.neo.log('Logged in as %s' % username)
            return True
        else:
            input('Unable to login as %s. Press enter to exit..' % username)
            return False

    def depositInventory(self):
        arr = 1
        resp = self.neo.get('quickstock.phtml')
        items = "<TD align=\"left\">"
        results = resp.count(items)
        if results:
            item_ids = re.findall('value="(.*)"><TD', resp)
            data = {}
            data['buyitem'] = 0
            for item in item_ids:
                data['id_arr[%s]' % arr] = item
                data['radio_arr[%s]' % arr] = 'deposit'
                arr += 1
            data['checkall'] = 'on'
            self.neo.post('process_quickstock.phtml', data, 'http://www.neopets.com/quickstock.phtml')
        if results:
            self.neo.log('Deposited %s items to your SDB' % results)
        else:
            self.neo.log('You don\'t have any items to deposit')

    def wiz(self):
        self.depositInventory()
        while True:
            with open('snipe.txt', 'r') as f:
                for data in f:
                    SnipeData = data.strip().split(':')
                    params = {'q': SnipeData[0],'priceOnly': 0,'context': 0,'partial': 0,'min_price': '','max_price': SnipeData[1], 'lang': 'en','json': 1}
                    resp = self.neo.get('shops/ssw/ssw_query.php?', 'http://www.neopets.com/', params)
                    if resp.find('No items found.') > 1:
                        self.neo.log('Unable to find %s' % SnipeData[0])
                    if resp.find('<br><b>Whoa there') > 1:
                        delta = datetime.timedelta(hours=1)
                        now = datetime.datetime.now()
                        next_hour = (now + delta).replace(microsecond=0, second=30, minute=1)
                        wait_seconds = (next_hour - now).seconds
                        self.neo.log('Banned from the SSW, paused for %s seconds..' % wait_seconds)
                        time.sleep(wait_seconds)
                    if resp.find('links') > 1:
                        jsonData = json.loads(resp)
                        price = jsonData['data']['prices'][0]
                        buy_link = jsonData['data']['links'][0]
                        self.neo.log('Found %s for %s NP, attempting to buy it..' % (SnipeData[0], price))
                        result = self.neo.GetBetween(buy_link, 'href=\'/', '\' target=')
                        resp = self.neo.get(result)
                        results = self.neo.GetBetween(resp, '"top"><A href="', '" onClick=')
                        resp = self.neo.get(results, 'http://www.neopets.com/%s' % result)
                        if resp.find('do not have enough Neopoints') > 1:
                            self.neo.log('You do not have enough Neopoints to purchase this item!')
                        if resp.find('do not have enough Neopoints') < 0:
                            self.neo.log('Successfully brought %s for %s NP!' % (SnipeData[0], price))

    def doBot(self):
        isLogged = self.doLogin()
        if isLogged:
            self.wiz()
        if not isLogged:
            sys.exit()

if __name__ == '__main__':
    a = client()
    a.doBot()
    