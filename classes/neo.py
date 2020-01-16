import os
import requests
import random
import time

class neo:
    def __init__(self):
        self.s = requests.session()
        self.base = 'http://www.neopets.com/'
        self.useragent = None
        self.minDelay = None
        self.MaxDelay = None
        self.getSettings()
        self.setHeaders()

    def log(self, msg): 
        print(time.strftime('%A') + ' ' + '%s%s'%(time.strftime('%H:%M:%S => '),msg.encode('utf-8').decode('utf-8')))

    def getSettings(self):
        with open('settings/settings.txt', 'r') as f:
            settings = f.read().rstrip()
        bot = self.GetBetween(settings, '[bot]', '[/bot]')
        bot = bot.split('\n')[1:-1]
        self.useragent = bot[0].split(':', 1)[1].strip()
        self.minDelay = float(bot[1].split(':', 1)[1].strip())
        self.MaxDelay = float(bot[2].split(':', 1)[1].strip())

    def setHeaders(self):
        self.s.headers.update({'User-Agent': self.useragent, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-US,en;q=0.9'})

    def proxy(self, prox):
        self.s.proxies.update({'http': 'http://%s' % prox})

    def GetBetween(self, data, first, last):
        return data[data.find(first) + len(first):data.find(last)]

    def url(self, path):
        return '%s%s' % (self.base, path)

    def get(self, path, referer = None, params = None):
        time.sleep(random.uniform(self.minDelay, self.MaxDelay))
        url = self.url(path)
        if referer:
            self.s.headers.update({'Referer': referer})
        if params:
            r = self.s.get(url, params=params)
        else:
            r = self.s.get(url)
        if 'Referer' in self.s.headers:
            del self.s.headers['Referer']
        return r.text

    def post(self, path, data, referer = None):
        time.sleep(random.uniform(self.minDelay, self.MaxDelay))
        if referer:
            self.s.headers.update({'Referer': referer})
        url = self.url(path)
        if data:
            r = self.s.post(url, data=data)
        else:
            r = self.s.post(url)
        return r.text