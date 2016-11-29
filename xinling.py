#coding:utf-8
from EasyLogin import EasyLogin#假设已经pip install bs4 requests pymysql
from time import sleep
from bs4 import BeautifulSoup
from mpms import MultiProcessesMultiThreads#假设mpms正常工作
import socket
import random
real_create_conn = socket.create_connection
ip='10.78.54.{}'.format(random.randint(101,110))
def set_src_addr(*args):
    address, timeout = args[0], args[1]
    source_address = (ip, 0)
    return real_create_conn(address, timeout, source_address)
socket.create_connection = set_src_addr
import requests,sys,pymysql,re,os


DOMAIN = "http://www.cc98.org"#假设当前网络能访问到本域名
COOKIE = {"BoardList":"BoardID=Show",
          "ASPSESSIONIDSCRQCTTR":"DCCBDFHDIIFJHOMHEIGAGHFP","upNum":"0",
          "aspsky":"username=%E5%BC%80%E6%A3%AE&usercookies=3&userid=551585&useranony=&userhidden=2&password=941ca9f6f80cd00f",
          "autoplay":"True", "owaenabled":"True"}#假设本账号的Cookie不会过期
boardlist=[182, 114, 100, 152, 235, 562, 80, 459, 135, 81, 287, 15, 146, 173, 515, 68, 563, 180, 102, 437, 581, 339, 399, 91, 104, 283, 372, 147, 611, 736, 743, 318, 328, 248, 226, 164, 101, 58, 314, 711, 741, 255, 198, 211, 144, 263, 584, 312, 258, 296, 357, 158, 334, 105, 628, 284, 315, 749, 509, 748, 564, 326, 241, 23, 30, 594, 323, 264, 229, 186, 623, 184, 744, 487, 401, 572, 383, 165, 86, 449, 187, 99, 57, 39, 261, 551, 599, 484, 329, 85, 217, 214, 139, 580, 392, 170, 742, 320, 212, 17, 545, 593, 371, 252, 576, 308, 67, 290, 247, 169, 622, 344, 341, 266, 455, 25, 321, 148, 485, 362, 391, 377, 193, 154, 352, 145, 75, 74, 621, 417, 324, 316, 194, 191, 16, 103, 256, 179, 620, 538, 519, 481, 462, 374, 304, 288, 274, 178, 307, 285, 268, 239, 183, 493, 411, 330, 232, 747, 598, 595, 560, 475, 393, 319, 234, 473, 272, 754, 625, 583, 550, 518, 499, 47, 469, 351, 282, 281, 26, 246, 236, 233, 203, 188, 142]

#conn = pymysql.connect(user='root',passwd='fox12345',host='10.71.115.234',db='cc98')#假设本机已经启动mysqld，建立好了cc98数据库，有表bbs_<板块id>
def db():
    global conn
    conn = pymysql.connect(user='root',passwd='ilovecc98butwhereisCC(*?',host='127.0.0.1',port=53306,db='cc98',charset='utf8',init_command="set NAMES utf8")
    conn.encoding = "utf8"
    return conn

db()

def filter_emoji(desstr,restr='emoji'):  
    try:  
        co = re.compile(u'[\U00010000-\U0010ffff]')  
    except re.error:  
        co = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')  
    return co.sub(restr, desstr)

def createTable(boardid,big=""):
    sql = """
CREATE TABLE `{}bbs_{}` (
  `id` int(11) NOT NULL,
  `lc` int(255) NOT NULL,
  `posttime` datetime NOT NULL,
  `edittime` datetime NOT NULL,
  `user` varchar(66) NOT NULL,
  `content` longtext NOT NULL,
  `gettime` datetime NOT NULL,
  PRIMARY KEY (`id`,`lc`,`edittime`,`posttime`,`user`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
ALTER TABLE `{}bbs_{}`
ADD INDEX `a2` (`user`) ,
ADD INDEX `a4` (`id`) ,
ADD INDEX `a5` (`lc`);
""".format(big,boardid,big,boardid)
    global conn
    conn=db()
    cur = conn.cursor()
    try:
        cur.execute(sql)
        conn.commit()
    except:
        pass
    conn=db()
    
def getNewPost():
    a = EasyLogin(cookie=COOKIE)
    result=[]
    for page in range(5,0,-1):
        a.get("{}/queryresult.asp?page={}&stype=3".format(DOMAIN,page))
        l=a.getList("dispbbs.asp")
        for i in l:
            if "http" in i:
                continue
            element = [getPart(i,"boardID=","&"),getPart(i,"&ID=","&")]
            if element not in result:
                result.append(element)
    return result

def getHotPost():
    a = EasyLogin(cookie=COOKIE)
    result=[]
    a.get("{}/hottopic.asp".format(DOMAIN))
    l=a.getList("dispbbs.asp")
    for i in l:
        if "http" in i:
            continue
        element = [getPart(i,"boardid=","&"),getPart(i,"&id=","&")]
        if element not in result:
            result.append(element)
    return result

def getPart(source,left,right):
    return source.split(left)[1].split(right)[0]#在"leftcontentright"中返回content，假设source中一定包含left

def getBoardID(bigboardid=0):
    a = EasyLogin(cookie=COOKIE)
    a.get("{}/list.asp?boardid={}".format(DOMAIN,bigboardid) if bigboardid!=0 else DOMAIN)
    l = a.getList("list.asp?boardid")
    result=set()
    for i in l:
        if '&' in i :
            continue
        result.add(getPart(i,"boardid=","&"))
    return [int(i) for i in result]

def getBoardSize(boardid):
    a = EasyLogin(cookie=COOKIE)
    a.get("{}/list.asp?boardid={}".format(DOMAIN,boardid))
    size=list(a.b.find('td',attrs={'style':'text-wrap: none; vertical-align: middle; margin: auto; text-align: left;'}).find_all('b'))[1].text
    return int(size)

def getBoardPage(boardid,page):
    a = EasyLogin(cookie=COOKIE)
    a.get("{}/list.asp?boardid={}&page={}".format(DOMAIN,boardid,page))
    result = set()
    for i in a.getList("dispbbs.asp?boardID="):
        result.add(getPart(i,"&ID=","&"))#假设帖子列表中的<a href='dispbbs.asp?boardID=326&ID=4593133&star=1&page=1'>
    return [i for i in result]

def getBBS(boardid,id,big):
    #print(id)
    a = EasyLogin(cookie=COOKIE)
    result = []
    star = 1
    a.get("{}/dispbbs.asp?BoardID={}&id={}&star=1".format(DOMAIN,boardid,id))
    try:
        number = int(a.b.find("span",attrs={"id":"topicPagesNavigation"}).find("b").text)#假设<span id="topicPagesNavigation">本主题贴数 <b>6</b>
    except:
        return [boardid,id,[],big]
    pages = (number//10 + 1) if number%10 !=0 else number//10#假设每页只有10个楼层
    lastpage = number - 10*(pages-1)
    for star in range(1,pages+1):
        if star!=1:
            a.get("{}/dispbbs.asp?BoardID={}&id={}&star={}".format(DOMAIN,boardid,id,star))
        else:
            title = a.b.title.text.strip(" » CC98论坛")#帖子标题使用页面标题，假设页面标题的格式为"title &raquo; CC98论坛"
            result.append([0,"",title,"1970-01-01 08:00:01","1970-01-01 08:00:01"])
            #print(title)
        for i in range(1,11 if star!=pages else lastpage+1):#最后一页没有第lastpage+1个楼层
            #print(star,i)
            lc = (star-1)*10 + i
            floorstart = a.b.find("a",attrs={"name":"{}".format(i if i!=10 else 0)})
            if floorstart is None:
                result.append([lc,"98Deleter",">>>No Content<<<","1970-01-01 08:00:01","1970-01-01 08:00:01"])
                continue
            table = floorstart.next_sibling.next_sibling#假设楼层内容开始的table前都有<a name="1"></a>

            #print(table)
            for t in list(table.next_siblings)[0:20]: #由于BeautifulSoup太渣,事实上table还有一部分
                if "IP" in str(t):
                    table_part2 = t
                    break     
            #print(table_part2)
            user = table.find('b').text#假设表格中第一个加粗<b>的就是发帖用户名
            #print("{},{},{},{}".format(id,star,user,i))
            lastedit = table_part2.find("span",attrs={"style":"color: gray;"})#假设本楼层发生了编辑，最后的编辑时间<span style="color: gray;">本贴由作者最后编辑于 2016/10/28 21:33:56</span>

            lastedittime = " ".join(lastedit.text.split()[-2:]).replace("/","-") if lastedit != None else "1970-01-01 08:00:01"#没有编辑就返回0
            #print(lastedittime)
            posttime = table.find_next("td",attrs={"align":"center"}).get_text(strip=True).replace("/","-")#发帖时间，注意find_next有可能找到下个楼层，希望没错			<td class="tablebody1" valign="middle" align="center" width="175">
            #假设发帖时间的HTML：
            #				<a href=#>
            #				<img align="absmiddle" border="0" width="13" height="15" src="pic/ip.gif" title="点击查看用户来源及管理&#13发贴IP：*.*.*.*"></a>
            #		2016/10/28 21:32:45
            #			</td>

            #print(posttime)
            contentdiv = table.find('article').find('div')
            content = contentdiv.text if contentdiv is not None else ">>>No Content<<<"
            #print(content)
            result.append([lc,user,content,posttime,lastedittime])
        #break
    return [boardid,id,result,big]

def handler(meta,boardid,id,result,big):
    if len(result)==0: #or boardid==146:
        return
    try:
        print(ip,boardid,id,result[0][2],len(result))
    except:
        print(boardid,id,">>>Cannot Print<<<",len(result))
    global conn
    sql = "insert ignore into {}bbs_{}(id,lc,user,content,posttime,edittime,gettime) values ".format(big,boardid)
    for i in result:
        sql += "({},{},\"{}\",\"{}\",\"{}\",\"{}\",date_add(now(),interval 8 hour)),".format(id,i[0],pymysql.escape_string(i[1]),pymysql.escape_string(i[2]),i[3],i[4])
        #print(sql)
    sql = filter_emoji(sql[:-1])#.replace("\n","<br>")
    #print(sql)
    cur = conn.cursor()
    try:
        cur.execute("SET NAMES utf8;")
    except:
        db()
    try:
        cur.execute(sql)
        conn.commit()
    except pymysql.err.ProgrammingError as e:
        createTable(boardid,big=big)
        cur.execute(sql)
        conn.commit()
    except Exception as e:
        print(e)
        

def deleteredundance(boardid,big=""):
    print(boardid)
    print(">>>Delete Redundance<<<")
    sql = """DELETE t2
FROM
	`{}bbs_{}` AS t1,
	`{}bbs_{}` AS t2
WHERE
	t2.gettime > t1.gettime
AND t2.id = t1.id
AND t2.lc = t1.lc
AND t2.user = t1.user
AND t2.posttime = t1.posttime
AND t2.edittime = t1.edittime;""".format(big,boardid,big,boardid)
    global conn
    cur = conn.cursor()
    try:
        cur.execute(sql)
        conn.commit()
        print(">>>Delete Finished<<<")
    except Exception as e:
        print(e)

def spyBoard(boardid=182,pages=None,spytimes=1,sleeptime=86400,processes=2,threads=2):
    if pages==None:
        pages=getBoardSize(boardid)
    print("Try to get {} pages".format(pages))
    m = MultiProcessesMultiThreads(getBBS,handler,processes=processes,threads_per_process=threads)
    t = 0
    while t<spytimes:
        workload = []
        for j in range(1,pages+1):
            thispage = getBoardPage(boardid,j)
            if thispage==[]: break
            for i in thispage:
                if [boardid,i] not in workload:
                    workload.append([boardid,i])
                    m.put([boardid,i,"big"])
        t += 1
        sleep(sleeptime)
        #deleteredundance(boardid,big="big")
    return

def spyNew(spytimes=10,sleeptime=300,processes=5,threads=4):
    m = MultiProcessesMultiThreads(getBBS,handler,processes=processes,threads_per_process=threads)
    t = 0
    while t<spytimes:
        workload = []
        for boardid,i in getHotPost():
            boardid,i = int(boardid),int(i)
            if [boardid,i] not in workload:
                workload.append([boardid,i])
                m.put([boardid,i,""])
        for boardid,i in getNewPost():
            boardid,i = int(boardid),int(i)
            if [boardid,i] not in workload:
                workload.append([boardid,i])
                m.put([boardid,i,""])
        for boardid in [182,100]:
          for i in getBoardPage(boardid,1):
            boardid,i = int(boardid),int(i)
            if [boardid,i] not in workload:
                workload.append([boardid,i])
                m.put([boardid,i,""])

        t += 1
        sleep(sleeptime)
        tmp = []
        for boardid,i in workload:
            if boardid not in tmp:
                #deleteredundance(boardid)
                tmp.append(boardid)
    m.close()
    return

def main():
    import sys
    if len(sys.argv)>1:
        if sys.argv[1]=="del":
            global boardlist
            for i in boardlist:
                deleteredundance(i)
                #deleteredundance(i,big="big")
            return
        else:
            spyBoard(boardid=int(sys.argv[1]))
    else:
        spyNew(spytimes=1)

def modifyTable(boardid,big=""):
    print(">>>Modify {}<<<".format(boardid),end="")
    sql = """ALTER TABLE `{}bbs_{}`
MODIFY COLUMN `edittime`  datetime NOT NULL AFTER `posttime`,
DROP PRIMARY KEY,
ADD PRIMARY KEY (`id`, `lc`, `edittime`,`posttime`,`user`);""".format(big,boardid)
    global conn
    cur = conn.cursor()
    try:
        cur.execute(sql)
        conn.commit()
        print("OK")
    except Exception as e:
        print("Error:")
        print(e)


def test():
            global boardlist
            for i in boardlist:
                deleteredundance(i)
                modifyTable(i)
                #modifyTable(i,big="big")

##print(getBoardSize(182))
##GetBBS
    #for j in range(2,100):
    #    for i in getBoardPage(100,j):
    #        getBBS(100,4661275)
##DeleteRedundance
    #deleteredundance(182)
    ##GetBoardID
    #print(sorted(getBoardID()))
    #result = []
    #for i in getBoardID():
    #    result.extend(getBoardID(i))
    #print(result)
    #return result
##CreateTable
    #boardlist = [284,7, 15, 16, 17, 20, 21, 23, 25, 26, 28, 30, 36, 38, 39, 40, 41, 42, 47, 48, 49, 50, 52, 58, 60, 67, 68, 75, 77, 80, 81, 83, 84, 85, 86, 91, 99, 100, 101, 102, 103, 104, 105, 114, 115, 119, 122, 129, 135, 136, 139, 140, 142, 144, 145, 146, 147, 148, 149, 151, 152, 154, 155, 157, 158, 164, 165, 169, 170, 173, 176, 179, 180, 182, 183, 184, 186, 187, 188, 190, 191, 192, 193, 194, 195, 198, 203, 204, 205, 206, 207, 208, 211, 212, 213, 214, 216, 217, 221, 222, 224, 226, 229, 232, 233, 234, 235, 236, 239, 241, 245, 246, 247, 249, 254, 256, 258, 261, 262, 263, 264, 266, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279, 281, 282, 283, 285, 286, 287, 288, 290, 292, 294, 295, 296, 298, 303, 304, 306, 307, 308, 310, 311, 312, 314, 315, 316, 318, 319, 320, 321, 323, 324, 325, 326, 328, 329, 330, 334, 339, 341, 344, 346, 347, 351, 352, 353, 355, 357, 361, 362, 363, 367, 368, 369, 371, 372, 375, 377, 383, 391, 392, 393, 399, 401, 402, 403, 404, 405, 406, 408, 412, 417, 422, 423, 427, 430, 431, 432, 433, 434, 436, 437, 440, 442, 446, 447, 448, 449, 450, 451, 452, 454, 455, 457, 459, 460, 461, 462, 465, 467, 468, 469, 471, 472, 473, 475, 480, 481, 482, 483, 484, 485, 486, 489, 491, 492, 493, 494, 498, 499, 501, 502, 503, 504, 505, 506, 507, 511, 513, 514, 515, 518, 519, 520, 535, 537, 538, 540, 545, 546, 548, 549, 550, 551, 559, 560, 562, 563, 564, 568, 569, 572, 574, 575, 576, 578, 579, 580, 581, 582, 587, 588, 589, 590, 591, 592, 593, 594, 595, 596, 597, 598, 599, 600, 601, 602, 603, 605, 606, 607, 610, 611, 613, 614, 615, 616, 618, 620, 621, 622, 623, 624, 625, 626, 628, 629, 630, 631, 632, 633, 634, 635, 640, 642, 710, 711, 713, 714, 723, 724, 726, 727, 728, 733, 736, 741, 742, 743, 744, 745, 747, 748, 749, 750, 751, 752, 753, 754]
    #for i in boardlist:
    #    createTable(i)
##GetNewPost
    #return getNewPost()
##SpyBoard
    #spyBoard(boardid=182,spytimes=1)
##GetHotPost
    #print(getHotPost())

if __name__ == "__main__": 
    if len(sys.argv)>1 and sys.argv[1]=="test":
        test()
    else:
        main()
        print("Quit!!!")
    os._exit(1)