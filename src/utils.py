from urllib import parse
import time
import os
import json
import requests
import js2py
import selenium.webdriver.support.ui as ui


def parse_cookiestr(cookie_str, split_str="; "):
    cookielist = []
    for item in cookie_str.split(split_str):
        cookie = {}
        itemname = item.split('=')[0]
        iremvalue = item.split('=')[1]
        cookie['name'] = itemname
        cookie['value'] = parse.unquote(iremvalue)
        cookielist.append(cookie)
    return cookielist


def set_cookies(chrome_driver, url, cookie_str):
    chrome_driver.get(url)
    # 2.需要先获取一下url，不然使用add_cookie会报错，这里有点奇怪
    cookie_list = parse_cookiestr(cookie_str)
    chrome_driver.delete_all_cookies()
    for i in cookie_list:
        cookie = {}
        # 3.对于使用add_cookie来说，参考其函数源码注释，需要有name,value字段来表示一条cookie，有点生硬
        cookie['name'] = i['name']
        cookie['value'] = i['value']
        # 4.这里需要先删掉之前那次访问时的同名cookie，不然自己设置的cookie会失效
        # chrome_driver.delete_cookie(i['name'])
        # 添加自己的cookie
        # print('cookie', cookie)
        chrome_driver.add_cookie(cookie)
    chrome_driver.refresh()


def identify_verification_code(chrome_driver, id="checkcodeImg"):
    # 生成年月日时分秒时间
    picture_time = time.strftime(
        "%Y-%m-%d-%H_%M_%S", time.localtime(time.time()))
    directory_time = time.strftime("%Y-%m-%d", time.localtime(time.time()))
    # 获取到当前文件的目录，并检查是否有 directory_time 文件夹，如果不存在则自动新建 directory_time 文件
    try:
        file_Path = os.getcwd() + '/code-record/' + directory_time + '/'
        if not os.path.exists(file_Path):
            os.makedirs(file_Path)
            print("目录新建成功：%s" % file_Path)
        else:
            print("目录已存在！！！")
    except BaseException as msg:
        print("新建目录失败：%s" % msg)
    try:
        from selenium.webdriver.common.by import By
        ele = chrome_driver.find_element(By.ID, id)
        code_path = './code-record/' + directory_time + '/' + picture_time + '_code.png'
        url = ele.screenshot(code_path)
        if url:
            print("%s ：截图成功！！！" % url)
            from PIL import Image
            image = Image.open(code_path)
            # image.show()
            import pytesseract
            custom_oem_psm_config = '--oem 0 --psm 13 digits'
            identify_code = pytesseract.image_to_string(
                image, config=custom_oem_psm_config)
            code = "".join(identify_code.split())
            return code
        else:
            raise Exception('截图失败,不能保存')
    except Exception as pic_msg:
        print("截图失败：%s" % pic_msg)


def get_star_count(morning_star_url):
    import numpy as np
    import requests
    from PIL import Image
    module_path = os.path.dirname(__file__)
    temp_star_url = module_path + '/assets/star/tmp.gif'
    r = requests.get(morning_star_url)
    with open(temp_star_url, "wb") as f:
        f.write(r.content)
    f.close()
    path = module_path + '/assets/star/star'

    # path = './assets/star/star'
    for i in range(6):
        p1 = np.array(Image.open(path + str(i) + '.gif'))
        p2 = np.array(Image.open(temp_star_url))
        if (p1 == p2).all():
            return i


def login_site(chrome_driver, site_url):
    chrome_driver.get(site_url)
    time.sleep(2)
    from selenium.webdriver.support import expected_conditions as EC
    username = chrome_driver.find_element_by_id('emailTxt')
    password = chrome_driver.find_element_by_id('pwdValue')
    check_code = chrome_driver.find_element_by_id('txtCheckCode')
    username.send_keys('sujinw@qq.com')
    password.send_keys('Zhcm1993')
    count = 1
    flag = True
    while count < 10 and flag:
        code = identify_verification_code(chrome_driver)
        check_code.clear()
        time.sleep(1)
        check_code.send_keys(code)
        time.sleep(3)
        submit = chrome_driver.find_element_by_id('loginGo')
        submit.click()
        # 通过弹窗判断验证码是否正确
        time.sleep(3)
        from selenium.webdriver.common.by import By
        # message_container = chrome_driver.find_element_by_id('message-container')
        try:
            message_box = chrome_driver.find_element_by_id(
                'message-container')
            flag = message_box.is_displayed()
            print('是否出现出错框'+ str(flag))
            if flag:
                close_btn = message_box.find_element(
                    By.CLASS_NAME, "modal-close")
                close_btn.click()
                time.sleep(1)
            print('flag', flag)

        except Exception as r:
            print('未知错误 %s' % r)
            return True

    if count > 10:
        return False
    return True


# 获取基金的详情
def get_fund_detail_morningstar(chrome_driver, subPath):
    # https://www.morningstar.cn/quicktake/0P00016LM0
    webUrl = 'https://www.morningstar.cn/quicktake/' + subPath
    print('打开', webUrl)
    chrome_driver.get(webUrl)

    time.sleep(2)

    totalFree = 0
    while totalFree == 0:
        wait = ui.WebDriverWait(chrome_driver, 5)
        wait.until(lambda driver: chrome_driver.find_element_by_xpath('//*[@id="qt_base"]/ul[3]/li[8]/span'))
        totalEle = chrome_driver.find_element_by_xpath('//*[@id="qt_base"]/ul[3]/li[8]/span')
        totalFree = totalEle.text
    #处理逗号问题
    totalFree = str(totalFree).replace(',', '')
    time.sleep(0.5)

    company = ''

    while company == '':
        wait = ui.WebDriverWait(chrome_driver, 5)
        wait.until(lambda driver: chrome_driver.find_element_by_xpath('//*[@id="qt_management"]/li[4]/span[2]/a'))
        companyEle = chrome_driver.find_element_by_xpath('//*[@id="qt_management"]/li[4]/span[2]/a')
        company = companyEle.text

    time.sleep(0.5)

    fundManager = 0

    while fundManager == 0:
        wait = ui.WebDriverWait(chrome_driver, 5)
        wait.until(lambda driver: chrome_driver.find_element_by_xpath('//*[@id="qt_manager"]/ul[1]/li[1]/a'))
        fundManagerEle = chrome_driver.find_element_by_xpath('//*[@id="qt_manager"]/ul[1]/li[1]/a')
        fundManager = fundManagerEle.text

    time.sleep(0.5)
    manager_time = ''
    while manager_time == '':
        wait = ui .WebDriverWait(chrome_driver, 5)
        wait.until(lambda driver: chrome_driver.find_element_by_xpath('//*[@id="qt_manager"]/ul[1]/li[1]/span'))
        manager_time_ele = chrome_driver.find_element_by_xpath('//*[@id="qt_manager"]/ul[1]/li[1]/span')
        manager_time = str(manager_time_ele.text).replace('管理时间：', '')
    companyFree = 0

    # 计算杠杆率
    wait = ui.WebDriverWait(chrome_driver, 5)
    wait.until(lambda driver: chrome_driver.find_element_by_xpath('//*[@id="qt_asset"]/li[5]'))
    # 现金
    cash_ele = chrome_driver.find_element_by_xpath('//*[@id="qt_asset"]/li[5]')
    cash = str(cash_ele.text)
    # 股票
    stock_ele = chrome_driver.find_element_by_xpath('//*[@id="qt_asset"]/li[8]')
    stock = str(stock_ele.text)
    # 债券
    bonds_ele = chrome_driver.find_element_by_xpath('//*[@id="qt_asset"]/li[11]')
    bonds = str(bonds_ele.text)

    leverage_ratio = float(cash) + float(stock) + float(bonds)

    # 获取阿尔法系数
    qt_riskstats_ele = chrome_driver.find_element_by_xpath('//*[@id="qt_riskstats"]/li[5]')
    qt_riskstats = str(qt_riskstats_ele.text)

    # 获取标准差 3年
    standard_deviation_ele = chrome_driver.find_element_by_xpath('//*[@id="qt_risk"]/li[16]')
    standard_deviation = str(standard_deviation_ele.text)

    # 三年夏普比率
    sharpe_ratio_ele = chrome_driver.find_element_by_xpath('//*[@id="qt_risk"]/li[30]')
    sharpe_ratio = str(sharpe_ratio_ele.text)

    beta_ele = chrome_driver.find_element_by_xpath('//*[@id="qt_riskstats"]/li[8]')
    beta = str(beta_ele.text)

    # 获得天天基金网站，关于基金公司的数据
    with open('../output/company.json', 'r') as cf:
        jsonData = json.loads(cf.read())

        for value in jsonData:
            if value[1] == company:
                companyFree = str(value[7]).replace(',', '')
                break

        print('+++++++基金数据')
        print(totalFree, company, fundManager, companyFree)

        return totalFree, company, companyFree, fundManager, manager_time, cash, stock, bonds, leverage_ratio, qt_riskstats, standard_deviation, sharpe_ratio, beta


# 获取天天基金的基金经理数据
def get_tt_fund_manager_detail(funCode):
    timestamp = time.time() * 1000
    apiUrl = "http://fund.eastmoney.com/pingzhongdata/" + funCode + ".js?v=20210226084939"
    header = {
        "Accept": "* / *",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh-TW;q=0.9,zh;q=0.8",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Cookie": "st_si=75540904388619; st_asi=delete; ASP.NET_SessionId=nvv1yet2ffaes4z5spbaoziz; EMFUND1=null; EMFUND2=null; EMFUND3=null; EMFUND4=null; EMFUND5=null; EMFUND6=null; EMFUND7=null; EMFUND0=null; qgqp_b_id=42a63a14f8cfdba4d003f387cd2f086f; EMFUND9=02-26%2008%3A53%3A59@%23%24%u56FD%u5BCC%u5065%u5EB7%u4F18%u8D28%u751F%u6D3B%u80A1%u7968@%23%24000761; EMFUND8=02-26 08:55:54@#$%u519C%u94F6%u65B0%u80FD%u6E90%u4E3B%u9898@%23%24002190; st_pvi=97911961255996; st_sp=2021-02-24%2014%3A23%3A57; st_inirUrl=https%3A%2F%2Fwww.baidu.com%2Flink; st_sn=157; st_psi=20210226085557905-0-9129869508",
        "Host": "fund.eastmoney.com",
        "Pragma": "no-cache",
        "Referer": "http://fund.eastmoney.com/" + funCode + ".html",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4168.3 Safari/537.36"
    }

    proxies = {"http": None, "https": None}
    response = requests.get(apiUrl, {}, headers=header, proxies=proxies)

    responseText = response.text

    #     - 使用js2py生成js的执行环境:context
    context = js2py.EvalJs()
    context.execute(responseText)

    return context.Data_currentFundManager[0].power.avr


# 获取好买基金经理平分
def get_howbuy_fund_manager_detail(manager):
    apiUrl = "https://www.howbuy.com/fund/manager/ajax.htm"
    header = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh-TW;q=0.9,zh;q=0.8",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": "_ga=GA1.2.405888444.1614148332; __hutmc=268394641; __hutmz=268394641.1614148332.1.1.hutmcsr=baidu|hutmccn=(organic)|hutmcmd=organic; __hutmmobile=640C1A6E-FEB5-4FE8-9314-F8E3C25F839E; _zero_hbtrack=0.2800000; _hbotrack=2800000-0-0-0.0; _hb_ref_pgid=11010; Hm_lvt_394e04be1e3004f9ae789345b827e8e2=1614148332; SESSION=40ec4d4f-ec06-444a-bf1c-d52887114acf; _gid=GA1.2.1249994975.1614245792; __hutma=268394641.557365076.1614148332.1614247910.1614303482.4; _gat=1; _hb_pgid=11010; Hm_lpvt_394e04be1e3004f9ae789345b827e8e2=1614303484; OZ_1U_1497=vid=v035f2ec9fe37d.0&ctime=1614303484&ltime=1614303481; OZ_1Y_1497=erefer=https%3A//www.baidu.com/link%3Furl%3Dvj22cGIHQ8lChAO7qJtKtmae2rkbb1aw_6dzCyK4LdKIT5yUYxE-BVlAmYfBahgb%26wd%3D%26eqid%3Dd2f56e67000640f6000000066035f2de&eurl=https%3A//www.howbuy.com/&etime=1614148332&ctime=1614303484&ltime=1614303481&compid=1497; __hutmb=268394641.3.10.1614303482; OZ_SI_1497=sTime=1614148332&sIndex=36",
        "Host": "www.howbuy.com",
        "Origin": "https://www.howbuy.com",
        "Pragma": "no-cache",
        "Referer": "https://www.howbuy.com/fund/manager/",
        "sec-ch-ua": '"\\Not;A\"Brand";v="99", "Google Chrome";v="85", "Chromium";v="85"',
        "sec-ch-ua-mobile": "?0",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4168.3 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest"
    }

    data = {
        "wzfl": '',
        "cynx": '',
        "jgdm": '',
        "keyword": manager,
        "ryzt": '',
        "orderField": "rqzs",
        "orderType": "true",
        "page": 1
    }

    proxies = {"http": None, "https": None}
    response = requests.post(apiUrl, data=data, headers=header, proxies=proxies)

    responseText = json.loads(response.text)

    try:
        manager = responseText["list"][0]['jdjf']
    except:
        manager = 0
    return manager
