from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
import requests
import csv
import os
from bs4 import BeautifulSoup
import time
import sys
import re

form_class = uic.loadUiType("main_window.ui")[0]

class MyWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.save_email = []
        self.blog_name = ''
        self.list_dict = {}
        self.setupUi(self)
        self.pushButton0.clicked.connect(self.btn0_clicked)
        self.pushButton1.clicked.connect(self.btn1_clicked)
        self.pushButton2.clicked.connect(self.btn2_clicked)    #self.btn2_clicked)
        self.radio1.setChecked(True)
        #self.statusBar = QStatusBar(self)
        #self.setStatusBar(self.statusBar)

        #self.radio1.clicked.connect(self.radioButtonClicked)
        #self.radio2.clicked.connect(self.radioButtonClicked)

        #self.timer = QTimer(self)
        #self.timer.start(1000) # a second
        #self.timer.timeout.connect(self.timeout) # pratice event per a second

    def call_url(self, url): #call url
        response = requests.get(url)
        html = response.text
        soup = BeautifulSoup(html, 'lxml')
        return soup

    def find_char(self, char_name, char_list): #특정 단어가 있는 것(하나 있는 경우)
        for i in range(len(char_list)):
            if char_name in str(char_list[i]):
                return char_list[i]
                break


    def find_char2(self, char_name, char_list, c): #특정 단어가 있는 것들 리스트에 저장
        for i in range(len(char_list)):
            if char_name in str(char_list[i]):
                c.append(char_list[i])


    def btn0_clicked(self):

        ### 모든 부분 초기화시키기 ###
        for i in range(self.listWidget2.count()):  #검색버튼 누를 때 초기화시키기
           item = self.listWidget2.item(0)
           self.listWidget2.takeItem(self.listWidget2.row(item))

        for i in range(self.listWidget.count()):
            self.listWidget.item(i).setText('')

        self.blog_name = self.lineEdit.text()  ## blogname 저장
        self.list_dict = {}
        ### 초기화 작업 끝 ###



        self.listWidget2.addItem('[전체] 블로그 전체 수집')
        self.listWidget2.addItem('[이웃] 블로그 이웃 수집')
        set_number = self.listWidget2.count()


        url_1 = "http://blog.naver.com/PostList.nhn?from=postList&blogId={}&categoryNo=0&currentPage=1".format(self.blog_name)
        soup_1 = self.call_url(url_1)

        blog_all_list = soup_1.select('.border li a')

        c = []
        self.find_char2('category', blog_all_list, c)

        #for blog_list in blog_all_list:
         #   if 'category' in str(blog_list):
          #      c.append(blog_list)
        self.list_dict[0] = 0
        for i in range(len(c)):
            try:
                cat_name = c[i].get_text()
                self.listWidget2.addItem('[목록] {}'.format(cat_name))
                cat_number = int(c[i]['class'][2].split('|')[2])
                #self.list_dict[cat_name] = cat_number
                self.list_dict[i+set_number] = cat_number

            except:
                continue


        item = self.listWidget.item(0)
        item.setText("블로그명: {}".format(self.blog_name))
        QApplication.processEvents()

        item = self.listWidget.item(1)
        item.setText("블로그 이웃/목록 검색 완료")
        QApplication.processEvents()

        item = self.listWidget.item(2)
        item.setText("이메일 추출 가능/목록 선택 후 추출 시작")
        QApplication.processEvents()



    ### MAIN ###
    def btn1_clicked(self):
        self.save_email = [] #클릭 누를 때마다 초기화


        list_number = self.listWidget2.currentRow()

        if list_number == 0:
            self.connect_email('ViewMoreFollowings')
            self.connect_email('ViewMoreFollowers')
            self.comment_email()


        elif list_number == 1:
            self.connect_email('ViewMoreFollowings')
            self.connect_email('ViewMoreFollowers')
        else:
            self.comment_email()



    def btn2_clicked(self):
        sys.exit() # 작업 종료



    def comment_email(self):
        try:
            category_n = self.list_dict[self.listWidget2.currentRow()]

            url_1 = "http://blog.naver.com/PostList.nhn?from=postList&blogId={}&categoryNo={}&currentPage=1".format(self.blog_name, category_n)
            soup_1 = self.call_url(url_1)
            page_number = int(soup_1.select('strong.itemSubjectBoldfont')[0].get_text()) #int 중요함


            if category_n == 0:
                item = self.listWidget.item(6)
                item.setText("전체 글 {}개 수집 진행 중...".format(page_number))
                QApplication.processEvents()
            else:
                item = self.listWidget.item(6)
                item.setText(" {}의 글 {}개 수집 진행 중...".format(self.listWidget2.currentItem().text(), page_number))
                QApplication.processEvents()


            for j in range(1,page_number+1):

                item = self.listWidget.item(9)
                item.setText("{}/{}".format(j, page_number))
                QApplication.processEvents()

                time.sleep(0.5)
                url_2 = "http://blog.naver.com/PostList.nhn?from=postList&blogId={}&categoryNo={}&currentPage={}".format(self.blog_name, category_n, j)
                soup_2 = self.call_url(url_2)

                a= soup_2.select('p.url')
                b= a[0]['id']
                c= b.split('_')

                log_number = int(c[2]) #0383496209 이런 거

                url_3 = 'http://blog.naver.com/CommentList.nhn?blogId={}&logNo={}&currentPage=&isMemolog=false&focusingCommentNo=&showLastPage=true&shortestContentAreaWidth=false'.format(self.blog_name,log_number)
                soup_3 = self.call_url(url_3)

                id_list = soup_3.select('.nick')

                for each in id_list:
                    try:
                        a = each['href'].split('/')

                        if self.radio2.isChecked():
                            email = a[3]
                        else:
                            email = a[3] + '@naver.com'

                        self.save_email.append(email)


                        item = self.listWidget.item(7)
                        item.setText("총 추출된 이메일 수 {}개".format(len(self.save_email)))
                        QApplication.processEvents()

                        item = self.listWidget.item(11)
                        item.setText("[중복 제거 후]")
                        QApplication.processEvents()

                        item = self.listWidget.item(12)
                        item.setText("총 {}개 저장 완료".format(len(list(set(self.save_email)))))
                        QApplication.processEvents()
                    except:
                        continue
                pure_email = list(set(self.save_email))

                if self.radio2.isChecked():
                    self.blog_csv('id', pure_email)
                else:
                    self.blog_csv('email', pure_email)

        except IndexError:
            QMessageBox.about(self, 'Message', '수집할 이메일이 없습니다.')


    def connect_email(self, kind):
        try:
            url_1 = "http://blog.naver.com/PostList.nhn?from=postList&blogId={}&categoryNo=0&currentPage=1".format(self.blog_name)
            soup_1 = self.call_url(url_1)

            buddy = soup_1.select('div#blog_buddyconnect iframe')
            aaa = buddy[0]['src']

            p = re.compile('widgetSeq=\d+')
            bbb = p.findall(aaa)[0]
            q = re.compile('\d+')
            widget_number = int(q.findall(bbb)[0])

            url = 'http://section.blog.naver.com/connect/ViewMoreBuddyPosts.nhn?blogId={}&widgetSeq={}'.format(self.blog_name,widget_number)
            soup_2 = self.call_url(url)

            find_gs = soup_2.select('script')
            ccc = self.find_char('gsBlogNo', find_gs)
            p = re.compile('gsBlogNo\s=\s\D*\d+') #  \D*의 사용으로 중간에 문자가 있든 없든 상관없음
            find_gs2 = p.findall(str(ccc)) #gsBlogNo = '19467274'
            q = re.compile('\d+')
            find_gs3 = q.findall(find_gs2[0]) # ['19467274']
            gs_number = int(find_gs3[0])


            item = self.listWidget.item(6)
            item.setText("블로그 이웃 이메일 수집 진행 중...")
            QApplication.processEvents()

            item = self.listWidget.item(9)
            item.setText("")
            QApplication.processEvents()



            k=1  #프로그램이 작업 중이라 중간에 작업을 끝내려면 X키를 눌러서 종료하셔야합니다. 조금만 기다려주세요!
            while True:
                try:
                    time.sleep(0.5)

                    apple = []
                    follower_url = 'http://section.blog.naver.com/connect/{}.nhn?blogId={}&currentPage={}&targetBlogNo={}'.format(kind,self.blog_name, k, gs_number)

                    c_soup = self.call_url(follower_url)

                    if kind == 'ViewMoreFollowers': # 나를 추가한 이웃
                        one_page_info = c_soup.select('dt.desc a')
                    else: # 내가 추가한 이웃
                        one_page_info = c_soup.select('dd.desc a')



                    for b in one_page_info: # b = each_info 개개인 정보
                        try:
                            if 'http://blog.naver.com/' in str(b):  #이 양식을 따라야 해줌
                                each_id = b['href'].split('/')[3]
                            elif '.blog.me' in str(b):
                                each_id = b['href'].split('.blog.me')[0][7:]
                            else:
                                continue

                            if self.radio2.isChecked():
                                email = each_id
                            else:
                                email = each_id + '@naver.com'

                            self.save_email.append(email)
                            apple.append(email)

                            item = self.listWidget.item(7)
                            item.setText("총 추출된 이메일 수 {}개".format(len(self.save_email)))
                            QApplication.processEvents()

                            item = self.listWidget.item(11)
                            item.setText("[중복 제거 후]")
                            QApplication.processEvents()

                            item = self.listWidget.item(12)
                            item.setText("총 {}개 저장 완료".format(len(list(set(self.save_email)))))
                            QApplication.processEvents()

                        except: #그냥 오류발생 시
                            continue
                    if len(apple) == 0:
                        break
                    k += 1
                    pure_email = list(set(self.save_email))

                    if self.radio2.isChecked():
                        self.blog_csv('id', pure_email)
                    else:
                        self.blog_csv('email', pure_email)

                except:
                    continue
        except IndexError:
            QMessageBox.about(self, 'Message', '이웃을 공개하지 않는 블로거입니다.')


    def blog_csv(self, method, email_list):
        with open('{}/blog_{}_{}.csv'.format(method,self.blog_name,self.listWidget2.currentRow()+1), 'w', newline='', encoding='euc-kr') as f:
            writer = csv.writer(f)
            for each_email in email_list:
                writer.writerow([each_email])



if __name__ == "__main__":

    if not os.path.isdir('email'):
        os.mkdir('email')

    if not os.path.isdir('id'):
        os.mkdir('id')


    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()