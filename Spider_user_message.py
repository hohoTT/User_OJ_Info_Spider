# coding=utf8
import requests
import re
import logging


class Spider(object):
    def request(self, url):
        user_agent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) " \
                     "Chrome/44.0.2403.130 Safari/537.36"
        headers = {'User-Agent': user_agent}
        for i in range(0, 3):
            try:
                html = requests.get(url, headers=headers).content
                return html
            except Exception as e:
                if i == 2:
                    raise e
                continue

    # BestCoder
    def bestcoder(self, username):
        url = "http://bestcoder.hdu.edu.cn/rating.php?user=" + username
        try:
            html = self.request(url)
            logging.debug("finished BestCoder " + username)
            return {"rank": int(re.search("<span class=\"text-muted\">RANK</span>[\s]+"
                                          "<span class=\"bigggger\">(\d+)</span>", html).groups()[0]),
                    "rating": int(re.search("<span class=\"text-muted\">RATING</span>[\s]+"
                                            "<span class=\"bigggger\">(\d+)</span>",
                                            html).groups()[0])}
        except Exception as e:
            logging.error(e)
            return {"rank": 0, "rating": 0}

    # CodeForces
    def codefoces(self, username):
        url = "http://codeforces.com/profile/" + username
        try:
            html = self.request(url)
            logging.debug("finished CodeForces " + username)
            pattern = "<span style=\"font-weight:bold;\" class=\"user-\w+\">(\d+)</span>"
            return {"rank": int(re.search(pattern, html).groups()[0])}
        except Exception as e:
            logging.error(e)
            return {"rank": 0}

    # hudoj
    def hduoj(self, username):
        url = "http://acm.hdu.edu.cn/userstatus.php?user=" + username
        try:
            html = self.request(url)
            logging.debug("finished hudoj " + username)
            return {"rank": int(re.search("<td>Rank</td><td align=center>(\d+)</td>", html).groups()[0]),
                    "problems_submitted": int(re.search("<td>Problems Submitted</td><td align=center>(\d+)</td>", html).groups()[0]),
                    "problems_solved": int(re.search("<td>Problems Solved</td><td align=center>(\d+)</td>", html).groups()[0]),
                    "submissions": int(re.search("<td>Submissions</td><td align=center>(\d+)</td>", html).groups()[0]),
                    "accepted": int(re.search("<td>Accepted</td><td align=center>(\d+)</td>", html).groups()[0])}
        except Exception as e:
            logging.error(e)
            return {"rank": 0, "problems_submitted": 0,
                    "problems_solved": -1, "submissions": 0,
                    "accepted": 0}

BC_USERNAME = "KirinoP"
CF_USERNAME = "tourist"
HDU_USERNAME = "bluebird"

s = Spider()

print s.bestcoder(BC_USERNAME)
print s.codefoces(CF_USERNAME)
print s.hduoj(HDU_USERNAME)



