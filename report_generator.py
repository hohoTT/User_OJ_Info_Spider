# coding=utf-8
import datetime
from db import BaseDBHandler


class ReportGenerator(BaseDBHandler):
    def __init__(self, db_path='result.db'):
        super(ReportGenerator, self).__init__(db_path)

    def fetch(self):
        dates = self.execute_sql("SELECT DISTINCT crawling_date FROM info ORDER BY crawling_date ASC").fetchall()
        users = self.get_user_list()

        results = []

        for user in users:
            tmp = []
            for date in dates:
                date = datetime.datetime.strptime(date[0], "%Y-%m-%d").date()
                r = self.execute_sql("SELECT * FROM info WHERE username = ? AND crawling_date = ?",
                                     (user[0], date)).fetchall()
                if r:
                    tmp.append(r[0])
                else:
                    tmp.append((-1, user[0], 0, 0, 0, 0, 0, 0, 0, 0, u'----'))
            results.append(tmp)
        return {"dates": dates, "users": users, "results": results}

    def _generate_thead(self, dates):
        html = u"<thead><tr><th>username</th><th>type</th>"
        for item in dates:
            html += (u"<th>" + str(item[0]) + u"</th>")
        html += u"</tr></thead>"
        return html

    def _generate_tbody(self, results):
        html = u"<tbody>"

        for item in results:
            html += u"<tr><td rowspan=\"8\">" + item[0][1] + u"</td>"
            for i in range(2, 10):
                if i == 2:
                    t = ""
                else:
                    t = u"<tr>"
                t += u"<td>" + \
                     ["BestCoder Rank", "BestCoder Rating", "CodeForces Rank", "HDUOJ Rank",
                      "HDUOJ Problems Submitted", "HDUOJ Problems Solved",
                      "HDUOJ Submissions", "HDUOJ Accepted"][i - 2] \
                     + u"</td>"

                for j in range(len(item)):
                    if j > 0:
                        if item[j][i] > item[j - 1][i]:
                            t += u"<td class=\"success\">" + str(item[j][i]) + u"</td>"
                        elif item[j][i] == item[j - 1][i]:
                            t += u"<td class=\"warning\">" + str(item[j][i]) + u"</td>"
                        else:
                            t += u"<td class=\"danger\">" + str(item[j][i]) + u"</td>"
                    else:
                        t += u"<td class=\"warning\">" + str(item[j][i]) + u"</td>"

                t += u"</tr>"
                html += t
        html += u"</tbody>"
        return html

    def generate_report(self):
        html = u"""<!DOCTYPE html>
            <html lang="zh-cn">
            <head>
                <meta charset="UTF-8">
                <title></title>
                <!-- 新 Bootstrap 核心 CSS 文件 -->
                <link rel="stylesheet" href="https://cdn.bootcss.com/bootstrap/3.3.5/css/bootstrap.min.css">
                <style>
                body{
                    margin: 30px;
                }
                </style>

            </head>
            <body>
                <div class="table-responsive">
                <table class="table table-bordered">
        """
        data = self.fetch()
        html += self._generate_thead(data["dates"])
        html += self._generate_tbody(data["results"])
        html += u"</table></div></html>"
        return html

    def save(self):
        report = self.generate_report()
        f = open("report.html", "w")
        f.write(report.encode("utf-8"))
        f.close()

g = ReportGenerator()
g.save()
