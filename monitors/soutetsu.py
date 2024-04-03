import json

import requests

from db import TrainStatus
import monitors.monitor


class SoutetsuMonitor(monitors.monitor.TrainMonitor):

    """
    Examples:
        [
{
"DATE": "2024/02/22 08:10:05","MSG": "相鉄線は、大和駅におきまして具合の悪いお客様の救護を行ったため、全線でダイヤ乱れが発生しております。","E_LINE": "Sotetsu Line","E_FROM": "All lines","E_TO": "","E_DIRECTION": "Inbound and outbound lines","E_CAUSE": "Emergency patient assistance","E_STATUS": "Trains not on schedule","IRREGULAR": true,"MSG2": ""
}
]
    """
    def get_status(self) -> monitors.monitor.TrainStatus:
        url = f"https://cdn.sotetsu.co.jp/unkou/dat/train_status1_v2.json"
        page = requests.get(url)
        site_json = json.loads(page.content)
        normal_operations = True if site_json[0]['MSG'] == '現在は平常通り運転しております。' else False
        return TrainStatus(operator=self.operator(),
                           normal_operations=normal_operations,
                           description=site_json[0]['MSG'])

    def operator(self) -> str:
        return '相鉄線'
