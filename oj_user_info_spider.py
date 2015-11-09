# coding=utf8
import sqlite3
import requests
import datetime
import re
import logging
from thread_pool import ThreadPool
from db import BaseDBHandler


logging.basicConfig(level=logging.DEBUG)


class DBHandler(BaseDBHandler):
    def __init__(self, db_path="result.db"):
        self.db_path = db_path
        super(DBHandler, self).__init__(self.db_path)
        self.init_db()

    def init_db(self):
        self.execute_sql("CREATE TABLE IF NOT EXISTS user (username VARCHAR(20) PRIMARY KEY, "
                         "bc_name VARCHAR(20) UNIQUE, cf_name VARCHAR(20) UNIQUE, hdu_name VARCHAR(20) UNIQUE)")

        self.execute_sql("CREATE TABLE IF NOT EXISTS info (id INTEGER PRIMARY KEY AUTOINCREMENT, "
                         "username VARCHAR(20), bc_rank INTEGER, bc_rating INTEGER, cf_rank INTEGER, hdu_rank INTEGER,"
                         "hdu_problems_submitted INTEGER, hdu_problems_solved INTEGER, hdu_submissions INTEGER,"
                         "hdu_accepted INTEGER, crawling_date DATE)")

    def save_user_info(self, username, **kwargs):
        bc_result = kwargs["bestcoder"]
        cf_result = kwargs["codeforces"]
        hdu_result = kwargs["hduoj"]

        today = datetime.date.today()

        # 如果这个人没有今天的爬取记录，就先插入一条全是0的，后面只需要 update 就行了。
        if not self.execute_sql("SELECT * FROM info WHERE username = ? and crawling_date = ?",
                                (username, today)).fetchall():
            self.execute_sql("INSERT INTO info(username, bc_rank, bc_rating, cf_rank, hdu_rank, hdu_problems_submitted,"
                             "hdu_problems_solved, hdu_submissions, hdu_accepted, crawling_date) "
                             "VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                             (username, 0, 0, 0, 0, 0, 0, 0, 0, today))

        if bc_result != {}:
            self.execute_sql("UPDATE info SET bc_rank = ?, bc_rating = ? WHERE username =  ? AND crawling_date = ? ",
                             (bc_result["rank"], bc_result["rating"], username, today))
            return
        elif cf_result != {}:
            self.execute_sql("UPDATE info SET cf_rank = ? WHERE username =  ? AND crawling_date = ? ",
                             (cf_result["rank"], username, today))
            return
        else:
            self.execute_sql("UPDATE info SET hdu_rank = ?, hdu_problems_submitted = ?, "
                             "hdu_problems_solved = ?, hdu_submissions = ?, "
                             "hdu_accepted = ? WHERE username =  ? AND crawling_date = ? ",
                             (hdu_result["rank"], hdu_result["problems_submitted"],
                              hdu_result["problems_solved"], hdu_result["submissions"],
                              hdu_result["accepted"], username, today))


class Spider(object):
    def request(self, url):
        user_agent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) " \
                     "Chrome/44.0.2403.130 Safari/537.36"
        headers = {'User-Agent': user_agent}
        # 重试三次，还不行就抛异常
        for i in range(0, 3):
            try:
                response = requests.get(url, headers=headers)
                # 防止403等
                if response.status_code != 200:
                    raise ValueError()
                return response.content
            except Exception as e:
                if i == 2:
                    raise e
                continue

    def re_search(self, regex, content):
        result = re.search(regex, content)
        if result:
            return int(result.groups()[0])
        else:
            return 0

    # BestCoder
    def bestcoder(self, bc_name):
        url = "http://bestcoder.hdu.edu.cn/rating.php?user=" + bc_name
        try:
            html = self.request(url)
            logging.debug("finished BestCoder " + bc_name)
            return {"website": "bestcoder",
                    "rank": self.re_search("<span class=\"text-muted\">RANK</span>[\s]+"
                                           "<span class=\"bigggger\">(\d+)</span>", html),
                    "rating": self.re_search("<span class=\"text-muted\">RATING</span>[\s]+"
                                             "<span class=\"bigggger\">(\d+)</span>", html)}
        except Exception as e:
            logging.error(e)
            return {"website": "bestcoder",
                    "rank": 0, "rating": 0}

    # CodeForces
    def codefoces(self, cf_name):
        url = "http://codeforces.com/profile/" + cf_name
        try:
            html = self.request(url)
            logging.debug("finished CodeForces " + cf_name)
            pattern = "<span style=\"font-weight:bold;\" class=\"user-\w+\">(\d+)</span>"
            return {"website": "codeforces",
                    "rank": self.re_search(pattern, html)}
        except Exception as e:
            logging.error(e)
            return {"website": "codeforces",
                    "rank": 0}

    # hudoj
    def hduoj(self, hdu_name):
        url = "http://acm.hdu.edu.cn/userstatus.php?user=" + hdu_name
        try:
            html = self.request(url)
            logging.debug("finished hudoj " + hdu_name)
            return {"website": "hduoj",
                    "rank": self.re_search("<td>Rank</td><td align=center>(\d+)</td>", html),
                    "problems_submitted": self.re_search("<td>Problems Submitted</td><td align=center>(\d+)</td>",
                                                         html),
                    "problems_solved": self.re_search("<td>Problems Solved</td><td align=center>(\d+)</td>", html),
                    "submissions": self.re_search("<td>Submissions</td><td align=center>(\d+)</td>", html),
                    "accepted": self.re_search("<td>Accepted</td><td align=center>(\d+)</td>", html)}
        except Exception as e:
            logging.error(e)
            return {"website": "hduoj",
                    "rank": 0, "problems_submitted": 0,
                    "problems_solved": 0, "submissions": 0,
                    "accepted": 0}


d = DBHandler()
s = Spider()

user_list = d.get_user_list()

pool = ThreadPool(size=10)
pool.start()


def add_username(func, username, oj_username):
    data = func(oj_username)
    data["username"] = username
    return data


for user in user_list:
    pool.append_job(add_username, s.bestcoder, user[0], user[1])
    pool.append_job(add_username, s.codefoces, user[0], user[2])
    pool.append_job(add_username, s.hduoj, user[0], user[3])
pool.join()
pool.stop()


while not pool.results.empty():
    result = pool.results.get()
    username = result["username"]
    kwargs = {"bestcoder": {}, "codeforces": {}, "hduoj": {}}
    kwargs[result["website"]] = result

    d.save_user_info(username, **kwargs)
