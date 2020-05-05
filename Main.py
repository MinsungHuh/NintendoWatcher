import smtplib

from email.mime.text import MIMEText
from selenium import webdriver

options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, "
                     "like Gecko) Chrome/81.0.3163.100 Safari/537.36")

browser = webdriver.Chrome("C:\\workspace\\nintendo\\chromedriver.exe", options=options)

account_path = "C:\\workspace\\nintendo\\account_info.txt"
email_address_path = "C:\\workspace\\nintendo\\mail_address.txt"


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
    print("\n")
    print('index : %d, url : %s' % (index, url))
    print("\n")
    browser.get(url=url)

    if url.__contains__("himart"):
        print("himart")
        item_list = browser.find_elements_by_xpath(".//ul[@id='productList']")[0].find_elements_by_tag_name("li")

        for item in item_list:
            sold_out = item.find_elements_by_xpath(".//a[@class='prdLink']/div[@class='soldout']/span")[0].text
            link = item.find_elements_by_xpath(".//a[@class='prdLink']")[0].get_attribute("href")
            print("sold_out : %s" % sold_out)
            print("link : %s" % link)

            if sold_out is None or sold_out != "SOLD OUT":
                return link

    elif url.__contains__("osgame"):
        print("onestop game")
        item_list = browser.find_elements_by_xpath(".//div[@class='PJ_good_table']")

        for item in item_list:
            link = str(item.get_attribute("onclick")).split("../")[1]
            link = "http://www.osgame.co.kr/" + link
            sold_out = item.find_elements_by_class_name("item_price")[0].text
            print("sold_out : %s" % sold_out)
            print("link : %s" % link)

            if sold_out != '품절':
                return link

    else:
        item_list = browser.find_elements_by_xpath(".//dl[@class='item-list']")

        for item in item_list:
            price = item.find_elements_by_xpath(".//li[@class='prd-price']")[0].text
            link = item.find_elements_by_xpath(".//dt[@class='thumb']/a")[0].get_attribute("href")
            print("sold out : %s" % price)
            print("link : %s" % link)

            if price != "Sold Out":
                return link

        return ""


def find_nintendo_switch():
    urls = ["http://www.nnmarket.co.kr/shop/shopbrand.html?type=M&xcode=025&mcode=001",
            "http://www.gamewoori.com/shop/shopbrand.html?type=M&xcode=005&mcode=001",
            "http://www.e-himart.co.kr/app/display/showDisplayCategory?dispNo=1014020700",
            "http://www.osgame.co.kr/goods/goods_list.php?cateCd=004001"]

    for idx, url in enumerate(urls):
        find_common(idx + 1, url)

    browser.quit()
    return ""


# send_email("닌텐도 메일 알리미", "테스트입니다.")
nintendo_link = find_nintendo_switch()
if nintendo_link:
    send_email("!!!! 닌텐도 스위치 재고떴다 !!!!", nintendo_link)
else:
    print("모든곳에서 재고가 없네요..")
