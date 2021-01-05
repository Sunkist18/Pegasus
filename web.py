import socket
from pprint import pprint

import requests
from bs4 import BeautifulSoup


def error(msg, place, kill=True):
    print('[*] 치명적인 오류가 발생했습니다')
    print(f'[*] {msg} ({place})')
    if kill:
        exit(1)


def getDataFromCourse(course):
    return ' '.join(course.text.split()[:-1]), course['course_id'], course['class_no'], {
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


def login_process(userId, userPw):
    cnu_login = 'https://e-learning.cnu.ac.kr/login/doGetUserCountId.dunet'
    cnu_main = 'http://e-learning.cnu.ac.kr/lms/myLecture/doListView.dunet'
    data = getDataFromLogin(userId, userPw)
    res = session.post(url=cnu_login, data=data)
    res.raise_for_status()
    res = session.get(url=cnu_main)
    res.raise_for_status()
    ret = BeautifulSoup(res.text, 'html.parser')
    if ret.html.body is None:
        # TODO 로그인은 에러가 아님. 반복문 추가바람
        error('로그린 에러', 'login_process')
    return ret


def getLecture(data):
    course_page = 'http://e-learning.cnu.ac.kr/lms/class/courseSchedule/doListView.dunet'
    res = session.post(url=course_page, data=data)
    res.raise_for_status()
    lecture_soup = BeautifulSoup(res.text, 'html.parser')
    return getDataFromVideoList(lecture_soup.find_all(class_='ag_c pd_ln'))


def data_process(soup):
    database_ = {}
    for class_ in soup.find_all('a', class_='classin2'):
        class_page = 'http://e-learning.cnu.ac.kr/lms/class/classroom/doViewClassRoom_new.dunet'
        class_name, class_id, class_no, data = getDataFromCourse(class_)
        # subject 기록
        database_[class_name] = {'no': class_no, 'id': class_id}

        res = session.post(url=class_page, data=data)
        res.raise_for_status()

        # 강의수강
        database_[class_name]['lecture'] = getLecture(data)

        # # TODO REMOVE THIS
        data['mnid'] = '201008945595'
        # res = session.post(data=data)
        # # TODO END

        database_[class_name]['notice'] = None  # TODO 과목공지 만들 것
        database_[class_name]['assignment'] = None  # TODO 과제제출 만들 것
    return database_


if __name__ == '__main__':
    # Initialization
    session = requests.session()

    # Login Process
    user_id, user_pw = '202002570', '010107'
    main_soup = login_process(user_id, user_pw)

    database = data_process(main_soup)
    pprint(database)
