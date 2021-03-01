import requests
import time
import os
import re
import json

os.environ['NO_PROXY'] = 'stackoverflow.com'


def loads_jsonp(_jsonp):
    try:
        return json.loads(re.match(".*?({.*}).*", _jsonp, re.S).group(1))
    except:
        raise ValueError('Invalid Input')


headers = {
    "Accept": "text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-TW,zh-CN;q=0.9,zh;q=0.8",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    # "Content-Length":"386", #这个需要注释掉，如果长度不对请求会被视作异常
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Cookie": "st_si=75540904388619; st_asi=delete; ASP.NET_SessionId=nvv1yet2ffaes4z5spbaoziz; qgqp_b_id=b0b95b4559e1a7f67265dd6484550bde; st_pvi=97911961255996; st_sp=2021-02-24%2014%3A23%3A57; st_inirUrl=https%3A%2F%2Fwww.baidu.com%2Flink; st_sn=86; st_psi=20210225145824655-0-2220923406",
    "Host": "fund.eastmoney.com",
    "Pragma": "no-cache",
    "Referer": "http://fund.eastmoney.com/company/default.html",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4168.3 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
}

timestamp = time.time() * 1000
url = 'http://fund.eastmoney.com/Data/FundRankScale.aspx?_=' + str(timestamp)[:13]
proxies = {"http": None, "https": None}
response = requests.get(url, {}, headers=headers, proxies=proxies)

responseText = response.text
jsonOrigin = responseText[16:-1].replace('\'', '\"')
with open('../output/company.json', 'w') as cf:
    cf.write(jsonOrigin)
    cf.close()
print(json.loads(jsonOrigin))
