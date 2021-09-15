import multiprocessing
import re
import socket
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.select import Select

# Add School Name Here
schoolName = ["성신여자대학교", "경북대학교", "한국외국어대학교", "서강대학교", "건국대학교", "서울여자대학교"]

# Add Login Page Here
loginUrlList = [
    "https://lms.sungshin.ac.kr/ilos/main/member/login_form.acl",   # SungShin Women's
    "https://lms.knu.ac.kr/ilos/main/member/login_form.acl",        # KyeongBuk
    "https://eclass.hufs.ac.kr/ilos/main/member/login_form.acl",    # HUFS
    "https://eclass.sogang.ac.kr/ilos/main/member/login_form.acl",  # SoGang
    "https://ecampus.konkuk.ac.kr/ilos/main/member/login_form.acl", # KonKuk
    "https://cyber.swu.ac.kr/ilos/main/member/login_form.acl"       # Seoul Women's
]

# Add Main Page Here
mainUrlList = [
    "https://lms.sungshin.ac.kr/ilos/main/main_form.acl",       # SungShin Women's
    "https://lms.knu.ac.kr/ilos/main/main_form.acl",            # KyeongBuk
    "https://eclass.hufs.ac.kr/ilos/main/main_form.acl",        # HUFS
    "https://eclass.sogang.ac.kr/ilos/main/main_form.acl",      # SoGang
    "https://ecampus.konkuk.ac.kr/ilos/main/main_form.acl",     # KonKuk
    "https://cyber.swu.ac.kr/ilos/main/main_form.acl"           # Seoul Women's
]

# Add Total Lecture Page Here
lectureUrlList = [
    "https://lms.sungshin.ac.kr/ilos/mp/course_register_list_form.acl",         # SungShin Women's
    "https://lms.knu.ac.kr/ilos/mp/course_register_list_form.acl",              # KyeongBuk
    "https://eclass.hufs.ac.kr/ilos/mp/course_register_list_form.acl",          # HUFS
    "https://eclass.sogang.ac.kr/ilos/mp/course_register_list_form.acl",        # SoGang
    "https://ecampus.konkuk.ac.kr/ilos/mp/course_register_list_form.acl",       # KonKuk
    "https://cyber.swu.ac.kr/ilos/mp/course_register_list_form.acl"             # Seoul Women's
]


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


def removePopUp():
    try:
        popUp = driver.find_elements_by_class_name('x')
        for popUpUnit in popUp:
            popUpUnit.click()
    except:
        # print("no popUp")
        print("", end="")


def getLMSLogin(idx, id, password):
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-extensions')
    options.add_argument('--headless')
    # options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')

    global driver
    driver = webdriver.Chrome('/home/compu/Downloads/UnivPlanner_ServerCode/chromedriver', chrome_options=options)
    driver.get(loginUrlList[idx])
    print(" LMS Login Start :", end=" ")
    # print(driver.current_url)

    elementID = driver.find_element_by_xpath("//*[@id=\"usr_id\"]")
    elementID.send_keys(id)

    elementPW = driver.find_element_by_xpath("//*[@id=\"usr_pwd\"]")
    elementPW.send_keys(password)

    try:
        alert = driver.switch_to.alert
        alert.accept()
        print("Login Failed, Again?")
        driver.close()
        return False

    except:
        print("Login Success!")
        return True


def getLMSSubject(idx, connection):
    mainLMSUrl = mainUrlList[idx]
    driver.get(mainLMSUrl)

    languangeChange = Select(driver.find_element_by_css_selector('#LANG'))
    languangeChange.select_by_index(0)
    # print("Translate Done")

    userName = driver.find_element_by_xpath("//*[@id=\"user\"]").text
    connection.sendall(bytes(userName + "\n", 'utf-8'))  # name
    print("\n ***** " + userName + " ***** \n")

    outerLectures = driver.find_elements_by_class_name("sub_open")
    # print(len(outerLectures))
    connection.sendall(bytes(str(len(outerLectures)) + "\n", 'utf-8'))  # total lecture num
    realLectureIdx = 0
    lectureListURL = lectureUrlList[idx]
    driver.get(lectureListURL)

    totalLecturesList = []
    for i in range(len(outerLectures)):
        if check_exists_by_xpath("//*[@id=\"lecture_list\"]/div[1]/div[1]/div[" + str(i + 2) + "]"):
            totalLecturesList.append("//*[@id=\"lecture_list\"]/div[1]/div[1]/div[" + str(i + 2) + "]")
        else:
            break

    totalLecturesNum = len(totalLecturesList) - 1
    # print(totalLecturesNum)
    connection.sendall(bytes(str(totalLecturesNum) + "\n", 'utf-8'))  # real total num

    driver.get(mainLMSUrl)
    outerLectures = driver.find_elements_by_class_name("sub_open")
    # print(len(outerLectures))

    for outerLecturesIdx in range(totalLecturesNum):
        # print(outerLecturesIdx)
        removePopUp()
        outerLectures[outerLecturesIdx].click()
        lectureTitle = driver.find_element_by_class_name("welcome_subject").text
        lectureTitle = re.sub(r'\([^)]*\)', '', lectureTitle)
        lectureTitle = re.sub(r'\[[^)]*]', '', lectureTitle)
        lectureTitle = lectureTitle.replace('.', '').replace('#', '').replace('$', '')
        realLectureIdx += 1

        connection.sendall(bytes(lectureTitle + "\n", 'utf-8'))  # lecture name
        print(" " + lectureTitle)
        innerLecture = driver.find_element_by_xpath("//*[@id=\"menu_lecture_weeks\"]")
        innerLecture.click()

        isNotAvailPeriod = False

        if check_exists_by_id("per_text"):
            innerTotalLectureLength = driver.find_elements_by_class_name("wb-inner-wrap ")
            driver.find_element_by_xpath("/ html / body / div[3] / div[2] / div / div[2] / div[2] / div[2] / "
                                         "div / div[" + str(len(innerTotalLectureLength)) + "] / div").click()

            if check_exists_by_xpath(
                    "/ html / body / div[3] / div[2] / div / div[2] / div[2] / div[3] / div / div[1] / div"):
                # print("try to go prev lecture")

                if len(innerTotalLectureLength) > 1:
                    driver.find_element_by_xpath("/ html / body / div[3] / div[2] / div / div[2] / div[2] / div[2] / "
                                                 "div / div[" + str(
                        len(innerTotalLectureLength) - 1) + "] / div").click()
                    # print("succ to go prev lecture")

                else:
                    isNotAvailPeriod = True
                    # print("not exist prev lecture")

            if not isNotAvailPeriod:
                # print("exist")
                innerLecturePerTexts = driver.find_elements_by_id("per_text")
                connection.sendall(bytes(str(len(innerLecturePerTexts)) + "\n", 'utf-8'))  # inner lecture num

                innerLecturePeriod = driver.find_element_by_xpath(
                    "//*[@id=\"lecture_form\"] / div[1] / div / ul / li[1] / ol / li[2] / div[2] ").text
                # print(innerLecturePeriod)
                connection.sendall(bytes(innerLecturePeriod + "\n", 'utf-8'))  # inner lecture period

                for innerLectureIdx in range(len(innerLecturePerTexts)):
                    innerLecturePerText = innerLecturePerTexts[innerLectureIdx].text
                    connection.sendall(bytes(innerLecturePerText + "\n", 'utf-8'))  # inner lecture percentage
                    # print(innerLectureIdx, innerLecturePerText)
                    innerLectureIdx += 1

            else:
                connection.sendall(bytes("0\n", 'utf-8'))
                # print("isNotAvailPeriod")

        else:
            connection.sendall(bytes("0\n", 'utf-8'))
            # print("does not exist")

        driver.get(driver.find_element_by_xpath("//*[@id=\"menu_report\"]").get_attribute("href"))

        if check_exists_by_xpath("//*[@id=\"report_list\"]/table/tbody/tr[1]/td[1]"):
            assignmentNum = driver.find_element_by_xpath("//*[@id=\"report_list\"]/table/tbody/tr[1]/td[1]").text
            # print("total assignment num: ", assignmentNum)

            if assignmentNum != "조회할 자료가 없습니다" and assignmentNum != "No Data.":
                connection.sendall(bytes(assignmentNum + "\n", 'utf-8'))  # total assignment num

                for i in range(int(assignmentNum)):
                    isAssignmentInPeriod = driver.find_element_by_xpath("//*[@id=\"report_list\"]/table/tbody/tr["
                                                                        + str(i + 1) + "]/td[4]").text
                    if isAssignmentInPeriod == "종료":
                        connection.sendall(bytes("AssignmentDone\n", 'utf-8'))
                        break

                    assignmentName = driver.find_element_by_xpath("//*[@id=\"report_list\"]/table/tbody/tr["
                                                                  + str(i + 1) + "]/td[3]/a/div[1]").text.replace('[',
                                                                                                                  '') \
                        .replace(']', '').replace('.', '').replace('#', '').replace('$', '')
                    connection.sendall(bytes(assignmentName + "\n", 'utf-8'))  # get assignment name
                    # print(assignmentName)

                    isAssignmentSubmitted = driver.find_element_by_xpath("//*[@id=\"report_list\"]/table/tbody/tr["
                                                                         + str(i + 1) + "]/td[5]/img").get_attribute(
                        "title")
                    connection.sendall(
                        bytes(isAssignmentSubmitted + "\n", 'utf-8'))  # if is assignment in period, get submitted
                    # print(isAssignmentSubmitted)

                    assignmentPeriod = driver.find_element_by_xpath("//*[@id=\"report_list\"]/table/tbody/tr["
                                                                    + str(i + 1) + "]/td[8]").text
                    connection.sendall(
                        bytes(assignmentPeriod + "\n", 'utf-8'))  # if is assignment in period, get deadline
                    # print(assignmentPeriod)
            else:
                connection.sendall(bytes("AssignmentDone\n", 'utf-8'))

        # else:
        # print("no assignment")

        driver.get(mainLMSUrl)
        removePopUp()
        outerLectures = driver.find_elements_by_class_name("sub_open")

    connection.sendall(bytes("LectureDone\n", 'utf-8'))
    connection.sendall(bytes(str(realLectureIdx) + "\n", 'utf-8'))  # real lecture num
    # print("real lecture num:", realLectureIdx)
    driver.close()


def handle(connection, address):
    try:
        input = connection.recv(1024).decode('utf-8')
        # print("input: " + input)
        # print(input.split("\n"))

        if len(input.split("\n")) < 3:
            print(" Error Input Form")
            connection.sendall(bytes("Closing socket\n", 'utf-8'))
            print(" Close Client Socket")
            connection.close()
            print(" ======================================\n")
            print(" Waiting For Client ...")
            return

        else:
            schoolIdx = int(input.split("\n")[0])
            id = input.split("\n")[1]
            pw = input.split("\n")[2] + "\n"

            print(" " + schoolName[schoolIdx] + " -> id: " + id)
            #
            # if len(id) != 9:
            #     print(" Error ID Form")
            #     connection.sendall(bytes("Closing socket\n", 'utf-8'))
            #     print(" Close Client Socket")
            #     connection.close()
            #     print(" ======================================\n")
            #     print(" Waiting For Client ...")
            #     return

            if getLMSLogin(schoolIdx, str(id), str(pw)):
                connection.sendall(bytes("Success\n", 'utf-8'))
                # print("Login Success, Get LMS Subject")
                getLMSSubject(schoolIdx, connection)

            else:
                connection.sendall(bytes("Failed\n", 'utf-8'))

    except:
        print(" Problem Handling Request")

    connection.sendall(bytes("Closing Socket\n", 'utf-8'))
    print("\n Close Client Socket")
    connection.close()
    print(" ======================================\n")
    print(" Waiting For Client ...")


class Server(object):
    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = port
        self.socket = None

    def start(self):
        print(" Waiting For Client ...")
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.hostname, self.port))
        self.socket.listen(1)

        while True:
            conn, address = self.socket.accept()
            print("\n ====================================== ")
            print(" Connected by", address)
            print(time.strftime(' ***** %c *****', time.localtime(time.time())))
            process = multiprocessing.Process(target=handle, args=(conn, address))
            process.daemon = True
            process.start()
            print(" ====================================== ")


if __name__ == "__main__":
    server = Server("0.0.0.0", 38497)
    print(" Hello from Server!")

    try:
        server.start()
    except:
        print(" Unexpected exception")
    finally:
        print(" Shutting down")

        for process in multiprocessing.active_children():
            print(" Shutting down process %r", process)
            process.terminate()
            process.join()

    print(" All done")

