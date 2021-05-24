import time
import socket
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options

user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'

print("python start")
print("before driver")

options = webdriver.ChromeOptions()
options.add_argument('--disable-extensions')
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
driver = webdriver.Chrome('/home/ubuntu/chromedriver', chrome_options=options)


def check_exists_by_id(id):
    try:
        driver.find_element_by_id(id)
    except NoSuchElementException:
        return False
    return True


def check_exists_by_xpath(xpath):
    try:
        driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False
    return True


def getLMSLogin(id, password):
    url = 'https://lms.sungshin.ac.kr/ilos/main/member/login_form.acl'
    driver.get(url)

    elementID = driver.find_element_by_xpath("//*[@id=\"usr_id\"]")
    elementID.send_keys(id)
    elementPW = driver.find_element_by_xpath("//*[@id=\"usr_pwd\"]")
    elementPW.send_keys(password)
    time.sleep(0.5)
    print("sleep done")

    try:
        alert = driver.switch_to.alert
        alert.accept()
        print("login fail")
        return False

    except:
        url = 'https://lms.sungshin.ac.kr/ilos/main/main_form.acl'
        driver.get(url)
        global userName
        userName = driver.find_element_by_xpath("//*[@id=\"user\"]").text
        print(userName)
        print("login success")
        return True


def getLMSSubject():
    url = 'https://lms.sungshin.ac.kr/ilos/main/main_form.acl'
    driver.get(url)

    outerLectures = driver.find_elements_by_class_name("sub_open")

    for outerLecturesIdx in range(len(outerLectures)):
        print(outerLecturesIdx)
        outerLectures[outerLecturesIdx].click()
        time.sleep(0.1)
        print(driver.find_element_by_class_name("welcome_subject").text)
        innerLecture = driver.find_element_by_xpath("//*[@id=\"menu_lecture_weeks\"]")
        innerLecture.click()
        time.sleep(0.1)

        if check_exists_by_id("per_text"):
            print("exist")
            innerLecturePerTexts = driver.find_elements_by_id("per_text")

            for innerLectureIdx in range(len(innerLecturePerTexts)):
                print(innerLectureIdx, innerLecturePerTexts[innerLectureIdx].text)
                innerLectureIdx += 1
        else:
            print("does not exist")

        driver.get(url)
        outerLectures = driver.find_elements_by_class_name("sub_open")
        outerLecturesIdx += 1
        time.sleep(0.1)


def socketServer():
    SERVER = "0.0.0.0"
    PORT = 8080
    ADDR = (SERVER, PORT)

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind(ADDR)
    server_sock.listen(0)

    print("Waiting for Client")
    client_sock, addr = server_sock.accept()

    print("Connected by", addr)

    id = client_sock.recv(1024).decode('cp949')
    print(id, len(id))

    pw = client_sock.recv(1024).decode('cp949')
    # print(pw, len(pw))

    if getLMSLogin(str(id), str(pw)):
        client_sock.sendall(bytes("Success\n", 'cp949'))
        print(userName)
        client_sock.sendall(bytes(userName, 'utf-8'))
        # time.sleep(1)
        # getLMSSubject()

    else:
        client_sock.sendall(bytes("Failed", 'cp949'))


while True:
    print("After driver")
    socketServer()
