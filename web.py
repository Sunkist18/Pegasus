import socket

import requests
from bs4 import BeautifulSoup

login_url = 'https://e-learning.cnu.ac.kr/main/MainView.dunet'
llll = 'https://e-learning.cnu.ac.kr/login/doGetUserCountId.dunet'
mypage_url = 'http://e-learning.cnu.ac.kr/lms/myLecture/doListView.dunet'

if __name__ == '__main__':
    session = requests.session()
    login = {
        # UN 본교, CE 학점교류, LE 일반회원
        'group_cd': 'UN',
        'user_id': '202002570',
        'user_password': '010107'
        
        # 'is_local': 'Y',
        # 'user_ip': str(socket.gethostbyname(socket.getfqdn())),
        # 'sub_group_cd': ''
    }
    res = session.post(url=llll, data=login)
    res.raise_for_status()

    res = session.get(url=mypage_url)
    res.raise_for_status()

    soup = BeautifulSoup(res.text, 'html.parser')
    if soup.html.body is None:
        print('로그인 실패')
    """//*[@id="rows1"]/table/tbody/tr[1]/td[4]"""

    print(soup.html.body)
