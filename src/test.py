from utils import parse_cookiestr, set_cookies, login_site, get_star_count, get_fund_detail_morningstar, get_howbuy_fund_manager_detail
from time import sleep
from selenium import webdriver

# options = webdriver.ChromeOptions()
# options.add_argument("--no-sandbox")
# chrome_driver = webdriver.Chrome(
#     './chromedriver/chromedriver.exe', chrome_options=options)
# chrome_driver.set_page_load_timeout(12000)    # 防止页面加载个没完
#
# """
# 模拟登录,支持两种方式：
#     1. 设置已经登录的cookie
#     2. 输入账号，密码，验证码登录（验证码识别正确率30%，识别识别支持重试）
# """
# morning_fund_selector_url = "https://www.morningstar.cn/fundselect/default.aspx"
# cookie_str = 'SP.NET_SessionId=cp4nyufd2u0ipkao0hgdly45; MS_LocalEmailAddr=sujinw@qq.com=; Hm_lvt_eca85e284f8b74d1200a42c9faa85464=1614146656,1614147023,1614147031,1614153867; MSCC=E6dNKVFNIgg=; user=username=sujinw@qq.com&nickname=cavinHuang&status=Free&password=x7aWDYhiBM38uQeqO3FbZw==; authWeb=D7E38C09DF684CD25744A56241E08826F7CADFF56E969CFBB090E3E93248DCC3797A9F6672121BB179C16DC8F10F8F26C6AE35436BB792EE52D921D7A613B5DEB5B000223199A321FAC8C771DD42B376C306C47A57E6BB0D7CB88EA0E800987E73798AEB5572C2B44726A393CB033F851EE76FBE; Hm_lpvt_eca85e284f8b74d1200a42c9faa85464=1614241928'
# if cookie_str:
#     set_cookies(chrome_driver, 'https://www.morningstar.cn/quicktake/0P00015AHN', cookie_str)
# get_fund_detail_morningstar(chrome_driver, '0P00015AHN')


print(get_howbuy_fund_manager_detail('张坤'))
