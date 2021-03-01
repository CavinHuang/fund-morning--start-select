'''
Desc: 爬取晨星网基金列表数据，支持保存成csv，或者存入到mysql中
File: /acquire_fund_list.py
Project: src
File Created: Saturday, 26th December 2020 11:48:55 am
Author: luxuemin2108@gmail.com
-----
Copyright (c) 2020 Camel Lu
'''

import re
import math
import os
# import pymysql
from time import sleep
from bs4 import BeautifulSoup
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains
from lib.mysnowflake import IdWorker
from utils import parse_cookiestr, set_cookies, login_site, get_star_count, get_fund_detail_morningstar, get_tt_fund_manager_detail, get_howbuy_fund_manager_detail

# connect = pymysql.connect(host='127.0.0.1', user='root',
#                           password='rootroot', db='fund_work', charset='utf8')
# cursor = connect.cursor()

'''
判读是否当前页一致，没有的话，切换上一页，下一页操作
'''

morning_fund_selector_url = "https://www.morningstar.cn/fundselect/default.aspx"
result_dir = '../output/'

def text_to_be_present_in_element(locator, text, next_page_locator):
    """ An expectation for checking if the given text is present in the
    specified element.
    locator, text
    """
    def _predicate(driver):
        try:
            element_text = driver.find_element_by_xpath(locator).text
            # 比给定的页码小的话，触发下一页
            if int(element_text) < int(text):
                print(element_text, text)
                next_page = driver.find_element_by_xpath(
                    next_page_locator)
                # driver.refresh()
                next_page.click()
                sleep(5)
                # 比给定的页码大的话，触发上一页
            elif int(element_text) > int(text):
                print(element_text, text)
                prev_page = driver.find_element_by_xpath(
                    '/html/body/form/div[8]/div/div[4]/div[3]/div[3]/div[1]/a[2]')
                # driver.refresh()
                prev_page.click()
                sleep(5)
            return text == element_text
        except:
            return False

    return _predicate

def set_fund_condition(chrome_driver):
    print('打开了基金筛选器')

    groupCheckBox = chrome_driver.find_element_by_id('ctl00_cphMain_cblGroup_0')
    groupCheckBox.click()
    print('选择组别：开放式')
    sleep(0.5)

    # 根据货币基金筛选条件，进行选择筛选条件 并选中
    # 可转债
    huobi1CheckBox = chrome_driver.find_element_by_id('ctl00_cphMain_cblCategory_10')
    huobi1CheckBox.click()
    sleep(0.5)
    # 激进债券
    huobi2CheckBox = chrome_driver.find_element_by_id('ctl00_cphMain_cblCategory_11')
    huobi2CheckBox.click()
    sleep(0.5)
    # 普通债券
    huobi3CheckBox = chrome_driver.find_element_by_id('ctl00_cphMain_cblCategory_12')
    huobi3CheckBox.click()
    sleep(0.5)
    # 纯债基金
    huobi4CheckBox = chrome_driver.find_element_by_id('ctl00_cphMain_cblCategory_13')
    huobi4CheckBox.click()
    sleep(0.5)
    # 短债基金
    huobi5CheckBox = chrome_driver.find_element_by_id('ctl00_cphMain_cblCategory_14')
    huobi5CheckBox.click()
    sleep(0.5)
    print('选择货币基金筛选条件成功')

    # 选择基金规模 range 并设置为100 - 200+
    ziChanRange = chrome_driver.find_element_by_id('fs_slider_tna')
    # 给浏览器添加事件
    action = ActionChains(chrome_driver)
    # 对滑块按住鼠标左键不放
    action.move_to_element(ziChanRange)
    action.move_by_offset(-45, 0)
    action.click().perform()
    sleep(1)
    action.release()
    action.move_to_element(ziChanRange)
    action.move_by_offset(90, 0)  # 以上一次移动为基础
    action.click().perform()
    action.release()
    # sleep(1)
    # action.reset_actions()
    # action.move_by_offset(45, 0) # 以上一次移动为基础
    # action.click().perform()
    print('选择基金规模筛选条件成功')

    # 业绩总回报 选择 今年以来、三个月、六个月、一年、两年、三年、五年 都>=同类平均
    thisYear = chrome_driver.find_element_by_id('ctl00_cphMain_ucPerformance_rbYtd1')
    thisYear.click()

    threeMonth = chrome_driver.find_element_by_id('ctl00_cphMain_ucPerformance_rbM31')
    threeMonth.click()

    sixMonth = chrome_driver.find_element_by_id('ctl00_cphMain_ucPerformance_rbM61')
    sixMonth.click()

    oneYear = chrome_driver.find_element_by_id('ctl00_cphMain_ucPerformance_rbY11')
    oneYear.click()

    twoYear = chrome_driver.find_element_by_id('ctl00_cphMain_ucPerformance_rbY21')
    twoYear.click()

    threeYear = chrome_driver.find_element_by_id('ctl00_cphMain_ucPerformance_rbY31')
    threeYear.click()

    fiveYear = chrome_driver.find_element_by_id('ctl00_cphMain_ucPerformance_rbY51')
    fiveYear.click()
    print('选择基金业绩总回报筛选条件成功')

    # 筛选
    chrome_driver.find_element_by_id('ctl00_cphMain_btnGo').click()
    print('开始筛选')

def get_fund_list(cookie_str=None):
    from selenium import webdriver

    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    chrome_driver = webdriver.Chrome(
        './chromedriver/chromedriver.exe', chrome_options=options)
    chrome_driver.set_page_load_timeout(12000)    # 防止页面加载个没完

    """
    模拟登录,支持两种方式：
        1. 设置已经登录的cookie
        2. 输入账号，密码，验证码登录（验证码识别正确率30%，识别识别支持重试）
    """
    if cookie_str:
        set_cookies(chrome_driver, morning_fund_selector_url, cookie_str)
    else:
        morning_cookies = ""
        if morning_cookies == "":
            login_status = login_site(chrome_driver, morning_fund_selector_url)
            if login_status:
                print('自动登录成功')
                sleep(3)
                set_fund_condition(chrome_driver)
            else:
                print('login fail')
                exit()
            # 获取网站cookie
            morning_cookies = chrome_driver.get_cookies()
        else:
            chrome_driver.get(morning_fund_selector_url)  # 再次打开爬取页面
            print(chrome_driver.get_cookies())  # 打印设置成功的cookie
    # 定义起始页码
    page_num = 1
    page_count = 25
    page_num_total = math.ceil(int(chrome_driver.find_element_by_xpath(
        '/html/body/form/div[8]/div/div[4]/div[3]/div[2]/span').text) / page_count)

    output_head = '代码' + ',' + '晨星专属号' + ',' + '名称' + ',' + '类型' + ',' + '三年评级' + ',' + '五年评级' + ',' + '今年回报率' + ',' + '基金规模' + ',' + '基金公司' + ',' + '基金公司规模' + ',' + '基金经理' + ',' + '任职时间' + ',' + '天天基金经理评分' + ',' + '好买基金经理评分' + ',' + '现金比率' + ',' + '股票比率' + ',' + '债券比率' + ',' + '杠杆率' + ',' + '阿尔法系数' + ',' + '夏普比率' + ',' + '标准差' + ',' + '贝塔系数' + '\n'
    # 设置表头
    if page_num == 1:
        with open(result_dir + 'fund_morning_star_bounds.csv', 'w+') as csv_file:
            csv_file.write(output_head)

    allData = []
    while page_num <= page_num_total:
        # 求余
        remainder = page_num_total % 10
        # 判断是否最后一页
        num = (remainder + 2) if page_num > (page_num_total - remainder) else 12
        xpath_str = '/html/body/form/div[8]/div/div[4]/div[3]/div[3]/div[1]/a[%s]' % (
            num)
        print('当前处理页', page_num)
        print('总页码', page_num_total)
        # 等待，直到当前页（样式判断）等于page_num
        WebDriverWait(chrome_driver, timeout=600).until(text_to_be_present_in_element(
            "/html/body/form/div[8]/div/div[4]/div[3]/div[3]/div[1]/span[@style='margin-right:5px;font-weight:Bold;color:red;']", str(page_num), xpath_str))
        sleep(2)
        # 列表用于存放爬取的数据
        id_list = []  # 雪花id
        code_list = []  # 基金代码
        morning_star_code_list = []  # 晨星专属代码
        name_list = []  # 基金名称
        fund_cat = []  # 基金分类
        fund_rating_3 = []  # 晨星评级（三年）
        fund_rating_5 = []  # 晨星评级（五年）
        rate_of_return = []  # 今年以来汇报（%）

        # 获取每页的源代码
        data = chrome_driver.page_source
        # 利用BeautifulSoup解析网页源代码
        bs = BeautifulSoup(data, 'lxml')
        class_list = ['gridItem', 'gridAlternateItem']  # 数据在这两个类下面

        # 取出所有类的信息，并保存到对应的列表里
        for i in range(len(class_list)):
            for tr in bs.find_all('tr', {'class': class_list[i]}):
                # 雪花id
                worker = IdWorker()
                id_list.append(worker.get_id())
                tds_text = tr.find_all('td', {'class': "msDataText"})
                tds_nume = tr.find_all('td', {'class': "msDataNumeric"})
                # 基金代码
                code_a_element = tds_text[0].find_all('a')[0]
                code_list.append(code_a_element.string)
                # 从href中匹配出晨星专属代码
                current_morning_code = re.findall(
                    r'(?<=/quicktake/)(\w+)$', code_a_element.get('href')).pop(0)
                # 晨星基金专属晨星码
                morning_star_code_list.append(current_morning_code)
                name_list.append(tds_text[1].find_all('a')[0].string)
                # 基金分类
                fund_cat.append(tds_text[2].string)
                # 三年评级
                rating = get_star_count(tds_text[3].find_all('img')[0]['src'])
                fund_rating_3.append(rating)
                # 5年评级
                rating = get_star_count(tds_text[4].find_all('img')[0]['src'])
                fund_rating_5.append(rating)
                # 今年以来回报(%)
                return_value = tds_nume[3].string if tds_nume[3].string != '-' else None
                rate_of_return.append(return_value)

        for item in pd.DataFrame({'fund_code': code_list, 'morning_star_code': morning_star_code_list, 'fund_name': name_list, 'fund_cat': fund_cat,'fund_rating_3': fund_rating_3, 'fund_rating_5': fund_rating_5, 'rate_of_return': rate_of_return}).values.tolist():
            allData.append(item)

        # ql_insert = "replace into fund_morning_star(`id`, `fund_code`,`morning_star_code`, `fund_name`, `fund_cat`, `fund_rating_3`, `fund_rating_5`, `rate_of_return`) values(%s, %s, %s, %s, %s, %s, %s, %s)"
        # print('fund_df', fund_df)
        # fund_list = fund_df.values.tolist()
        # cursor.executemany(sql_insert, fund_list)
        # connect.commit()
        # print('fund_list', fund_list)
        print('第' + str(page_num) + '页数据准备完毕')
        # 获取下一页元素
        next_page = chrome_driver.find_element_by_xpath(
            xpath_str)
        # 点击下一页
        next_page.click()
        page_num += 1
        print('下一页：第' + str(page_num) + '页')


    # 填充基金详细数据
    writeCsvAndGetFundDetail(chrome_driver, allData)
    chrome_driver.close()
    print('end')
    # chrome_driver.close()


def writeCsvAndGetFundDetail(chrome_driver, allData):
    print('开始组织表格数据')
    with open(result_dir + 'fund_morning_star_bounds.csv', 'a') as csv_file:
        for fund_item in allData:
            print('开始处理' + str(fund_item[2]) + str(fund_item[1]))
            output_line = ', '.join('\t' + str(x) for x in fund_item)
            # 获取天天基金详细信息
            print('获取详细信息')
            totalFree, company, companyFree, fundManager, manager_time, cash, stock, bonds, leverage_ratio, qt_riskstats, standard_deviation, sharpe_ratio, beta = get_fund_detail_morningstar(chrome_driver, fund_item[1])

            sleep(1)
            # 获取天天基金经理评分
            print('获取天天基金经理评分')
            tt_fund_manager_roate = get_tt_fund_manager_detail(fund_item[0])
            print('获取好买基金经理评分')
            howbuy_manager_roate = get_howbuy_fund_manager_detail(fundManager)

            output_line += ',' + str(totalFree) + ',' + str(company) + ',' + str(companyFree) + ',' + str(fundManager) + ',' + str(manager_time) + ',' + str(tt_fund_manager_roate) + ',' + str(howbuy_manager_roate) + ',' + str('\t'+cash) + ',' + str('\t'+stock) + ',' + str('\t' + bonds) + ',' + str(leverage_ratio) + ',' + str(qt_riskstats) + ',' + str(sharpe_ratio) + ',' + str(standard_deviation) + ',' + str(beta) + '\n'
            sleep(2)
            print('数据准备写入文件', output_line)
            csv_file.write(output_line)

if __name__ == "__main__":
    cookie_str = ''

    fund_list = get_fund_list()
