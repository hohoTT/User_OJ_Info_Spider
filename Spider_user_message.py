# coding=utf8
import requests
import re


class Spider(object):
    def __init__(self, bc_username, cf_username, hdu_username):
        self.bc_username = bc_username
        self.cf_username = cf_username
        self.hdu_username = hdu_username

    def request(self, url):
        user_agent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) " \
                     "Chrome/44.0.2403.130 Safari/537.36"
        headers = {'User-Agent': user_agent}
        html = requests.get(url, headers=headers).content
        return html

    # BestCoder
    def bestcoder(self):
        url = "http://bestcoder.hdu.edu.cn/rating.php?user=" + self.bc_username
        try:
            html = self.request(url)
            return {"rank": int(re.search("<span class=\"text-muted\">RANK</span>[\s]+"
                                          "<span class=\"bigggger\">(\d+)</span>", html).groups()[0]),
                    "rating": int(re.search("<span class=\"text-muted\">RATING</span>[\s]+"
                                            "<span class=\"bigggger\">(\d+)</span>",
                                            html).groups()[0])}
        except Exception as e:
            print e
            return {"rank": -1, "rating": -1}

    # CodeForces
    def codefoces(self):
        url = "http://codeforces.com/profile/" + self.cf_username
        try:
            html = self.request(url)
            pattern = "<span style=\"font-weight:bold;\" class=\"user-\w+\">(\d+)</span>"
            return {"rank": int(re.search(pattern, html).groups()[0])}
        except Exception as e:
            print e
            return {"rank": -1}

    # hudoj
    def hduoj(self):
        url = "http://acm.hdu.edu.cn/userstatus.php?user=" + self.hdu_username
        try:
            html = self.request(url)
            return {"rank": int(re.search("<td>Rank</td><td align=center>(\d+)</td>", html).groups()[0]),
                    "problems_submitted": int(re.search("<td>Problems Submitted</td><td align=center>(\d+)</td>", html).groups()[0]),
                    "problems_solved": int(re.search("<td>Problems Solved</td><td align=center>(\d+)</td>", html).groups()[0]),
                    "submissions": int(re.search("<td>Submissions</td><td align=center>(\d+)</td>", html).groups()[0]),
                    "accepted": int(re.search("<td>Accepted</td><td align=center>(\d+)</td>", html).groups()[0])}
        except Exception as e:
            print e
            return {"rank": -1, "problems_submitted": -1,
                    "problems_solved": -1, "submissions": -1,
                    "accepted": -1}

BC_USERNAME = "aaa"
CF_USERNAME = "aa"
HDU_USERNAME = "bluebird"

s = Spider(BC_USERNAME, CF_USERNAME, HDU_USERNAME)

print s.bestcoder()
print s.codefoces()
print s.hduoj()



