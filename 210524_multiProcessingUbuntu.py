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
    "https://lms.sungshin.ac.kr/ilos/main/member/login_form.acl",  # SungShin Women's
    "https://lms.knu.ac.kr/ilos/main/member/login_form.acl",  # KyeongBuk
    "https://eclass.hufs.ac.kr/ilos/main/member/login_form.acl",  # HUFS
    "https://eclass.sogang.ac.kr/ilos/main/member/login_form.acl",  # SoGang
    "https://ecampus.konkuk.ac.kr/ilos/main/member/login_form.acl",  # KonKuk
    "https://cyber.swu.ac.kr/ilos/main/member/login_form.acl"  # Seoul Women's
]

#
# # Add Main Page Here
# mainUrlList = [
#     "https://lms.sungshin.ac.kr/ilos/main/main_form.acl",  # SungShin Women's
#     "https://lms.knu.ac.kr/ilos/main/main_form.acl",  # KyeongBuk
#     "https://eclass.hufs.ac.kr/ilos/main/main_form.acl",  # HUFS
#     "https://eclass.sogang.ac.kr/ilos/main/main_form.acl",  # SoGang
#     "https://ecampus.konkuk.ac.kr/ilos/main/main_form.acl",  # KonKuk
#     "https://cyber.swu.ac.kr/ilos/main/main_form.acl"  # Seoul Women's
# ]

# Add Total Lecture Page Here

lectureUrlList = [
    "https://lms.sungshin.ac.kr/ilos/mp/course_register_list_form.acl",  # SungShin Women's
    "https://lms.knu.ac.kr/ilos/mp/course_register_list_form.acl",  # KyeongBuk
    "https://eclass.hufs.ac.kr/ilos/mp/course_register_list_form.acl",  # HUFS
    "https://eclass.sogang.ac.kr/ilos/mp/course_register_list_form.acl",  # SoGang
    "https://ecampus.konkuk.ac.kr/ilos/mp/course_register_list_form.acl",  # KonKuk
    "https://cyber.swu.ac.kr/ilos/mp/course_register_list_form.acl"  # Seoul Women's
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


def check_exists_by_class_multi_elements(className):
    try:
        driver.find_elements_by_class_name(className)
    except NoSuchElementException:
        return False
    return True


def removePopUp():
    try:
        # Remove Pop Up by Class 'x'
        popUp = driver.find_elements_by_class_name('x')
        for popUpUnit in popUp:
            popUpUnit.click()
    except:
        # print("no popUp")
        print("", end="")


def getLMSLogin(idx, id, password):
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-extensions')
    # Remove Below Line for Non-Background Page
    # options.add_argument('--headless')
    # options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')

    # Set Chrome Driver
    global driver
    driver = webdriver.Chrome('/home/compu/Downloads/UnivPlanner_ServerCode/chromedriver', chrome_options=options)

    # Go Login Page
    driver.get(loginUrlList[idx])
    print(" LMS Login Start :", end=" ")
    # print(driver.current_url)

    # Input ID and PW in Login Page
    elementID = driver.find_element_by_xpath("//*[@id=\"usr_id\"]")
    elementID.send_keys(id)

    elementPW = driver.find_element_by_xpath("//*[@id=\"usr_pwd\"]")
    elementPW.send_keys(password)

    try:
        # Remove Alert Window
        alert = driver.switch_to.alert
        alert.accept()
        print("Login Failed, Again?")
        driver.close()
        return False

    except:
        print("Login Success!")
        return True


def getLMSSubject(idx, connection):
    # Go Main LMS Page
    # mainLMSUrl = mainUrlList[idx]
    # driver.get(mainLMSUrl)

    # Change Language Setup
    languangeChange = Select(driver.find_element_by_css_selector('#LANG'))
    languangeChange.select_by_index(0)
    # print("Translate Done")

    # Get User Name
    userName = driver.find_element_by_xpath("//*[@id=\"user\"]").text

    # Send Name to Android Client
    connection.sendall(bytes(userName + "\n", 'utf-8'))  # name
    print("\n ***** " + userName + " ***** \n")

    # Get Lectures Link
    # outerLectures = driver.find_elements_by_class_name("sub_open")
    # print(len(outerLectures))
    connection.sendall(bytes("0\n", 'utf-8'))  # total lecture num
    realLectureIdx = 0

    # Go Total Lecture Page
    lectureListURL = lectureUrlList[idx]
    driver.get(lectureListURL)

    # Get Lectures Number, but Not Exactly cause Previous Period, so Named 'Candidate'
    candidate_lectures = 0

    if check_exists_by_class_multi_elements('content-title'):
        candidate_lectures = driver.find_elements_by_class_name('content-title')

    # Get Inner Lecture Links
    totalLecturesLink = []
    for i in range(len(candidate_lectures)):
        if check_exists_by_xpath("//*[@id=\"lecture_list\"]/div[1]/div[1]/div[" + str(i + 2) + "]/div/a"):
            lectureLink = driver.find_element_by_xpath("//*[@id=\"lecture_list\"]/div[1]/div[1]/div["
                                                       + str(i + 2) + "]/div/a").get_attribute('href')
            # print(lectureLink)
            totalLecturesLink.append(lectureLink)
        else:
            break

    # print(totalLecturesNum)
    connection.sendall(bytes(str(len(totalLecturesLink)) + "\n", 'utf-8'))  # real total num

    # Get Lecture Information
    for lecturesIdx in range(len(totalLecturesLink)):
        # Go Total Lecture Page
        driver.get(lectureListURL)
        # print('lecturesIdx', lecturesIdx)

        # Go Inner Lecture Page
        driver.find_element_by_xpath(
            "//*[@id=\"lecture_list\"]/div[1]/div[1]/div[" + str(lecturesIdx + 2) + "]/div").click()

        lectureTitle = driver.find_element_by_class_name("welcome_subject").text
        lectureTitle = re.sub(r'\([^)]*\)', '', lectureTitle)
        lectureTitle = re.sub(r'\[[^)]*]', '', lectureTitle)
        lectureTitle = lectureTitle.replace('.', '').replace('#', '').replace('$', '')
        realLectureIdx += 1

        # Send Lecture Title Name to Android Client
        connection.sendall(bytes(lectureTitle + "\n", 'utf-8'))  # lecture name
        print(" " + lectureTitle)
        innerLecture = driver.find_element_by_xpath("//*[@id=\"menu_lecture_weeks\"]")
        innerLecture.click()

        isNotAvailPeriod = False

        # Get Lecture Percentage
        if check_exists_by_id("per_text"):
            innerTotalLectureLength = driver.find_elements_by_class_name("wb-inner-wrap ")
            driver.find_element_by_xpath("/ html / body / div[3] / div[2] / div / div[2] / div[2] / div[2] / "
                                         "div / div[" + str(
                len(innerTotalLectureLength)) + "] / div").click()  # last inner lecture
            driver.implicitly_wait(0.1)

            # Check Lecture Period, Not in Period but Uploaded in Advance
            if check_exists_by_xpath(
                    "/html/body/div[3]/div[2]/div/div[2]/div[2]/div[3]/div[1]/div[1]/div"):
                # print("try to go prev lecture")

                prevLectureIdx = len(innerTotalLectureLength)

                # Check Previous Lecture Available
                if len(innerTotalLectureLength) > 1:
                    while prevLectureIdx > -1:  # 뒤부터 한 주차씩 돌면서 학습 기간인 강의 가져오기
                        if (check_exists_by_xpath(
                                '/html/body/div[3]/div[2]/div/div[2]/div[2]/div[3]/div/div[1]/div') and
                                driver.find_element_by_xpath(
                                    '/html/body/div[3]/div[2]/div/div[2]/div[2]/div[3]/div/div[1]/div').text == "학습 기간이 아닙니다."):
                            prevLectureIdx = prevLectureIdx - 1
                            driver.find_element_by_xpath(
                                "/ html / body / div[3] / div[2] / div / div[2] / div[2] / div[2] / "
                                "div / div[" + str(
                                    prevLectureIdx) + "] / div").click()
                        else:
                            break
                    # print("succ to go prev lecture")

                # UnAvailable Previous Lecture
                else:
                    isNotAvailPeriod = True
                    # print("not exist prev lecture")

            # Uploaded Properly Case
            if not isNotAvailPeriod:
                # print("exist")
                innerLecturePerTexts = driver.find_elements_by_id("per_text")
                tmp = driver.find_elements_by_id("per_text")[0].text

                connection.sendall(bytes(str(len(innerLecturePerTexts)) + "\n", 'utf-8'))  # inner lecture num (n차시)
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

        # '''''''''''''''''''''''''''no exist assignment tap'''''''''''''''''''''''''''''''''''#
        try:
            driver.get(driver.find_element_by_xpath("//*[@id=\"menu_report\"]").get_attribute("href"))
        except:
            print("no assignment tap")
            connection.sendall(bytes("AssignmentDone\n", 'utf-8'))
        # ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''#

        # Get Assignment
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
                                                                    + str(
                        i + 1) + "]/td[8]").text  # 지각제출 마감일 : 2021.~~~

                    # slice (시작연도 2를 찾아서 거기부터 넘겨주기)
                    slice_period = assignmentPeriod[assignmentPeriod.find("2"):]
                    connection.sendall(
                        bytes(slice_period + "\n", 'utf-8'))  # if is assignment in period, get deadline
                    # print(assignmentPeriod)
            else:
                connection.sendall(bytes("AssignmentDone\n", 'utf-8'))
        # else:
        #     print("no assignment tap")

        driver.get(lectureListURL)
        # removePopUp()
        # outerLectures = driver.find_elements_by_class_name("sub_open")

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
            print(" Close Client Socket error")
            connection.close()
            print(" ======================================\n")
            print(" Waiting For Client ...")
            return

        else:
            schoolIdx = int(input.split("\n")[0])
            id = input.split("\n")[1]
            pw = input.split("\n")[2] + "\n"

            print(" " + schoolName[schoolIdx] + " -> id: " + id)

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
