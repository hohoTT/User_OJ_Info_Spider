# coding=utf-8
import requests
from bs4 import BeautifulSoup

page = 1

count = 0

for i in range(1, 101):
    page = i
    url = 'http://codeforces.com/contest/585/status/page/' + str(page)
    response = requests.get(url)
    soup = BeautifulSoup(response.content)
    file_object = open("SubId\submissionId_" + str(i) + ".txt", 'a')

    for item in soup.find_all("a", class_="view-source"):
        # print item['submissionid']
        file_object.write(item['submissionid']+"\n")
        count += 1

print count

file_object.close()



