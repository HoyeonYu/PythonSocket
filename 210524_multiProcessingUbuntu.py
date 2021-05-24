import multiprocessing
import socket
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException


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
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-extensions')
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')

    global driver
    driver = webdriver.Chrome('/home/ubuntu/chromedriver', chrome_options=options)
    driver.implicitly_wait(0.2)
    url = 'https://lms.sungshin.ac.kr/ilos/main/member/login_form.acl'
    driver.get(url)
    print("LMS Login Start")
    print(driver.current_url)

    elementID = driver.find_element_by_xpath("//*[@id=\"usr_id\"]")
    elementID.send_keys(id)

    elementPW = driver.find_element_by_xpath("//*[@id=\"usr_pwd\"]")
    elementPW.send_keys(password)
    time.sleep(0.1)

    try:
        alert = driver.switch_to.alert
        alert.accept()
        print("login fail, again?")
        return False

    except:
        print("login success")
        return True


def getLMSSubject(connection):
    url = 'https://lms.sungshin.ac.kr/ilos/main/main_form.acl'
    driver.get(url)

    userName = driver.find_element_by_xpath("//*[@id=\"user\"]").text
    connection.sendall(bytes(userName + "\n", 'utf-8')) #name
    print(userName)

    outerLectures = driver.find_elements_by_class_name("sub_open")
    print(len(outerLectures))
    connection.sendall(bytes(str(len(outerLectures)) + "\n", 'utf-8'))  # total lecture num
    realLectureIdx = 0

    for outerLecturesIdx in range(len(outerLectures)):
        print(outerLecturesIdx)
        outerLectures[outerLecturesIdx].click()
        lectureTitle = driver.find_element_by_class_name("welcome_subject").text

        if lectureTitle[0:10] == "[Sungshin]" or lectureTitle[0:6] == "[성신여대]":
            connection.sendall(bytes("LectureDone\n", 'utf-8'))
            break

        print(lectureTitle)
        realLectureIdx += 1

        connection.sendall(bytes(lectureTitle + "\n", 'utf-8')) # lecture name
        innerLecture = driver.find_element_by_xpath("//*[@id=\"menu_lecture_weeks\"]")
        innerLecture.click()

        if check_exists_by_id("per_text"):
            print("exist")
            innerLecturePerTexts = driver.find_elements_by_id("per_text")
            connection.sendall(bytes(str(len(innerLecturePerTexts)) + "\n", 'utf-8'))   # inner lecture num

            for innerLectureIdx in range(len(innerLecturePerTexts)):
                innerLecturePerText = innerLecturePerTexts[innerLectureIdx].text
                connection.sendall(bytes(innerLecturePerText + "\n", 'utf-8'))  # inner lecture percentage
                print(innerLectureIdx, innerLecturePerText)
                innerLectureIdx += 1
        else:
            connection.sendall(bytes("0\n", 'utf-8'))
            print("does not exist")

        driver.get(url)
        outerLectures = driver.find_elements_by_class_name("sub_open")
        outerLecturesIdx += 1

    connection.sendall(bytes(str(realLectureIdx) + "\n", 'utf-8'))  # real lecture num
    print("real lecture num:", realLectureIdx)
    driver.close()


def handle(connection, address):
    try:
        input = connection.recv(1024).decode('utf-8')
        print("input: " + input)
        print(input.split("\n"))

        if len(input.split("\n")) == 2:
            id = input
            pw = connection.recv(1024).decode('utf-8')
            print("pw: " + pw)

        else:
            id = input.split("\n")[0] + "\n"
            pw = input.split("\n")[1] + "\n"
            print("split id: " + id)
            print("split pw: " + pw)

        if getLMSLogin(str(id), str(pw)):
            connection.sendall(bytes("Success\n", 'utf-8'))
            print("get LMS Subject")
            getLMSSubject(connection)

        else:
            connection.sendall(bytes("Failed\n", 'utf-8'))

    except:
        print("Problem handling request")

    connection.sendall(bytes("Closing socket\n", 'utf-8'))
    print("Close Client Socket")
    connection.close()


class Server(object):
    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = port
        self.socket = None

    def start(self):
        print("Waiting For Client ...")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.hostname, self.port))
        self.socket.listen(1)

        while True:
            conn, address = self.socket.accept()
            print("Connected by", address)
            process = multiprocessing.Process(target=handle, args=(conn, address))
            process.daemon = True
            process.start()


if __name__ == "__main__":
    server = Server("0.0.0.0", 8080)
    print("Hello from Server")

    try:
        server.start()
    except:
        print("Unexpected exception")
    finally:
        print("Shutting down")

        for process in multiprocessing.active_children():
            print("Shutting down process %r", process)
            process.terminate()
            process.join()

    print("All done")
