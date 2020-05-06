import smtplib
import os

from email.mime.text import MIMEText

from selenium import webdriver
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from apscheduler.schedulers.blocking import BlockingScheduler

options = webdriver.ChromeOptions()
options.add_argument('headless')

dirName = os.path.dirname(__file__)
account_path = os.path.join(dirName, "account_info.txt")
email_address_path = os.path.join(dirName, "mail_address.txt")
real_path = os.path.join(dirName, "chromedriver.exe")

browser = webdriver.Chrome(real_path, options=options)

scheduler = BlockingScheduler()


def read_account(path):
    file = open(path, 'r')
    id = file.readline().replace("\n", "")
    pw = file.readline().replace("\n", "")
    file.close()
    return {"id": id, "pw": pw}


def read_send_email(path):
    file = open(path, 'r')
    email = []
    for mail in file.readlines():
        if not mail:
            continue

        mail = mail.replace("\n", "")
        email.append(mail)
    file.close()
    return email


def send_email(title, msg):
    print("send_email")
    try:
        account_info = read_account(account_path)
        smtp = smtplib.SMTP_SSL('smtp.naver.com', 465)
        smtp.login(account_info['id'], account_info['pw'])
        smtp.helo()

        mail_list = read_send_email(email_address_path)

        message = MIMEText(msg)
        message["Subject"] = title
        message["To"] = mail_list[0]
        message["From"] = mail_list[0]

        for mail in mail_list:
            smtp.sendmail(mail_list[0], mail, message.as_string())
        smtp.quit()

    except Exception as ex:
        print("Email Send Error : %s" % ex)


def find_common(index, url):
    print('index : %d, url : %s' % (index, url))
    browser.get(url=url)

    if url.__contains__("himart"):
        item_list = browser.find_elements_by_xpath(".//ul[@id='productList']")

        if item_list.__len__() > 0:
            item_list = item_list[0].find_elements_by_tag_name("li")

            for item in item_list:
                sold_out = item.find_elements_by_xpath(".//a[@class='prdLink']/div[@class='soldout']")
                link = item.find_elements_by_xpath(".//a[@class='prdLink']")[0].get_attribute("href")
                if not sold_out:
                    return link

    elif url.__contains__("osgame"):
        item_list = browser.find_elements_by_xpath(".//div[@class='PJ_good_table']")

        for item in item_list:
            link = str(item.get_attribute("onclick")).split("../")[1]
            link = "http://www.osgame.co.kr/" + link
            sold_out = item.find_elements_by_class_name("item_price")[0].text

            if sold_out != '품절':
                return link

    else:
        item_list = browser.find_elements_by_xpath(".//dl[@class='item-list']")

        for item in item_list:
            price = item.find_elements_by_xpath(".//li[@class='prd-price']")[0].text
            link = item.find_elements_by_xpath(".//dt[@class='thumb']/a")[0].get_attribute("href")

            if price != "Sold Out":
                return link


def find_nintendo_switch():
    urls = ["http://www.e-himart.co.kr/app/display/showDisplayCategory?dispNo=1014020700",
            "http://www.nnmarket.co.kr/shop/shopbrand.html?type=M&xcode=025&mcode=001",
            "http://www.gamewoori.com/shop/shopbrand.html?type=M&xcode=005&mcode=001",
            "http://www.osgame.co.kr/goods/goods_list.php?cateCd=004001"]

    link = ""
    for idx, url in enumerate(urls):
        link = find_common(idx + 1, url)
        if link:
            break

    return link


def start_crawling():
    nintendo_link = find_nintendo_switch()
    if nintendo_link:
        send_email("!!!! 닌텐도 스위치 재고떴다 !!!!", nintendo_link)
        scheduler.remove_all_jobs()
    else:
        print("모든곳에서 재고가 없네요..")


def listener(event):
    if event.exception:
        print("The job crashed")
    else:
        print("The job worked")


start_crawling()
# scheduler.add_job(start_crawling, 'interval', minutes=1)
# scheduler.add_listener(listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
# scheduler.start()
