# coding=utf-8
import json
import sqlite3
import requests

from time import sleep
from thread_pool import ThreadPool
from bs4 import BeautifulSoup

FILE_SUBMISSION_ID = "submission_id_new.txt"


class SubmissionIdSpider(object):
    def __init__(self, contest_id):
        self.contest_id = contest_id

    def craw(self, from_page, to_page):
        f = open(FILE_SUBMISSION_ID, 'a')

        for page in range(from_page, to_page + 1):
            url = 'http://codeforces.com/contest/' + str(self.contest_id) + '/status/page/' + str(page)
            try:
                response = requests.get(url)
            except Exception as e:
                print "ERROR", e, "page = ", page
                continue
            soup = BeautifulSoup(response.content)

            for item in soup.find_all("a", class_="view-source"):
                f.write(item['submissionid']+"\n")

            print "finished page", page


class Spider(object):
    def __init__(self, token, cookie):
        self.token = token
        self.cookie = cookie
        self.db_path = "results.db"

    def db_connection(self):
        cx = sqlite3.connect(self.db_path)
        cu = cx.cursor()
        cu.execute("create table if not exists code (id integer primary key, "
                   "submission_id varchar(100), source text, verdict text, href text)")
        return cx, cu

    def job(self, submission_id):
        cx, cu = self.db_connection()

        url = "http://codeforces.com/data/submitSource"
        values = {"submission_id": submission_id, "csrf_token": self.token}
        user_agent = "Mozilla/5.0 (Windows NT 6.1; WOW64) " \
                     "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.130 Safari/537.36"

        try:
            response = requests.post(url, data=values,
                                     headers={"X-Csrf-Token": self.token,
                                              "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                                              "User-Agent": user_agent,
                                              "Cookie": self.cookie})

            content = json.loads(response.content)
        except Exception as e:
            print "ERROR", submission_id, e
            return

        cu.execute("insert into code(submission_id, source, verdict, href) values(?, ?, ?, ?)",
                   (submission_id, content["source"], content["verdict"], content["href"]))
        cx.commit()

        print "finished", submission_id

    def run(self):
        cx, cu = self.db_connection()
        pool = ThreadPool(size=20)
        pool.start()
        file_submission_id = open(FILE_SUBMISSION_ID)

        finished_submissions = [int(item[0]) for item in cu.execute("select submission_id from code")]
        all_submissions = [int(item) for item in file_submission_id.readlines()]

        for line in list(set(all_submissions).difference(set(finished_submissions))):
            sleep(0.2)
            pool.append_job(s.job, line)
        pool.join()
        pool.stop()

CONTEST_ID = 585
FROM_PAGE = 1
TO_PAGE = 100

# SubmissionIdSpider(CONTEST_ID).craw(FROM_PAGE, TO_PAGE)

TOKEN = "08c862e45ea4e3d900fe423974038d84"
COOKIE = "70a7c28f3de=0ktv7ft5v5tgldip7i; BD_vm1098=_; BD_vm1098=_; Hm_lvt_2e0d0c19ba238c377d" \
         "f12aab9ab19379=1444742113; Hm_lpvt_2e0d0c19ba238c377df12aab9ab19379=1444908445; " \
         "JSESSIONID=9CDDDEF5853C493B773F3F972C4A8F16-n1; 39ce7=CFNqxYZs; __utmt=1; __utma=" \
         "71512449.1470370097.1433660642.1444915088.1444982591.9; __utmb=71512449.1.10.1444982591; " \
         "__utmc=71512449; __utmz=71512449.1444737703.4.4.utmcsr=baidu|utmccn=(organic)|utmcmd=organic"

s = Spider(TOKEN, COOKIE)
s.run()

