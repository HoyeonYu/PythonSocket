import multiprocessing
import socket
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.select import Select


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

    languangeChange = Select(driver.find_element_by_css_selector('#LANG'))
    languangeChange.select_by_index(0)
    print("Translate Done")

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

        realLectureIdx += 1

        connection.sendall(bytes(lectureTitle[4:] + "\n", 'utf-8')) # lecture name
        innerLecture = driver.find_element_by_xpath("//*[@id=\"menu_lecture_weeks\"]")
        innerLecture.click()

        if check_exists_by_id("per_text"):
            innerTotalLectureLength = driver.find_elements_by_class_name("wb-inner-wrap ")
            driver.find_element_by_xpath("/ html / body / div[3] / div[2] / div / div[2] / div[2] / div[2] / "
                                         "div / div[" + str(len(innerTotalLectureLength)) + "] / div").click()

            print("exist")
            innerLecturePerTexts = driver.find_elements_by_id("per_text")
            connection.sendall(bytes(str(len(innerLecturePerTexts)) + "\n", 'utf-8'))   # inner lecture num

            innerLecturePeriod = driver.find_element_by_xpath(
                "//*[@id=\"lecture_form\"] / div[1] / div / ul / li[1] / ol / li[2] / div[2] ").text
            print(innerLecturePeriod)
            connection.sendall(bytes(innerLecturePeriod + "\n", 'utf-8'))  # inner lecture period

            for innerLectureIdx in range(len(innerLecturePerTexts)):
                innerLecturePerText = innerLecturePerTexts[innerLectureIdx].text
                connection.sendall(bytes(innerLecturePerText + "\n", 'utf-8'))  # inner lecture percentage
                print(innerLectureIdx, innerLecturePerText)
                innerLectureIdx += 1
        else:
            connection.sendall(bytes("0\n", 'utf-8'))
            print("does not exist")

        driver.get(driver.find_element_by_xpath("//*[@id=\"menu_report\"]").get_attribute("href"))

        if check_exists_by_xpath("//*[@id=\"report_list\"]/table/tbody/tr[1]/td[1]"):
            assignmentNum = driver.find_element_by_xpath("//*[@id=\"report_list\"]/table/tbody/tr[1]/td[1]").text
            print("total assignment num: ", assignmentNum)

            if assignmentNum != "조회할 자료가 없습니다" and assignmentNum != "No Data.":
                connection.sendall(bytes(assignmentNum + "\n", 'utf-8'))  # total assignment num

                for i in range (int(assignmentNum)):
                    isAssignmentInPeriod = driver.find_element_by_xpath("//*[@id=\"report_list\"]/table/tbody/tr["
                                                                        + str(i + 1) + "]/td[4]").text
                    if isAssignmentInPeriod == "종료":
                        connection.sendall(bytes("AssignmentDone\n", 'utf-8'))
                        break

                    assignmentName = driver.find_element_by_xpath("//*[@id=\"report_list\"]/table/tbody/tr["
                                                                      + str(i + 1) + "]/td[3]/a/div[1]").text.replace('[', '').replace(']', '')
                    connection.sendall(bytes(assignmentName + "\n", 'utf-8'))  # get assignment name
                    print(assignmentName)

                    isAssignmentSubmitted = driver.find_element_by_xpath("//*[@id=\"report_list\"]/table/tbody/tr["
                                                                      + str(i + 1) + "]/td[5]/img").get_attribute("title")
                    connection.sendall(bytes(isAssignmentSubmitted + "\n", 'utf-8'))   # if is assignment in period, get submitted
                    print(isAssignmentSubmitted)

                    assignmentPeriod = driver.find_element_by_xpath("//*[@id=\"report_list\"]/table/tbody/tr["
                                                                    + str(i + 1) + "]/td[8]").text
                    connection.sendall(bytes(assignmentPeriod + "\n", 'utf-8')) # if is assignment in period, get deadline
                    print(assignmentPeriod)
            else:
                connection.sendall(bytes("AssignmentDone\n", 'utf-8'))

        else:
            print("no assignment")

        # report_list > table > tbody > tr:nth-child(1) > td:nth-child(4)
        driver.get(url)
        outerLectures = driver.find_elements_by_class_name("sub_open")
        outerLecturesIdx += 1

    connection.sendall(bytes(str(realLectureIdx) + "\n", 'utf-8'))  # real lecture num
    print("real lecture num:", realLectureIdx)
    driver.close()


def handle(connection, address):
    try:
        input = connection.recv(1024).decode('utf-8')
        #print("input: " + input)
        #print(input.split("\n"))

        if len(input.split("\n")) == 2:
            id = input
            pw = connection.recv(1024).decode('utf-8')
            #print("pw: " + pw)

        else:
            id = input.split("\n")[0] + "\n"
            pw = input.split("\n")[1] + "\n"

        print("id: " + id)

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
