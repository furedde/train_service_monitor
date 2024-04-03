import requests
from bs4 import BeautifulSoup

from db import TrainStatus
import monitors.monitor


class OdakyuMonitor(monitors.monitor.TrainMonitor):
    def operator(self) -> str:
        return "小田急線"

    def get_status(self) -> TrainStatus:
        url = f"https://www.odakyu.jp/cgi-bin/user/emg/emergency_bbs.pl"
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        status = None

        # snippet on how th epage looked when the code was written
        """
        <main class="main" role="main">
        <div class="headline"></div>
        <div class="center"><div id="pagettl">
        <p class="date" wovn-ignore>2024/02/12 07:08</p>
        <p class="ttl_daiya_blue">小田急線は平常どおり運転しております。</p>
        <div class="update">
        <input type="image" src="/program/emg/img/common/btn_update_off.jpg" OnMouseOver="translateImage(this, '/program/emg/img/common/btn_update_on.jpg')" OnMouseOut="translateImage(this, '/program/emg/img/common/btn_update_off.jpg')" alt="更新" onclick="javascript:location.reload(true)">
        </div></div></div>
        """

        div_center = soup.find(name="div", attrs={'class': 'center'})
        if div_center:
            ps = div_center.findAll(name="p")
            p_class = ps[1]['class']
            p_text = ps[1].text

            if p_text == '小田急線は平常どおり運転しております。':
                status = TrainStatus(operator='小田急線',
                                     normal_operations=True,
                                     description=p_text)
            else:
                status = TrainStatus(operator='小田急線',
                                     normal_operations=False,
                                     description=f"class='{p_class}' text='{p_text}'")

        return status
