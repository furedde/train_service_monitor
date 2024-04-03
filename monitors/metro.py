import requests

from db import TrainStatus
from bs4 import BeautifulSoup
import monitors.monitor

class MetroMonitor(monitors.monitor.TrainMonitor):
    def get_status(self) -> TrainStatus:
        url = f"https://www.tokyometro.jp/lang_en/unkou/history/chiyoda.html"
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        results = soup.find(name='div', attrs={'class': 'v2_unkouRouteUnkou'})
        status = None
        for el_li in results.findAll(name='li'):
            text = el_li.text
            text = text.lstrip('\n').rstrip('\n')
            line = text.split('\n')[0]
            status = " ".join(text.split('\n')[2:])
            if line == self._operator:
                if status == '平常運転':
                    return TrainStatus(operator=self.operator(),
                                       normal_operations=True,
                                       description=status)
                else:
                    return TrainStatus(operator=line,
                                       normal_operations=False,
                                       description=status)

    def operator(self) -> str:
        return self._operator

    def __init__(self, operator):
        self._operator = operator
