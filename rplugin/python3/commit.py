import os
import re
import sys
import urllib.parse as up
import urllib.request as ur

import pynvim

tturl = 'http://www.tzcoder.cn/acmhome/submitcode.do'
# http://www.tzcoder.cn/acmhome/submitcode.do


@pynvim.plugin
class Oj(object):
    def __init__(self, vim) -> None:
        self.vim = vim
        self.head = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}
        self.headers = {
            'Cookie': '',
        }

    @ pynvim.command("OjCommit")
    def commit(self) -> None:
        cookie = self.vim.vars["tzoj_cookie"]
        self.headers["Cookie"] = cookie
        if(cookie == ''):
            self.vim.command("echo 'not set cookie'")
            return
        b = self.vim.current.buffer
        problemId = str(b.name).replace('.cpp', '').replace(".c", '')[-4:]
        strtxt = "\n".join(b[:])
        fordate = {}
        fordate["contestId"] = "0"
        fordate["localIp"] = "60.180.247.18"
        fordate["problemId"] = problemId
        fordate["language"] = "C++"
        fordate["code"] = strtxt.encode("utf-8")
        refordate = up.urlencode(fordate).encode('utf-8')
        req = ur.Request(tturl, data=refordate, headers=self.headers)
        ur.urlopen(req)

    @ pynvim.command("OjLevel")
    def level(self) -> None:
        turl = 'http://www.tzcoder.cn/acmhome/problemList.do?method=show&type=1&page='
        b = self.vim.current.buffer
        anotherId = b.name.replace(".cpp", '')[-4:]
        a = int(anotherId)
        a = int((a-1000)/100)+1
        url = turl+str(a)
        req = ur.Request(url)
        response = ur.urlopen(req)
        html = response.read().decode('gbk')
        arule = r'<td class="EVENLINE"><DIV align="center">' + str(anotherId) +\
            r'[\s\S]+?<td class="EVENLINE"><DIV align="center">([\d]+?)' \
            r'</DIV></td>'
        brule = r'<td class="ODDLINE"><DIV align="center">' + str(anotherId) +\
            r'[\s\S]+?<td class="ODDLINE"><DIV align="center">([\d]+?)' \
            r'</DIV></td>'
        if int(anotherId) % 2 == 0:
            aclist = re.findall(arule, html)
            if not len(aclist):
                aclist = re.findall(brule, html)
        else:
            aclist = re.findall(brule, html)
            if not len(aclist):
                aclist = re.findall(arule, html)
        self.vim.command("echo 'this problem rank is "+aclist[0]+"'")

    def savelist(self, url):
        req = ur.Request(url, headers=self.head)
        response = ur.urlopen(req)
        html = response.read().decode('gbk')
        # print(html)
        rule = r'<a href="[^"]+">(\d{4})</a>'
        rulel = r'<div align="center"><h2><strong>已解答的较难题[\s\S]+?<strong>'
        html1 = re.search(rulel, html).group(0)
        print(html1)
        aclist = re.findall(rule, html1)
        return aclist

    @ pynvim.command("OjDifferent")
    def different(self):
        user = self.vim.vars["tzoj_compare_user"]
        cshtml = 'http://www.tzcoder.cn/acmhome/userDetail.do?&userName='
        aurl = cshtml+self.vim.vars["tzoj_user"]
        burl = cshtml+user
        alist = self.savelist(aurl)
        blist = self.savelist(burl)
        anotlist = [x for x in alist if x not in blist]
        # bnotlist = [y for y in blist if y not in alist]
        self.vim.command("vsplit")
        self.vim.command("e ~/myCode/clang/acm/tzoj/different/"+user+".txt")
        del self.vim.current.buffer[:]
        self.vim.current.buffer[0] = anotlist[0]
        for pro in anotlist[1:]:
            self.vim.current.buffer.append(pro)

    # @pynvim.command("OjDownloadAll")
