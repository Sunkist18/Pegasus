import socket
from pprint import pprint

import requests
from bs4 import BeautifulSoup

cnu_login = 'https://e-learning.cnu.ac.kr/login/doGetUserCountId.dunet'
cnu_main = 'http://e-learning.cnu.ac.kr/lms/myLecture/doListView.dunet'
class_page = 'http://e-learning.cnu.ac.kr/lms/class/classroom/doViewClassRoom_new.dunet'
course_page = 'http://e-learning.cnu.ac.kr/lms/class/courseSchedule/doListView.dunet'


def getDataFromCourse(course):
    return ' '.join(course.text.split()[:-1]), course['class_no'], {
        'mnid': "201008254671",
        'course_id': course['course_id'],
        'class_no': course['class_no'],
        'term_year': course['term_ym'],
        'term_cd': course['term_cd'],
        'subject_cd': course['subject_cd'],
        'user_no': course['user_no']
    }


def getDataFromLogin(userId, userPw):
    return {
        # UN 본교, CE 학점교류, LE 일반회원
        'group_cd': 'UN',
        'user_id': userId,
        'user_password': userPw,
        'is_local': 'Y',
        'user_ip': str(socket.gethostbyname(socket.getfqdn())),
        'sub_group_cd': ''
    }


def getDataFromVideoList(video_list):
    text_list = list(map(lambda x: x.text.replace('\r', '').replace('\t', '').replace('\n', ''), video_list))
    return [
        [0 if text_list[i] == '' else int(text_list[i][:-1]),
         text_list[i + 1].replace(' ~ ', ' ').split('    지각기간')[0],
         text_list[i + 2]]
        for i in range(0, len(text_list), 3)]


if __name__ == '__main__':
    # Initialization
    session = requests.session()

    # Login Process
    user_id, user_pw = '202002488', '010618'
    data = getDataFromLogin(user_id, user_pw)
    res = session.post(url=cnu_login, data=data)
    res.raise_for_status()
    res = session.get(url=cnu_main)
    res.raise_for_status()

    main_soup = BeautifulSoup(res.text, 'html.parser')
    if main_soup.html.body is None:
        print('로그인 실패')  # TODO
    for class_ in main_soup.find_all('a', class_='classin2'):
        class_name, class_no, data = getDataFromCourse(class_)

        res = session.post(url=class_page, data=data)
        res.raise_for_status()
        res = session.post(url=course_page, data=data)
        res.raise_for_status()

        course_soup = BeautifulSoup(res.text, 'html.parser')
        course_list = getDataFromVideoList(course_soup.find_all(class_='ag_c pd_ln'))
        print(class_name)
        pprint(course_list)

        # class_soup = BeautifulSoup(res.text, 'html.parser')
        # print(class_soup)
        # input('next')
