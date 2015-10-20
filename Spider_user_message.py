# coding=utf8
import requests
import re
import logging
import sqlite3
from thread_pool import ThreadPool

logging.basicConfig(level=logging.DEBUG)


class DbHandler(object):
    def __init__(self):
        self.db_path = 'D:/result.db'

    def db_user_connection(self):
        cx = sqlite3.connect(self.db_path)
        cu = cx.cursor()
        cu.execute("create table if not exists user (username varchar(20) primary key, "
                   "bc_name varchar(20) UNIQUE, cf_name varchar(20) UNIQUE, hdu_name varchar(20) UNIQUE)")
        return cx, cu

    def db_info_connection(self):
        cx = sqlite3.connect(self.db_path)
        cu = cx.cursor()
        cu.execute("create table if not exists info (username varchar(20) primary key, "
                   "bc_rank integer, bc_rating integer, cf_rank integer, hdu_rank integer,"
                   "hdu_problems_submitted integer, hdu_problems_solved integer, hdu_submissions integer,"
                   "hdu_accepted integer)")
        return cx, cu

    def get_user_list(self):
        cx, cu = self.db_user_connection()
        cu.execute("select * from user")
        return cu.fetchall()

    def save_user_info(self, username, **kwargs):
        bc_result = kwargs["bestcoder"]
        cf_result = kwargs["codeforces"]
        hdu_result = kwargs["hduoj"]
        cx, cu = self.db_info_connection()
        cu.execute("select * from info where username = ?", (username, ))
        results = cu.fetchall()
        if not results:
            cu.execute("insert into info values(?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       (username, 0, 0, 0, 0, 0, 0, 0, 0))

        if bc_result != {}:
            cu.execute("update info set bc_rank = ?, bc_rating = ? where username =  ? ",
                       (bc_result["rank"], bc_result["rating"], username))
        elif cf_result != {}:
            cu.execute("update info set cf_rank = ? where username =  ? ", (cf_result["rank"], username))
        else:
            cu.execute("update info set hdu_rank = ?, hdu_problems_submitted = ?, "
                       "hdu_problems_solved = ?, hdu_submissions = ?, "
                       "hdu_accepted = ? where username =  ? ",
                       (hdu_result["rank"], hdu_result["problems_submitted"],
                        hdu_result["problems_solved"], hdu_result["submissions"],
                        hdu_result["accepted"], username))
        cx.commit()


class Spider(object):
    def request(self, url):
        user_agent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) " \
                     "Chrome/44.0.2403.130 Safari/537.36"
        headers = {'User-Agent': user_agent}
        for i in range(0, 3):
            try:
                response = requests.get(url, headers=headers)
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
                    "problems_submitted": self.re_search("<td>Problems Submitted</td><td align=center>(\d+)</td>", html),
                    "problems_solved": self.re_search("<td>Problems Solved</td><td align=center>(\d+)</td>", html),
                    "submissions": self.re_search("<td>Submissions</td><td align=center>(\d+)</td>", html),
                    "accepted": self.re_search("<td>Accepted</td><td align=center>(\d+)</td>", html)}
        except Exception as e:
            logging.error(e)
            return {"website": "hduoj",
                    "rank": 0, "problems_submitted": 0,
                    "problems_solved": 0, "submissions": 0,
                    "accepted": 0}


USERNAME = "hohoTT"
BC_USERNAME = "KirinoP"
CF_USERNAME = "tourist"
HDU_USERNAME = "bluebird"

d = DbHandler()
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
