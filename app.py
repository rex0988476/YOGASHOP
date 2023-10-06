#約定俗成:
#1.會員跟管理員id至少6碼, 需包含英文小寫及數字
#2.商品id固定4碼, 第一碼為1或2, 1代表書(1001~1999), 2代表cd(2001~2999)
#3.每筆交易(buy)如無分數評價則設-1,無文字評價則為空值(NULL)
#4.交易紀錄id預設5碼,第一筆從10000開始
#5.商品如無綜合評價則設-1
#6.transaction_record 表格的 transaction_status屬性為0代表未出貨,1代表已出貨,2代表已送達未領貨,3代表已送達已領貨,預設為0
#7.transaction_record_goods 表格的 goods_status屬性為0代表未打包,1代表已打包
#8.QA_id固定3碼,100~999
#9.goods表格的supply_status為1則為供貨狀態,0為暫停供貨
#10.bid表格的bid_status,'0'為未開始,'1'為進行中,'2'為待結帳,3為已結束(刪除)
#11.goods表格的can_bid為0為不可競標,為1為可競標
#12.bid_id從1000開始
#13.consult表格id從100000開始

#localtime = time.localtime()
#result = time.strftime("%Y-%m-%d %H:%M:%S", localtime)
from glob import glob
from flask import Flask
from flask import render_template
from flask import request
import random
import os
import mysql.connector
import time
import datetime
import statistics
connection = mysql.connector.connect(host='localhost',#創建連線
                                    port='3306',
                                    user='root',
                                    password='hsieh17')
#                                   database='database_system' ) #可先預設要使用的資料庫

cursor = connection.cursor()#開始使用

#use
cursor.execute("USE `database_system`;")

#image path
BASEPATH = os.path.join(os.path.dirname(__file__), 'static','uploads')




#全域變數/常數
IS_LOGIN = "" #0管理員 1使用者
USER_AVATAR_SRC="/static/uploads" #<img> src in html
SRC = "/static/uploads"
USER_NAME=""
USER_ID=""
USER_PHONENUMBER=""
USER_BANKACC=""
USER_CARD=""
USER_PASSWORD = ""
MANAGER_ID="000000"
MANAGER_PASSWORD="yoga7414"
SIMULATE_ARRIVAL_TIME = 60
SIMULATE_LIMIT_GET_TIME = 120
SIMULATE_GET_DAY = 1
is_stop_supply= "0"
############################副函式
def few_mins_later(DELTA_TIME):#現在到DELTA_TIME分鐘的時間
    localtime = time.localtime()
    front_DATE = time.strftime("%Y-%m-%d ", localtime)
    mi2 = str(int(time.strftime("%H", localtime)))
    if int(time.strftime("%M", localtime))+int(DELTA_TIME)>59:
        middle_DATE = str(DELTA_TIME)
        mi2 = str(int(time.strftime("%H", localtime))+1)
    else:    
        middle_DATE = str(int(time.strftime("%M", localtime))+int(DELTA_TIME))
    if len(middle_DATE)==1:
        middle_DATE="0"+middle_DATE
    behind_DATE = time.strftime(":%S", localtime)
    rEND_DATE = f'{front_DATE}{mi2}:{middle_DATE}{behind_DATE}'
    return rEND_DATE
#struct_time = time.strptime('2022-05-24', "%Y-%m-%d")
#few = few_days_later(struct_time,7)
#print(struct_time,few)
def few_days_later(localtime,DELTA_TIME):#localtime到DELTA_TIME天後的時間
    front_DATE = time.strftime("%Y-%m-", localtime)
    middle_DATE = str(int(time.strftime("%d", localtime))+DELTA_TIME)
    if len(middle_DATE)==1:
        middle_DATE="0"+middle_DATE
    behind_DATE = time.strftime(" %H:%M:%S", localtime)
    sEND_DATE = f'{front_DATE}{middle_DATE}{behind_DATE}'
    struct_time = time.strptime(sEND_DATE, "%Y-%m-%d %H:%M:%S")
    return struct_time

def two_mins_later(localtime):#localtime到2分鐘後的時間
    front_DATE = str(time.strftime("%Y-%m-%d ", localtime))
    mi2 = str(int(time.strftime("%H", localtime)))
    if int(time.strftime("%M", localtime))+2>59:
        middle_DATE = "02"
        mi2 = str(int(time.strftime("%H", localtime))+1)
    else:    
        middle_DATE = str(int(time.strftime("%M", localtime))+2)
    if len(middle_DATE)==1:
        middle_DATE="0"+middle_DATE
    behind_DATE = str(time.strftime(":%S", localtime))
    sEND_DATE = f'{front_DATE}{mi2}:{middle_DATE}{behind_DATE}'
    print(sEND_DATE)
    struct_time = time.strptime(sEND_DATE, "%Y-%m-%d %H:%M:%S")
    return struct_time

def random_arrival_date(buy_date_d):
    #now=datetime.datetime.now()
    delta = datetime.timedelta(random.randint(3,7))
    n_days=buy_date_d+delta
    arrival_date = n_days.strftime('%Y-%m-%d %H:%M:%S')
    return arrival_date
############################網頁顯示區
app = Flask(__name__)

@app.route("/",methods=['GET','POST'])
def home():
    global IS_LOGIN
    global USER_AVATAR_SRC
    global USER_NAME
    global SRC
    cursor = connection.cursor()

    #取得資料庫所有商品資料
    sql="SELECT * FROM `goods` WHERE `goods_quantity` > 0 AND `supply_status` = 1;"
    cursor.execute(sql)
    goods_datas = cursor.fetchall()
    if goods_datas:
        i=0
        goods = []
        while i<len(goods_datas):
            goodsub = []
            j=0
            while j<4 and i<len(goods_datas):
                member_id = goods_datas[i][0]
                goods_id = str(goods_datas[i][1])
                goods_name = goods_datas[i][2]
                goods_picture = goods_datas[i][3]
                
                if goods_picture:
                    
                    goods_picture = SRC + "/" +member_id + "/" + goods_picture
                else:
                    goods_picture = ""
                goods_author = goods_datas[i][5]
                goods_price = goods_datas[i][6]
                goods_rate = goods_datas[i][9]
                #商品分類
                if str(goods_id[0])=="1":#書
                    sql=f"SELECT `category` FROM `goods_book_category`,`goods` WHERE `goods_book_id` = `goods_id` AND `goods_id` = {goods_id};"
                    cursor.execute(sql)
                    categories = cursor.fetchall()
                    goodsub.append({"member_id":member_id,"goods_id":goods_id,"goods_name":goods_name,"goods_picture":goods_picture,"goods_author":goods_author,"goods_price":goods_price,"goods_rate":goods_rate,"categories":categories})
                elif str(goods_id[0])=="2":#CD 
                    sql=f"SELECT `category` FROM `goods_CD`,`goods` WHERE `goods_CD_id` = `goods_id` AND `goods_id` = {goods_id};"
                    cursor.execute(sql)
                    categories = cursor.fetchall()
                    goodsub.append({"member_id":member_id,"goods_id":goods_id,"goods_name":goods_name,"goods_picture":goods_picture,"goods_author":goods_author,"goods_price":goods_price,"goods_rate":goods_rate,"categories":categories})
                i+=1
                j+=1
            goods.append(goodsub)
    #取得評價前三高的商品圖片跟id
    slideshow = []
    sql=f"SELECT `goods_id`,`goods_picture`,`member_id` FROM `goods` WHERE `goods_quantity` > 0 AND `supply_status` = 1 ORDER BY `goods_rate` DESC LIMIT 3;"
    cursor.execute(sql)
    top3_fetch = cursor.fetchall()
    if top3_fetch:
        i=0
        while i<len(top3_fetch):
            top3_id = str(top3_fetch[i][0])
            top3_picture = top3_fetch[i][1]
            if top3_picture:
                top3_picture = SRC + "/" + str(top3_fetch[i][2]) + "/" + top3_picture
            else:
                top3_picture = ""
            i+=1
            slideshow.append({"goods_id":top3_id,"goods_picture":top3_picture})
    connection.commit()
    return render_template("home.html",slideshow=slideshow,IS_LOGIN=IS_LOGIN,USER_NAME=USER_NAME,USER_AVATAR_SRC=USER_AVATAR_SRC,goods=goods)

@app.route("/logout",methods=['GET','POST'])
def logout():
    global IS_LOGIN
    global USER_AVATAR_SRC
    global USER_NAME
    global USER_CARD
    global USER_ID
    global USER_PHONENUMBER
    global USER_BANKACC
    global USER_PASSWORD
    IS_LOGIN = ""
    USER_AVATAR_SRC="/static/uploads"
    USER_NAME = ""
    USER_ID = ""
    USER_PHONENUMBER = ""
    USER_BANKACC = ""
    USER_CARD = ""
    USER_PASSWORD = ""
    return render_template("login.html",IS_LOGIN=IS_LOGIN)
    
def checktimebreak():
    global USER_ID
    global MANAGER_ID
    global SIMULATE_LIMIT_GET_TIME
    #超時未寄出
    sql=f"SELECT `transaction_id`,`buy_date` FROM `transaction_record` WHERE `transaction_status` = 0;"
    cursor.execute(sql)
    transaction_id_fetch = cursor.fetchall()
    if transaction_id_fetch:
        i=0
        timebreakout_tid = []
        #判斷時間是否超過
        while i<len(transaction_id_fetch):
            need_check_time = time.strptime(str(transaction_id_fetch[i][1]),"%Y-%m-%d %H:%M:%S")
            #seven_days_later = few_days_later(need_check_time,7)
            seven_days_later = two_mins_later(need_check_time)
            localtime = time.localtime()
            print(type(localtime),type(seven_days_later))
            print("ls",localtime,seven_days_later)
            loc = time.strftime("%Y-%m-%d %H:%M:%S", localtime)
            sev = time.strftime("%Y-%m-%d %H:%M:%S", seven_days_later)
            print("sls",loc,sev)
            if localtime>seven_days_later:#超時,刪除物流並送檢舉
                timebreakout_tid.append(transaction_id_fetch[i][0])
            i+=1
        #返回所有購買數量
        i=0
        while i<len(timebreakout_tid):
            sql=f"SELECT `transaction_id`,`goods_id`,`goods_amount` FROM `transaction_record_goods` WHERE `transaction_id` = {timebreakout_tid[i]};"
            cursor.execute(sql)
            goods_id_amount_fetch = cursor.fetchall()
            if goods_id_amount_fetch:
                j=0
                while j<len(goods_id_amount_fetch):
                    print("id,amount",goods_id_amount_fetch[j][1],goods_id_amount_fetch[j][2])
                    sql=f"UPDATE `goods` SET `goods_quantity` = `goods_quantity` + {goods_id_amount_fetch[j][2]} WHERE `goods_id` = {goods_id_amount_fetch[j][1]};"
                    cursor.execute(sql)
                    j+=1
            i+=1
        #找出沒打包的戰犯
        i=0
        reportmember_id = []
        while i<len(timebreakout_tid):
            sql=f"SELECT `goods_id` FROM `transaction_record_goods` WHERE `transaction_id` = {timebreakout_tid[i]} AND `goods_status` = 0;"
            cursor.execute(sql)
            goods_id_fetch = cursor.fetchall()
            if goods_id_fetch:
                j=0
                while j<len(goods_id_fetch):
                    sql=f"SELECT `member_id` FROM `goods` WHERE `goods_id` = '{goods_id_fetch[j][0]}';"
                    cursor.execute(sql)
                    member_id_fetch = cursor.fetchall()
                    print("gid,mid",goods_id_fetch[j][0],member_id_fetch)
                    if member_id_fetch:
                        reportmember_id.append(member_id_fetch[0][0])
                    j+=1
            i+=1
        
        #刪除交易紀錄
        i=0
        while i<len(timebreakout_tid):
            sql=f"DELETE FROM `transaction_record` WHERE `transaction_id` = {timebreakout_tid[i]};"
            cursor.execute(sql)
            i+=1
        
        #送去檢舉
        i=0
        while i<len(reportmember_id):
            sql=f"SELECT COUNT(*) FROM `report` WHERE `member_id` = '{MANAGER_ID}' AND `seller_id` = '{reportmember_id[i]}';"
            cursor.execute(sql)
            reported_fetch = cursor.fetchall()
            if reported_fetch and reported_fetch[0][0]==0:
                print("repf",reported_fetch)
                sql=f"insert into `report` values('{MANAGER_ID}','{reportmember_id[i]}','超時未寄出');"
                cursor.execute(sql)
            i+=1
    #超時未領貨
    #判斷時間是否超過
    #sql=f"SELECT `arrival_date`,`transaction_id`,`member_id` FROM `transaction_record` WHERE `transaction_status` = 2;"
    sql=f"SELECT `buy_date`,`transaction_id`,`member_id` FROM `transaction_record` WHERE `transaction_status` = 2;"
    cursor.execute(sql)
    check_time_fetch = cursor.fetchall()
    if check_time_fetch:
        i=0
        while i<len(check_time_fetch):
            localtime = time.localtime()
            result = time.strftime("%Y-%m-%d %H:%M:%S", localtime)
            simulate_time = datetime.datetime.strptime(str(result),'%Y-%m-%d %H:%M:%S')
            buy_date =check_time_fetch[i][0]
            d = simulate_time - buy_date
            print(simulate_time,buy_date)
            print(d.seconds,SIMULATE_LIMIT_GET_TIME)
            if d.seconds > SIMULATE_LIMIT_GET_TIME:#超時,返回物品數量,刪除物流並送檢舉
                sql=f"UPDATE `transaction_record` SET `transaction_status` = 2 WHERE `transaction_id` = {check_time_fetch[i][1]};"
                cursor.execute(sql)      
            #need_check_time = time.strptime(str(check_time_fetch[i][0]),"%Y-%m-%d %H:%M:%S")
            #seven_days_later = few_days_later(need_check_time,7)
            #seven_days_later = two_mins_later(need_check_time)
            #localtime = time.localtime()
            #print("ls",localtime,seven_days_later)
            #loc = time.strftime("%Y-%m-%d %H:%M:%S", localtime)
            #sev = time.strftime("%Y-%m-%d %H:%M:%S", seven_days_later)
            #print("sls",loc,sev)
            #if localtime>CHECK: 
            #if localtime>seven_days_later:
                #取得所有物品數量並返回
                sql=f"SELECT `transaction_id`,`goods_id`,`goods_amount` FROM `transaction_record_goods` WHERE `transaction_id` = {check_time_fetch[i][1]};"
                cursor.execute(sql)
                goods_id_amount_fetch = cursor.fetchall()
                if goods_id_amount_fetch:
                    j=0
                    while j<len(goods_id_amount_fetch):
                        sql=f"UPDATE `goods` SET `goods_quantity` = `goods_quantity` + {goods_id_amount_fetch[j][2]} WHERE `goods_id` = {goods_id_amount_fetch[j][1]};"
                        cursor.execute(sql)
                        j+=1
                #刪除物流
                sql=f"DELETE FROM `transaction_record` WHERE `transaction_id` = {check_time_fetch[i][1]};"
                cursor.execute(sql)
                #檢舉
                sql=f"SELECT COUNT(*) FROM `report` WHERE `member_id` = '{MANAGER_ID}' AND `seller_id` = '{check_time_fetch[i][2]}';"
                cursor.execute(sql)
                reported_fetch = cursor.fetchall()
                if reported_fetch and reported_fetch[0][0]==0:
                    sql=f"insert into `report` values('{MANAGER_ID}','{check_time_fetch[i][2]}','超時未領貨');"
                    cursor.execute(sql)
            i+=1
    connection.commit()
    return 1

@app.route("/seller.html",methods=['GET','POST'])
def seller():
    global IS_LOGIN
    global USER_AVATAR_SRC
    global USER_NAME
    global USER_CARD
    global USER_ID
    global SRC
    cursor = connection.cursor()
    #取得身分
    #member_id = request.values['id']
    #如果有登入
    #本人賣場
    seller = {}
    if IS_LOGIN == "1":
        need_send = "0"
        id = request.args.get('id')
        seller = {}
        member_id = ""
        is_self=0
        if id:#他人賣場
            member_id = id
            sql=f"SELECT `name`,`picture` FROM `member` WHERE `member_id` = '{member_id}';"
            cursor.execute(sql)
            seller_info = cursor.fetchall()
            if seller_info:
                seller_name = seller_info[0][0]
                seller_picture = seller_info[0][1]
                if seller_picture:
                    seller_picture = SRC + "/" + member_id + "/" + seller_picture
                else:
                    seller_picture = ""
                seller = {"seller_id":member_id,"seller_name":seller_name,"seller_picture":seller_picture}
        else:#本人
            checktimebreak()
            is_self = 1
            member_id = USER_ID
            #判斷是否需出貨
            sql = f"SELECT `goods_status` FROM `transaction_record_goods` WHERE `transaction_record_goods`.`goods_id` IN (SELECT `goods`.`goods_id` FROM `goods` WHERE `goods`.`member_id` = '{member_id}');"
            cursor.execute(sql)
            goods_status_fetch = cursor.fetchall()
            if goods_status_fetch:
                i=0
                while i<len(goods_status_fetch):
                    goods_status = str(goods_status_fetch[i][0])
                    print("gs",goods_status)
                    if goods_status == "0":
                        need_send = "1"
                    i+=1
            seller = {"seller_id":member_id,"seller_name":USER_NAME,"seller_picture":USER_AVATAR_SRC}
        #讀取商品資料
        if is_self==1:
            sql=f"SELECT * FROM `goods` WHERE `member_id` = '{member_id}';"
        else:
            sql=f"SELECT * FROM `goods` WHERE `member_id` = '{member_id}' AND `goods_quantity` > 0 AND `supply_status` = 1;"
        cursor.execute(sql)
        goods_datas = cursor.fetchall()
        goods = []

        if goods_datas:
            i=0
            while i<len(goods_datas):
                goodsub = []
                j=0
                while j<4 and i<len(goods_datas):
                    goods_id = str(goods_datas[i][1])
                    goods_name = goods_datas[i][2]
                    goods_picture = goods_datas[i][3]
                    if goods_picture:
                        goods_picture = SRC + "/" +member_id + "/" + goods_picture
                    else:
                        goods_picture = ""
                    goods_author = goods_datas[i][5]
                    goods_price = goods_datas[i][6]
                    goods_rate = goods_datas[i][9]
                    #商品分類
                    if str(goods_id[0])=="1":#書
                        sql=f"SELECT `category` FROM `goods_book_category`,`goods` WHERE `goods_book_id` = `goods_id` AND `goods_id` = {goods_id};"
                        cursor.execute(sql)
                        categories = cursor.fetchall()
                        goodsub.append({"goods_id":goods_id,"goods_name":goods_name,"goods_picture":goods_picture,"goods_author":goods_author,"goods_price":goods_price,"goods_rate":goods_rate,"categories":categories})
                    elif str(goods_id[0])=="2":#CD 
                        sql=f"SELECT `category` FROM `goods_CD`,`goods` WHERE `goods_CD_id` = `goods_id` AND `goods_id` = {goods_id};"
                        cursor.execute(sql)
                        categories = cursor.fetchall()
                        goodsub.append({"goods_id":goods_id,"goods_name":goods_name,"goods_picture":goods_picture,"goods_author":goods_author,"goods_price":goods_price,"goods_rate":goods_rate,"categories":categories})
                    i+=1
                    j+=1
                #print(goodsub)
                goods.append(goodsub)
        print(IS_LOGIN,2)  
        return render_template("seller.html",need_send=need_send,seller=seller,IS_LOGIN=IS_LOGIN,USER_CARD=USER_CARD,USER_NAME=USER_NAME,USER_AVATAR_SRC=USER_AVATAR_SRC,goods=goods,USER_ID=USER_ID)
    else:
        print(IS_LOGIN,1)
        return render_template("seller.html",seller=seller,IS_LOGIN=IS_LOGIN)


@app.route("/search_result.html",methods=['GET','POST'])
def search_result():
    global IS_LOGIN
    global USER_AVATAR_SRC
    global USER_NAME
    cursor = connection.cursor()
    searched_goods_id = []
    #取得輸入
    check = "search_text" in request.form
    search_text=""
    if check:
        search_text=request.values['search_text']
    print(search_text)
    #取得分類
    #書為0~12,CD為13~30
    add_categories = []
    i=0
    while i<13:
        cname = f"{i}"
        check = cname in request.form
        if check:
            cvalue = str(request.values[cname])
            add_categories.append(cvalue)
        i+=1
    i=13
    while i<31:
        cname = f"{i}"
        check = cname in request.form
        if check:
            cvalue = str(request.values[cname])
            add_categories.append(cvalue)
        i+=1
    
    #抓搜尋文字
    #名稱 作者 敘述 出版社 書分類 CD分類
    select_name = [f"SELECT `goods_id` FROM `goods` WHERE `goods_quantity` > 0 AND `supply_status` = 1 AND `goods_name` LIKE '%{search_text}%';",
                   f"SELECT `goods_id` FROM `goods` WHERE `goods_quantity` > 0 AND `supply_status` = 1 AND `goods_author` LIKE '%{search_text}%';",
                   f"SELECT `goods_id` FROM `goods` WHERE `goods_quantity` > 0 AND `supply_status` = 1 AND `goods_describe` LIKE '%{search_text}%';",
                   f"SELECT `goods_book_id` FROM `goods_book`,`goods` WHERE `goods_id` = `goods_book_id` AND `goods_quantity` > 0 AND `supply_status` = 1 AND `goods_book_publisher` LIKE '%{search_text}%';",
                   f"SELECT DISTINCT `goods_book_id` FROM `goods_book_category`,`goods` WHERE `goods_id` = `goods_book_id` AND `goods_quantity` > 0 AND `supply_status` = 1 AND `category` LIKE '%{search_text}%';",
                   f"SELECT DISTINCT `goods_CD_id` FROM `goods_CD`,`goods` WHERE `goods_id` = `goods_CD_id`  AND `goods_quantity` > 0 AND `supply_status` = 1 AND `category` LIKE '%{search_text}%';"]
    k=0
    while k<5:
        sql = f"{select_name[k]}" 
        cursor.execute(sql)
        print(sql)
        search_fetch = cursor.fetchall()
        if search_fetch:
            i=0
            while i<len(search_fetch):
                is_repeat = 0
                j=0
                #判斷是否重複
                while j<len(searched_goods_id):
                    if str(search_fetch[i][0]) == searched_goods_id[j]:
                        is_repeat = 1
                        break
                    j+=1
                #如果沒有重複再加進去
                if is_repeat == 0:
                    searched_goods_id.append(str(search_fetch[i][0]))
                i+=1
        k+=1

    #分類篩選
    i=0
    searched_and_classified_goods_id = []
    print(searched_goods_id)
    while i<len(searched_goods_id) and len(add_categories) > 0:
        need_delete = 1
        table_name = ""
        att_name = ""
        if searched_goods_id[i][0] == "1":#書
            table_name = "goods_book_category"
            att_name = "goods_book_id"
        else:#CD
            table_name = "goods_CD"
            att_name = "goods_CD_id"
        #選出該商品分類
        sql=f"SELECT `category` from `{table_name}` WHERE `{att_name}` = {searched_goods_id[i]};"
        cursor.execute(sql)
        category_check_fetch = cursor.fetchall()
        if category_check_fetch:
            j=0
            while j<len(category_check_fetch):
                k=0
                while k<len(add_categories):
                    if category_check_fetch[j][0] == add_categories[k]:
                        #有符合的分類的id就append
                        searched_and_classified_goods_id.append(searched_goods_id[i])
                        break
                    k+=1
                j+=1
        i+=1
    last_category = ""
    if len(add_categories) == 0:
        i=0
        while i<len(searched_goods_id):
            searched_and_classified_goods_id.append(searched_goods_id[i])
            i+=1
    else:
        last_category = add_categories[len(add_categories)-1]
    #更新商品綜合評價
    sql=f"SELECT `goods_id` FROM `goods`;"
    cursor.execute(sql)
    goods_id_fetch = cursor.fetchall()
    if goods_id_fetch:
        k=0
        while k<len(goods_id_fetch):
            sql=f"SELECT `star_rate` FROM `buy` WHERE `star_rate` <> -1 AND goods_id = {goods_id_fetch[k][0]};"
            cursor.execute(sql)
            goods_rate_up = cursor.fetchall()
            avg = []
            if goods_rate_up:
                j=0
                while j<len(goods_rate_up):
                    avg.append(int(goods_rate_up[j][0]))
                    j+=1
                goods_avg = statistics.mean(avg)
                goods_avg = round(goods_avg,1)
                sql=f"UPDATE `goods` SET `goods_rate` = {goods_avg} WHERE `goods_id` = {goods_id_fetch[k][0]};"
                cursor.execute(sql)
            k+=1    
    #取得資料庫所有商品資料
    no_goods = "1"
    goods_datas = []
    i=0
    while i<len(searched_and_classified_goods_id):
        sql=f"SELECT * FROM `goods` WHERE `goods_quantity` > 0 AND `supply_status` = 1 AND `goods_id` = {searched_and_classified_goods_id[i]};"
        cursor.execute(sql)
        searched_goods_datas = cursor.fetchall()
        goods_datas.append(searched_goods_datas[0])
        i+=1
    goods = []
    if goods_datas:
        i=0
        while i<len(goods_datas):
            goodsub = []
            j=0
            while j<4 and i<len(goods_datas):
                member_id = goods_datas[i][0]
                goods_id = str(goods_datas[i][1])
                goods_name = goods_datas[i][2]
                goods_picture = goods_datas[i][3]
                
                if goods_picture:
                    
                    goods_picture = SRC + "/" +member_id + "/" + goods_picture
                else:
                    goods_picture = ""
                goods_author = goods_datas[i][5]
                goods_price = goods_datas[i][6]
                goods_rate = goods_datas[i][9]
                #商品分類
                if str(goods_id[0])=="1":#書
                    sql=f"SELECT `category` FROM `goods_book_category`,`goods` WHERE `goods_book_id` = `goods_id` AND `goods_id` = {goods_id};"
                    cursor.execute(sql)
                    categories = cursor.fetchall()
                    goodsub.append({"member_id":member_id,"goods_id":goods_id,"goods_name":goods_name,"goods_picture":goods_picture,"goods_author":goods_author,"goods_price":goods_price,"goods_rate":goods_rate,"categories":categories})
                elif str(goods_id[0])=="2":#CD 
                    sql=f"SELECT `category` FROM `goods_CD`,`goods` WHERE `goods_CD_id` = `goods_id` AND `goods_id` = {goods_id};"
                    cursor.execute(sql)
                    categories = cursor.fetchall()
                    goodsub.append({"member_id":member_id,"goods_id":goods_id,"goods_name":goods_name,"goods_picture":goods_picture,"goods_author":goods_author,"goods_price":goods_price,"goods_rate":goods_rate,"categories":categories})
                i+=1
                j+=1
            goods.append(goodsub)
    if goods:
        no_goods = "0"
    
    connection.commit()
    return render_template("search_result.html",add_categories=add_categories,last_category=last_category,no_goods=no_goods,search_text=search_text,IS_LOGIN=IS_LOGIN,USER_NAME=USER_NAME,USER_AVATAR_SRC=USER_AVATAR_SRC,goods=goods)

@app.route("/shopping_cart.html",methods=['GET','POST'])
def shopping_cart():
    global IS_LOGIN
    global USER_AVATAR_SRC
    global USER_NAME
    global USER_ID
    if IS_LOGIN == "":
        return render_template("shopping_cart.html",IS_LOGIN=IS_LOGIN)
    cursor = connection.cursor()
    sql=f"SELECT * FROM `shopping_cart` WHERE `member_id` = '{USER_ID}';"
    cursor.execute(sql)
    shopping_datas = cursor.fetchall()
    goods_id = ""
    goods = []
    no_goods = "1"
    all_sum_price = 0
    if shopping_datas:
        i=0
        while i<len(shopping_datas):
            goods_id = str(shopping_datas[i][1])
            sql = f"SELECT `member_id` FROM `goods` WHERE `goods_id` = {goods_id};"
            cursor.execute(sql)
            member_id_fetch = cursor.fetchall()
            member_id = ""
            if member_id_fetch:
                member_id = member_id_fetch[0][0]
            goods_name = shopping_datas[i][2]
            goods_sum_price = shopping_datas[i][3]
            all_sum_price += goods_sum_price
            goods_picture = shopping_datas[i][4]
            if goods_picture:
                goods_picture = SRC + "/" + member_id + "/" + goods_picture
            else:
                goods_picture = ""
            goods_amount = shopping_datas[i][5]
            goods_price = int(goods_sum_price / goods_amount)
            #取得物品剩餘數量
            sql = f"SELECT `goods_quantity` FROM `goods` WHERE `goods_id` = {goods_id};"
            cursor.execute(sql)
            goods_quantity_fetch = cursor.fetchall()
            goods_quantity = ""
            if goods_quantity_fetch:
                goods_quantity = str(goods_quantity_fetch[0][0])
            goods.append({"goods_id":goods_id,"goods_name":goods_name,"goods_sum_price":goods_sum_price,"goods_price":goods_price,"goods_picture":goods_picture,"goods_amount":goods_amount,"goods_quantity":goods_quantity})
            i+=1
    if goods:
        no_goods = "0"
    return render_template("shopping_cart.html",all_sum_price=all_sum_price,IS_LOGIN=IS_LOGIN,USER_NAME=USER_NAME,USER_AVATAR_SRC=USER_AVATAR_SRC,goods=goods,no_goods=no_goods)

@app.route("/delivery_service.html",methods=['GET','POST'])
def delivery_service():
    global IS_LOGIN
    global USER_AVATAR_SRC
    global USER_NAME
    global USER_ID
    global SIMULATE_ARRIVAL_TIME
    global SIMULATE_GET_DAY
    cursor = connection.cursor()
    no_goods = "1"
    end_transaction = ""
    if IS_LOGIN=="1":
        transaction_id = request.args.get('tid')
        if transaction_id:#取貨並結束交易
            end_transaction = "1"
            #已送達已取貨+虛擬取貨日期
            print(transaction_id)
            sql = f"SELECT `arrival_date` FROM `transaction_record` WHERE `transaction_id` = {transaction_id};"
            cursor.execute(sql)
            arrival_fetch = cursor.fetchall()
            if arrival_fetch:
                arrival_date = arrival_fetch[0][0]
                d = datetime.timedelta(days=SIMULATE_GET_DAY)#取貨日期模擬
                simulate_finish = d + arrival_date
                finish_date = simulate_finish.strftime('%Y-%m-%d %H:%M:%S')
                print(finish_date)
            sql = f"UPDATE `transaction_record` SET `transaction_status` = 3,`finish_date` = '{finish_date}' WHERE `transaction_id` = {transaction_id};"
            cursor.execute(sql)
        
        #更新物流狀態
        sql=f"SELECT `transaction_id`, `buy_date`,`transaction_status` FROM `transaction_record` WHERE `member_id` = '{USER_ID}' AND `transaction_status` < 3;"
        cursor.execute(sql)
        update_fetch = cursor.fetchall()
        localtime = time.localtime()
        result = time.strftime("%Y-%m-%d %H:%M:%S", localtime)
        simulate_time = datetime.datetime.strptime(str(result),'%Y-%m-%d %H:%M:%S')
        if update_fetch:
            i=0
            while i<len(update_fetch):
                #已出貨未送達
                if update_fetch[i][2] == 1:
                    buy_date =update_fetch[i][1]
                    d = simulate_time - buy_date
                    print(simulate_time,buy_date)
                    print(d.seconds,SIMULATE_ARRIVAL_TIME)
                    if d.seconds > SIMULATE_ARRIVAL_TIME:#已送達模擬
                        sql=f"UPDATE `transaction_record` SET `transaction_status` = 2 WHERE `transaction_id` = {update_fetch[i][0]};"
                        cursor.execute(sql)
                i+=1
        
        
        checktimebreak()

        goods = []
        transaction = []
        #選出所有進行中交易
        sql=f"SELECT `transaction_id` FROM `transaction_record` WHERE `member_id` = '{USER_ID}' AND `transaction_status` < 3;"
        cursor.execute(sql)
        transaction_ids_fetch = cursor.fetchall()
        if transaction_ids_fetch:
            i=0
            no_goods = "0"
            while i<len(transaction_ids_fetch):
                transaction_id = transaction_ids_fetch[i][0]
                #取得每筆交易所有商品
                sql=f"SELECT `goods_id`,`goods_name`,`goods_price`,`goods_amount`,`goods_status` FROM `transaction_record_goods` WHERE `transaction_id` = {transaction_id};"
                cursor.execute(sql)
                transaction_goods_fetch = cursor.fetchall()
                #取得每筆交易狀態
                sql=f"SELECT `transaction_status` FROM `transaction_record` WHERE `transaction_id` = {transaction_id};"
                cursor.execute(sql)
                transaction_status_fetch = cursor.fetchall()
                if transaction_goods_fetch:
                    j=0
                    goods_sum_price =0
                    while j<len(transaction_goods_fetch):
                        goods_sum_price += transaction_goods_fetch[j][2]
                        j+=1
                    j=0
                    goods = []
                    while j<len(transaction_goods_fetch):
                        goods_id = transaction_goods_fetch[j][0]
                        goods_name = transaction_goods_fetch[j][1]
                        goods_amount =transaction_goods_fetch[j][3]
                        goods_status = transaction_goods_fetch[j][4]
                        goods.append({"goods_id":goods_id,"goods_name":goods_name,"goods_amount":goods_amount,"goods_status":goods_status})
                        j+=1
                    transaction_status = str(transaction_status_fetch[0][0])
                    print(transaction_status,goods)
                    transaction.append({"transaction_id":transaction_id,"goods_sum_price":goods_sum_price,"goods":goods,"transaction_status":transaction_status,"last_goods_id":transaction_goods_fetch[len(transaction_goods_fetch)-1][0]})
                i+=1
        connection.commit()
        return render_template("delivery_service.html",end_transaction=end_transaction,no_goods=no_goods,transaction=transaction,IS_LOGIN=IS_LOGIN,USER_NAME=USER_NAME,USER_AVATAR_SRC=USER_AVATAR_SRC)
    else:
        return render_template("delivery_service.html",IS_LOGIN=IS_LOGIN)

@app.route("/login.html",methods=['GET','POST'])
def login():
    global IS_LOGIN
    global USER_AVATAR_SRC
    global USER_NAME
    IS_LOGIN = ""
    cursor = connection.cursor()
    return render_template("login.html",IS_LOGIN=IS_LOGIN,USER_NAME=USER_NAME,USER_AVATAR_SRC=USER_AVATAR_SRC)

@app.route("/create_account.html",methods=['GET','POST'])
def create_account():
    global IS_LOGIN
    global USER_AVATAR_SRC
    global USER_NAME
    cursor = connection.cursor()
    return render_template("create_account.html",IS_LOGIN=IS_LOGIN,USER_NAME=USER_NAME,USER_AVATAR_SRC=USER_AVATAR_SRC)

@app.route("/account.html",methods=['GET','POST'])
def account():
    global IS_LOGIN
    global USER_AVATAR_SRC
    global USER_NAME
    global USER_ID
    global USER_PHONENUMBER
    global USER_BANKACC
    global USER_CARD
    global USER_PASSWORD
    global MANAGER_ID
    global MANAGER_PASSWORD
    goods_sum_price = 0
    cursor = connection.cursor()
    user = {}
    type = str(request.args.get('type'))#1為修改資訊
    if IS_LOGIN =="1":
        if type == "1":
            USER_PASSWORD = request.values['password']
            USER_NAME = request.values['name']
            #取得圖片
            picture = request.files.get("picture")
            format = ""
            fileName = ""
            #取得副檔名
            if picture:
                i=len(picture.filename)-1
                while picture.filename[i] != "." and i>0:
                    i-=1
                format = picture.filename[i:]
                fileName=USER_ID+"_avatar"
                if format == '.jpg':
                    fileName+=".jpg"
                elif format == '.png':
                    fileName+=".png"
                #儲存圖片
                upload_path = os.path.join(BASEPATH,USER_ID,str(fileName))
                USER_AVATAR_SRC = f"/static/uploads/{USER_ID}/{fileName}"
                if picture:
                    picture.save(upload_path)
            else:
                picture = ""
            USER_PHONENUMBER = request.values['phone_number']
            USER_BANKACC = request.values['bank_account']
            USER_CARD = request.values['credit_card']
            sql=f"UPDATE `member` SET `name`= '{USER_NAME}',`password` = '{USER_PASSWORD}',`picture` = '{fileName}',`phone_number` = '{USER_PHONENUMBER}',`bank_account` = '{USER_BANKACC}',`credit card` = '{USER_CARD}' WHERE `member_id` = '{USER_ID}';"
            cursor.execute(sql)
            connection.commit()
        #取得已結束交易紀錄
        transaction = []
        
        sql=f"SELECT * FROM `transaction_record` WHERE `member_id` = '{USER_ID}' AND `transaction_status` = 3;"
        cursor.execute(sql)
        transaction_record_fetch = cursor.fetchall()
        if transaction_record_fetch:
            i=0
            #取得每筆交易的所有商品
            while i<len(transaction_record_fetch):
                transaction_id = transaction_record_fetch[i][1]
                buy_date = transaction_record_fetch[i][2]
                finish_date = transaction_record_fetch[i][4]
                sql=f"SELECT * FROM `transaction_record_goods` WHERE `transaction_id` = {transaction_id};"
                cursor.execute(sql)
                goods_fetch = cursor.fetchall()
                goods = []
                if goods_fetch:
                    
                    j=0
                    goods_sum_price = 0
                    while j<len(goods_fetch):
                        goods_sum_price += goods_fetch[j][3]
                        j+=1
                    j=0
                    
                    while j<len(goods_fetch):
                        print(goods_fetch[j])
                        goods_id = goods_fetch[j][1]
                        goods_name = goods_fetch[j][2]
                        goods_amount = goods_fetch[j][4]
                        goods.append({"goods_id":goods_id,"goods_name":goods_name,"goods_amount":goods_amount})
                        j+=1
                transaction.append({"transaction_id":transaction_id,"goods":goods,"goods_sum_price":goods_sum_price,"buy_date":buy_date,"finish_date":finish_date,"last_goods_id":goods_fetch[len(goods_fetch)-1][1]})
                i+=1
                
        user = {"id":USER_ID,"password":USER_PASSWORD,"name":USER_NAME,"phone_number":USER_PHONENUMBER,"bank_account":USER_BANKACC,"credit_card":USER_CARD,"picture":USER_AVATAR_SRC}
        return render_template("account.html",transaction=transaction,IS_LOGIN=IS_LOGIN,user=user,USER_NAME=USER_NAME,USER_AVATAR_SRC=USER_AVATAR_SRC)
    elif IS_LOGIN == "0":
        if type == "1":
            MANAGER_PASSWORD = request.values['password']
            sql=f"UPDATE `member` SET `password`= '{MANAGER_PASSWORD}';"
            cursor.execute(sql)
            connection.commit()
        user = {"id":MANAGER_ID,"password":MANAGER_PASSWORD}
        return render_template("account.html",IS_LOGIN=IS_LOGIN,user=user,USER_NAME=USER_NAME,USER_AVATAR_SRC=USER_AVATAR_SRC)
    else:
        return render_template("account.html",IS_LOGIN=IS_LOGIN)

@app.route("/bidding.html",methods=['GET','POST'])
def bidding():
    global IS_LOGIN
    global USER_AVATAR_SRC
    global USER_NAME
    global SRC
    global USER_ID
    cursor = connection.cursor()
    bid_fail = "0"
    no_bank_account = ""
    if USER_BANKACC == "":
        no_bank_account = "1"
        return render_template("bidding.html",no_bank_account=no_bank_account,IS_LOGIN=IS_LOGIN,USER_NAME=USER_NAME,USER_AVATAR_SRC=USER_AVATAR_SRC)
    
    bid = str(request.args.get('bid'))

    nowtime = time.localtime()
    localtime = time.strftime("%Y-%m-%d %H:%M:%S", nowtime)

    #更新競標活動狀態
    sql=f"UPDATE `bid` SET `bid_status` = '1' WHERE `start_date` < '{localtime}';"
    cursor.execute(sql)
    sql=f"UPDATE `bid` SET `bid_status` = '2' WHERE `end_date` < '{localtime}';"
    cursor.execute(sql)
    sql=f"SELECT `bid_id`,`bid_goods_id` FROM `bid` WHERE `bid_status` = '2' AND `max_member_id` IS NULL;"
    cursor.execute(sql)
    bid_goods_delete_id_fetch = cursor.fetchall()
    if bid_goods_delete_id_fetch:
        i=0
        while i<len(bid_goods_delete_id_fetch):
            sql =f"UPDATE `goods` SET `goods_quantity` = `goods_quantity` + 1 WHERE `goods_id` = {bid_goods_delete_id_fetch[i][1]};"
            cursor.execute(sql)
            sql =f"UPDATE `goods` SET `supply_status` = 1 WHERE `goods_id` = {bid_goods_delete_id_fetch[i][1]};"
            cursor.execute(sql)
            sql =f"DELETE FROM `bid` WHERE `bid_id` = {bid_goods_delete_id_fetch[i][0]};"
            cursor.execute(sql)
            i+=1

    #喊價
    sta = str(request.args.get('sta'))
    if sta == "1":
        money = int(request.values['money'])
        sql = f"SELECT `max_price` FROM `bid` WHERE `bid_id` = {bid};"
        cursor.execute(sql)
        check_price_fetch = cursor.fetchall()
        if check_price_fetch:
            if int(check_price_fetch[0][0])*1.05 < money:#喊價成功
                sql=f"UPDATE `bid` SET `max_price` = {money},`max_member_id`= '{USER_ID}' WHERE `bid_id` = {bid};"
                cursor.execute(sql)
            else:
                bid_fail = "1"


    #顯示所有進行中競標
    no_goods = "1"
    pre_text = ""
    sql=f"SELECT * FROM `bid`;"
    cursor.execute(sql)
    bid_fetch = cursor.fetchall()
    bidding = []
    if bid_fetch:
        i=0
        while i<len(bid_fetch):
            bid_id = bid_fetch[i][0]
            goods_id = bid_fetch[i][1]
            sql=f"SELECT `goods_name` FROM `goods` WHERE `goods_id` = {goods_id};"
            cursor.execute(sql)
            goods_name_fetch = cursor.fetchall()
            sql = f"SELECT `goods_picture`,`member_id` FROM `goods`,`bid` WHERE `goods_id` = {goods_id};"
            cursor.execute(sql)
            goods_picture_fetch = cursor.fetchall()
            goods_picture = ""
            if goods_picture_fetch:
                goods_picture = goods_picture_fetch[0][0]
                member_id = goods_picture_fetch[0][1]
                goods_picture = SRC + "/" + member_id + "/" + goods_picture

            max_price = bid_fetch[i][2]
            max_member_id = bid_fetch[i][3]
            start_date = bid_fetch[i][4]
            end_date = bid_fetch[i][5]
            bid_status = bid_fetch[i][6]
            #輸入金額要>當前最高價的5%
            sql=f"SELECT `max_price` FROM `bid` WHERE `bid_id` = {bid_id};"
            cursor.execute(sql)
            max_price_fetch = cursor.fetchall()
            if max_price_fetch:
                max_price = int(max_price_fetch[0][0])
                pre_text = str(int(max_price*1.05)+1)
            bidding.append({"bid_id":bid_id,"goods_name":goods_name_fetch[0][0],"goods_id":goods_id,"goods_picture":goods_picture,"max_price":max_price,"max_member_id":max_member_id,"start_date":start_date,"end_date":end_date,"bid_status":bid_status,"pre_text":pre_text})
            #判斷是否為商品賣家
            sql=f"SELECT COUNT(*) FROM `goods` WHERE `member_id` = '{USER_ID}' AND `goods_id` = {goods_id};"
            cursor.execute(sql)
            is_seller_fetch = cursor.fetchall()
            if is_seller_fetch and is_seller_fetch[0][0] > 0:#是的話就不顯示該競標
                del bidding[len(bidding)-1]
            i+=1
    connection.commit()
    if bidding:
        no_goods = "0"
    return render_template("bidding.html",bid_fail=bid_fail,no_goods=no_goods,USER_ID=USER_ID,bidding=bidding,no_bank_account=no_bank_account,IS_LOGIN=IS_LOGIN,USER_NAME=USER_NAME,USER_AVATAR_SRC=USER_AVATAR_SRC)


@app.route("/goods_info.html",methods=['GET','POST'])
def goods_info():
    global IS_LOGIN
    global USER_AVATAR_SRC
    global USER_NAME
    global is_stop_supply
    
    cursor = connection.cursor()
    return render_template("goods_info.html",IS_LOGIN=IS_LOGIN,USER_NAME=USER_NAME,USER_AVATAR_SRC=USER_AVATAR_SRC)

@app.route("/manager_home.html",methods=['GET','POST'])
def manager_home():
    global IS_LOGIN
    global MANAGER_ID
    cursor = connection.cursor()
    mtype = str(request.args.get('type'))#處理檢舉訊息,0取消1刪除
    if mtype == "0":#取消
        rid = str(request.args.get('rid'))
        mid = str(request.args.get('mid'))
        sql=f"DELETE FROM `report` WHERE `member_id` = '{mid}' AND `seller_id` = '{rid}';"
        cursor.execute(sql)
    if mtype == "1":#刪除
        rid = str(request.args.get('rid'))
        mid = str(request.args.get('mid'))
        sql=f"DELETE FROM `member` WHERE `member_id` = '{rid}';"
        cursor.execute(sql)
        
    #取得會員總數
    sql=f"SELECT COUNT(*) FROM `member`;"
    cursor.execute(sql)
    member_sum_fetch = cursor.fetchall()
    member_sum = 0
    if member_sum_fetch:
        member_sum = member_sum_fetch[0][0]
    #取得商品總數
    sql=f"SELECT COUNT(*) FROM `goods`;"
    cursor.execute(sql)
    goods_sum_fetch = cursor.fetchall()
    goods_sum = 0
    if goods_sum_fetch:
        goods_sum = goods_sum_fetch[0][0]
    #取得交易總金額
    sql=f"SELECT sum(`goods_price`) FROM `transaction_record_goods`;"
    cursor.execute(sql)
    price_sum_fetch = cursor.fetchall()
    price_sum = 0
    if price_sum_fetch:
        price_sum = price_sum_fetch[0][0]
    #取得被檢舉人資料
    checktimebreak()
    report = []
    sql =f"SELECT `seller_id`, `report_text`,`member_id` FROM `report`;"
    cursor.execute(sql)
    reported_id_fetch = cursor.fetchall()
    if reported_id_fetch:
        i=0
        while i<len(reported_id_fetch):
            reported_id = reported_id_fetch[i][0]
            report_text = reported_id_fetch[i][1]
            mid = reported_id_fetch[i][2]
            report.append({"id":reported_id,"text":report_text,"mid":mid})
            i+=1
    
    no_report = "1"
    if report:
        no_report = "0"
    connection.commit()
    return render_template("manager_home.html",no_report=no_report,member_sum=member_sum,goods_sum=goods_sum,price_sum=price_sum,report=report,IS_LOGIN=IS_LOGIN,MANAGER_ID=MANAGER_ID)

@app.route("/QA.html",methods=['GET','POST'])
def QA():
    global IS_LOGIN
    cursor = connection.cursor()
    need_sub = 0
    if IS_LOGIN == "0":
        global MANAGER_ID
        deal_type = str(request.args.get('type'))
        if deal_type == "0":#增
            sql=f"SELECT COUNT(*) FROM `QA`;"
            cursor.execute(sql)
            QAnum_fetch = cursor.fetchall()
            if QAnum_fetch:
                QAnum = int(QAnum_fetch[0][0])
                QA_id = str(QAnum + 100)
                Q = request.values['Q']
                A = request.values['A']
                sql=f"SELECT COUNT(*) FROM `QA` WHERE `QA_id` = {QA_id};"
                cursor.execute(sql)
                repeat_id_fetch = cursor.fetchall()
                if repeat_id_fetch and repeat_id_fetch[0][0]>0:
                    QA_id = 100
                    need_sub = 1
                while repeat_id_fetch and repeat_id_fetch[0][0]>0:
                    sql=f"SELECT COUNT(*) FROM `QA` WHERE `QA_id` = {QA_id};"
                    cursor.execute(sql)
                    repeat_id_fetch = cursor.fetchall()
                    QA_id += 1
                if need_sub == 1:
                    QA_id -= 1
                sql = f"insert into `QA` values('{QA_id}','{Q}','{A}');"
                cursor.execute(sql)
                connection.commit()
        if deal_type == "1":#刪
            QA_id = str(request.args.get('QA_id'))
            sql = f"DELETE FROM `QA` WHERE `QA_id` = '{QA_id}';"
            cursor.execute(sql)
            connection.commit()
        if deal_type == "2":#改
            QA_id = str(request.args.get('QA_id'))
            Q = request.values['Q']
            A = request.values['A']
            sql=f"UPDATE `QA` SET `Q` = '{Q}',`A` = '{A}' WHERE `QA_id` = '{QA_id}';"
            cursor.execute(sql)
            connection.commit()
        if deal_type == "3":#改使用手冊   
            manual_text = str(request.values['manual'])
            sql=f"SELECT COUNT(*) FROM `manual`;"
            cursor.execute(sql)
            count_fetch = cursor.fetchall()
            if count_fetch or int(count_fetch[0][0]) == 0:
                if int(count_fetch[0][0]) == 0:
                    sql=f"insert into `manual` values(0,'{manual_text}');"
                    cursor.execute(sql)
                if int(count_fetch[0][0]) == 1:
                    sql=f"UPDATE `manual` SET `text` = '{manual_text}' WHERE `id` = 0;"
                    cursor.execute(sql)
            
        #取得使用手冊
        manual_text_get = ""
        sql=f"SELECT `text` FROM `manual`;"
        cursor.execute(sql)
        text_fetch = cursor.fetchall()
        if text_fetch:
            manual_text_get = text_fetch[0][0]            
        #選擇所有QA
        QA = []
        sql=f"SELECT * FROM `QA`;"
        cursor.execute(sql)
        QA_fetch = cursor.fetchall()
        if QA_fetch:
            i=0
            while i<len(QA_fetch):
                QA_id = QA_fetch[i][0]
                Q = QA_fetch[i][1]
                A = QA_fetch[i][2]
                QA.append({"QA_id":QA_id,"Q":Q,"A":A})
                i+=1
                
        return render_template("QA.html",manual_text=manual_text_get,QA=QA,IS_LOGIN=IS_LOGIN,MANAGER_ID=MANAGER_ID)
    global USER_AVATAR_SRC
    global USER_NAME
    #取得使用手冊
    manual_text_get = ""
    sql=f"SELECT `text` FROM `manual`;"
    cursor.execute(sql)
    text_fetch = cursor.fetchall()
    if text_fetch:
        manual_text_get = text_fetch[0][0]
    #選擇所有QA
    QA = []
    sql=f"SELECT * FROM `QA`;"
    cursor.execute(sql)
    QA_fetch = cursor.fetchall()
    if QA_fetch:
        i=0
        while i<len(QA_fetch):
            QA_id = QA_fetch[i][0]
            Q = QA_fetch[i][1]
            A = QA_fetch[i][2]
            QA.append({"QA_id":QA_id,"Q":Q,"A":A})
            i+=1
    return render_template("QA.html",manual_text=manual_text_get,QA=QA,IS_LOGIN=IS_LOGIN,USER_NAME=USER_NAME,USER_AVATAR_SRC=USER_AVATAR_SRC)

@app.route("/manager_bidding.html",methods=['GET','POST'])
def manager_bidding():
    global IS_LOGIN
    global MANAGER_ID
    global SRC
    cursor = connection.cursor()
    type = str(request.args.get('type'))
    bid = str(request.args.get('bid'))
    date_error = "0"
    can_bid = "1"
    can_book =0 
    can_cd=0
    sql =f"SELECT COUNT(*) FROM `goods` WHERE `goods_id` < 2000;"
    cursor.execute(sql)
    can_bid_fetch = cursor.fetchall()
    if can_bid_fetch and can_bid_fetch[0][0]>0:#算出最大書id
        sql =f"SELECT COUNT(*) FROM `goods` WHERE `goods_id` < 2000 AND `goods_quantity` > 0 AND `supply_status` = 1 AND `can_bid` = 1;"
        cursor.execute(sql)
        can_book_fetch = cursor.fetchall()
        if can_book_fetch:
            if int(can_book_fetch[0][0])>0:#有cd
                can_book = 1
        randmax_book = int(can_bid_fetch[0][0]) + 1000
        print("max_book",randmax_book)
    sql =f"SELECT COUNT(*) FROM `goods` WHERE `goods_id` > 2000;"
    cursor.execute(sql)
    can_bid_fetch = cursor.fetchall()
    if can_bid_fetch and can_bid_fetch[0][0]>0:#算出最大CDid
        sql =f"SELECT COUNT(*) FROM `goods` WHERE `goods_id` > 2000 AND `goods_quantity` > 0 AND `supply_status` = 1 AND `can_bid` = 1;"
        cursor.execute(sql)
        can_cd_fetch = cursor.fetchall()
        if can_cd_fetch:
            if int(can_cd_fetch[0][0])>0:#有cd
                can_cd = 1
        randmax_cd = int(can_bid_fetch[0][0]) + 2000
        print("max_cd",randmax_cd)
    print("can_b_cd",can_book,can_cd)
    if can_book == 0 and can_cd ==0:
        can_bid="0"
    if type == "0":#新增
        select_book=0
        select_cd=0
        new_bid_id = 0
        new_max_price = 0
        need_sub = 0
        sql =f"SELECT COUNT(*) FROM `bid`;"
        cursor.execute(sql)
        new_bid_id_fetch = cursor.fetchall()
        if new_bid_id_fetch or int(new_bid_id_fetch[0][0]) == 0:
            new_bid_id = int(new_bid_id_fetch[0][0])+1000
            bid = new_bid_id
            sql=f"SELECT COUNT(*) FROM `bid` WHERE `bid_id` = {new_bid_id};"
            cursor.execute(sql)
            repeat_id_fetch = cursor.fetchall()
            if repeat_id_fetch and repeat_id_fetch[0][0]>0:
                new_bid_id = 1000
                need_sub = 1
            while repeat_id_fetch and repeat_id_fetch[0][0]>0:
                bid = new_bid_id
                sql=f"SELECT COUNT(*) FROM `bid` WHERE `bid_id` = {new_bid_id};"
                cursor.execute(sql)
                repeat_id_fetch = cursor.fetchall()
                new_bid_id += 1
            if need_sub == 1:
                new_bid_id -= 1
            
        start_date = request.values['start_bidding']
        end_date = request.values['end_bidding']
        end_date = few_mins_later(2)
        print(start_date,end_date)
        if start_date>=end_date:
            date_error = "1"

        if can_book == 1 and can_cd == 1 and date_error == "0":
            rtype = random.randint(1,2)
            if rtype == 1:#書
                print("select_max_book",randmax_book)
                select_book = random.randint(1001,randmax_book)
                sql=f"SELECT COUNT(*) FROM `goods` WHERE `goods_id` = {select_book} AND `goods_quantity` > 0 AND `supply_status` = 1 AND `can_bid` = 1;"
                cursor.execute(sql)
                is_can_bid_fetch = cursor.fetchall()
                while int(is_can_bid_fetch[0][0])==0:
                    select_book = random.randint(1001,randmax_book)
                    sql=f"SELECT COUNT(*) FROM `goods` WHERE `goods_id` = {select_book} AND `goods_quantity` > 0 AND `supply_status` = 1 AND `can_bid` = 1;"
                    cursor.execute(sql)
                    is_can_bid_fetch = cursor.fetchall()
                print("sb",select_book)
                sql=f"SELECT `goods_price` FROM `goods` WHERE `goods_id` = {select_book};"
                cursor.execute(sql)
                ori_price_fetch = cursor.fetchall()
                if ori_price_fetch:
                    new_max_price = int(int(ori_price_fetch[0][0])*0.7) + 1
                sql=f"insert into `bid` values({new_bid_id},{select_book},{new_max_price},NULL,'{start_date}','{end_date}','0');"
                cursor.execute(sql)
                sql=f"UPDATE `goods` SET `supply_status` = 0 WHERE `goods_id` = {select_book};"
                cursor.execute(sql)
                sql=f"UPDATE `goods` SET `goods_quantity` = `goods_quantity` - 1 WHERE `goods_id` = {select_book};"
                cursor.execute(sql)
            else:#cd
                print("select_max_cd",randmax_cd)
                select_cd = random.randint(2001,randmax_cd)
                sql=f"SELECT COUNT(*) FROM `goods` WHERE `goods_id` = {select_cd} AND `goods_quantity` > 0 AND `supply_status` = 1 AND `can_bid` = 1;"
                cursor.execute(sql)
                is_can_bid_fetch = cursor.fetchall()
                while int(is_can_bid_fetch[0][0])==0:
                    select_cd = random.randint(2001,randmax_cd)
                    sql=f"SELECT COUNT(*) FROM `goods` WHERE `goods_id` = {select_cd} AND `goods_quantity` > 0 AND `supply_status` = 1 AND `can_bid` = 1;"
                    cursor.execute(sql)
                    is_can_bid_fetch = cursor.fetchall()
                print("scd",select_cd)
                sql=f"SELECT `goods_price` FROM `goods` WHERE `goods_id` = {select_cd};"
                cursor.execute(sql)
                ori_price_fetch = cursor.fetchall()
                if ori_price_fetch:
                    new_max_price = int(int(ori_price_fetch[0][0])*0.7) + 1
                sql=f"insert into `bid` values({new_bid_id},{select_cd},{new_max_price},NULL,'{start_date}','{end_date}','0');"
                cursor.execute(sql)
                sql=f"UPDATE `goods` SET `supply_status` = 0 WHERE `goods_id` = {select_cd};"
                cursor.execute(sql)
                sql=f"UPDATE `goods` SET `goods_quantity` = `goods_quantity` - 1 WHERE `goods_id` = {select_cd};"
                cursor.execute(sql)
        elif can_book == 1 and can_cd == 0 and date_error == "0": #書
            print("select_max_book",randmax_book)
            select_book = random.randint(1001,randmax_book)
            sql=f"SELECT COUNT(*) FROM `goods` WHERE `goods_id` = {select_book} AND `goods_quantity` > 0 AND `supply_status` = 1 AND `can_bid` = 1;"
            cursor.execute(sql)
            is_can_bid_fetch = cursor.fetchall()
            while int(is_can_bid_fetch[0][0])==0:
                select_book = random.randint(1001,randmax_book)
                sql=f"SELECT COUNT(*) FROM `goods` WHERE `goods_id` = {select_book} AND `goods_quantity` > 0 AND `supply_status` = 1 AND `can_bid` = 1;"
                cursor.execute(sql)
                is_can_bid_fetch = cursor.fetchall()
            print("sb",select_book)
            sql=f"SELECT `goods_price` FROM `goods` WHERE `goods_id` = {select_book};"
            cursor.execute(sql)
            ori_price_fetch = cursor.fetchall()
            if ori_price_fetch:
                new_max_price = int(int(ori_price_fetch[0][0])*0.7) + 1
            sql=f"insert into `bid` values({new_bid_id},{select_book},{new_max_price},NULL,'{start_date}','{end_date}','0');"
            cursor.execute(sql)
            sql=f"UPDATE `goods` SET `supply_status` = 0 WHERE `goods_id` = {select_book};"
            cursor.execute(sql)
            sql=f"UPDATE `goods` SET `goods_quantity` = `goods_quantity` - 1 WHERE `goods_id` = {select_book};"
            cursor.execute(sql)
        elif can_book == 0 and can_cd == 1 and date_error == "0":#cd
            print("select_max_cd",randmax_cd)
            select_cd = random.randint(2001,randmax_cd)
            sql=f"SELECT COUNT(*) FROM `goods` WHERE `goods_id` = {select_cd} AND `goods_quantity` > 0 AND `supply_status` = 1 AND `can_bid` = 1;"
            cursor.execute(sql)
            is_can_bid_fetch = cursor.fetchall()
            while int(is_can_bid_fetch[0][0])==0:
                select_cd = random.randint(2001,randmax_cd)
                sql=f"SELECT COUNT(*) FROM `goods` WHERE `goods_id` = {select_cd} AND `goods_quantity` > 0 AND `supply_status` = 1 AND `can_bid` = 1;"
                cursor.execute(sql)
                is_can_bid_fetch = cursor.fetchall()
            print("scd",select_cd)
            sql=f"SELECT `goods_price` FROM `goods` WHERE `goods_id` = {select_cd};"
            cursor.execute(sql)
            ori_price_fetch = cursor.fetchall()
            if ori_price_fetch:
                new_max_price = int(int(ori_price_fetch[0][0])*0.7) + 1
            sql=f"insert into `bid` values({new_bid_id},{select_cd},{new_max_price},NULL,'{start_date}','{end_date}','0');"
            cursor.execute(sql)
            sql=f"UPDATE `goods` SET `supply_status` = 0 WHERE `goods_id` = {select_cd};"
            cursor.execute(sql)
            sql=f"UPDATE `goods` SET `goods_quantity` = `goods_quantity` - 1 WHERE `goods_id` = {select_cd};"
            cursor.execute(sql)
        elif can_book == 0 and can_cd == 0:
            can_bid = "0"
        
    
    
    
    #刪除
    if type == "1":
        sql=f"SELECT `bid_goods_id` FROM `bid` WHERE `bid_id` = {bid};"
        cursor.execute(sql)
        bid_goods_id_fetch = cursor.fetchall()
        sql =f"UPDATE `goods` SET `goods_quantity` = `goods_quantity` + 1 WHERE `goods_id` = {bid_goods_id_fetch[0][0]};"
        cursor.execute(sql)
        sql =f"UPDATE `goods` SET `supply_status` = 1 WHERE `goods_id` = {bid_goods_id_fetch[0][0]};"
        cursor.execute(sql)
        sql =f"DELETE FROM `bid` WHERE `bid_id` = {bid};"
        cursor.execute(sql)
        


    nowtime = time.localtime()
    localtime = time.strftime("%Y-%m-%d %H:%M:%S", nowtime)

    #更新競標活動狀態
    sql=f"UPDATE `bid` SET `bid_status` = '1' WHERE `start_date` < '{localtime}';"
    cursor.execute(sql)
    sql=f"UPDATE `bid` SET `bid_status` = '2' WHERE `end_date` < '{localtime}';"
    cursor.execute(sql)
    sql=f"SELECT `bid_id`,`bid_goods_id` FROM `bid` WHERE `bid_status` = '2' AND `max_member_id` IS NULL;"
    cursor.execute(sql)
    bid_goods_delete_id_fetch = cursor.fetchall()
    print("why",bid_goods_delete_id_fetch)
    if bid_goods_delete_id_fetch:
        i=0
        while i<len(bid_goods_delete_id_fetch):
            sql =f"UPDATE `goods` SET `goods_quantity` = `goods_quantity` + 1 WHERE `goods_id` = {bid_goods_delete_id_fetch[i][1]};"
            cursor.execute(sql)
            sql =f"UPDATE `goods` SET `supply_status` = 1 WHERE `goods_id` = {bid_goods_delete_id_fetch[i][1]};"
            cursor.execute(sql)
            sql =f"DELETE FROM `bid` WHERE `bid_id` = {bid_goods_delete_id_fetch[i][0]};"
            cursor.execute(sql)
            i+=1

    #顯示所有進行中競標
    no_goods = "1"
    pre_text = ""
    sql=f"SELECT * FROM `bid`;"
    cursor.execute(sql)
    bid_fetch = cursor.fetchall()
    bidding = []
    if bid_fetch:
        i=0
        while i<len(bid_fetch):
            bid_id = bid_fetch[i][0]
            goods_id = bid_fetch[i][1]
            sql=f"SELECT `goods_name` FROM `goods` WHERE `goods_id` = {goods_id};"
            cursor.execute(sql)
            goods_name_fetch = cursor.fetchall()
            sql = f"SELECT `goods_picture`,`member_id` FROM `goods`,`bid` WHERE `goods_id` = {goods_id};"
            cursor.execute(sql)
            goods_picture_fetch = cursor.fetchall()
            goods_picture = ""
            if goods_picture_fetch:
                goods_picture = goods_picture_fetch[0][0]
                member_id = goods_picture_fetch[0][1]
                goods_picture = SRC + "/" + member_id + "/" + goods_picture

            max_price = bid_fetch[i][2]
            max_member_id = bid_fetch[i][3]
            start_date = bid_fetch[i][4]
            end_date = bid_fetch[i][5]
            bid_status = bid_fetch[i][6]
            #輸入金額要>當前最高價的5%
            print("bid_id",bid_id)
            sql=f"SELECT `max_price` FROM `bid` WHERE `bid_id` = {bid_id};"
            cursor.execute(sql)
            max_price_fetch = cursor.fetchall()
            if max_price_fetch:
                max_price = int(max_price_fetch[0][0])
                pre_text = str(int(max_price*1.05)+1)
            
            bidding.append({"bid_id":bid_id,"goods_name":goods_name_fetch[0][0],"goods_id":goods_id,"goods_picture":goods_picture,"max_price":max_price,"max_member_id":max_member_id,"start_date":start_date,"end_date":end_date,"bid_status":bid_status,"pre_text":pre_text})
            i+=1
    connection.commit()
    if bidding:
        no_goods = "0"
    return render_template("manager_bidding.html",date_error=date_error,no_goods=no_goods,can_bid=can_bid,bidding=bidding,IS_LOGIN=IS_LOGIN,MANAGER_ID=MANAGER_ID)

#############################################功能區
#request.values['']

#註冊提交
@app.route("/register",methods=['GET','POST'])
def register():
    cursor = connection.cursor()
    id=str(request.values['ID'])
    bankacc=str(request.values['bank_account'])
    creditcd=str(request.values['credit_card'])
    #判斷是否有重複
    cursor.execute("SELECT `member_id`, `bank_account`,`credit card` FROM `member`;")
    members_info = cursor.fetchall()
    i=0
    stat_id=""
    stat_bank=""
    stat_card=""
    global MANAGER_ID
    while i<len(members_info):
        if id == str(members_info[i][0]) or id == str(MANAGER_ID):
            stat_id="repeat"
        if bankacc == str(members_info[i][1]):
            stat_bank="repeat"
        if creditcd == str(members_info[i][2]):
            stat_card="repeat"
        i+=1
    
    if stat_id=="" and stat_bank=="" and stat_card=="":#如果沒有重複就創建成功
        password=request.values['password']
        name=request.values['name']
        #創建會員圖片資料夾
        global BASEPATH
        if not os.path.isdir(os.path.join(BASEPATH,id)):
            os.mkdir(os.path.join(BASEPATH,id))
        #取得圖片
        picture = request.files.get("picture")
        format = ""
        fileName = ""
        #取得副檔名
        if picture:
            i=len(picture.filename)-1
            while picture.filename[i] != "." and i>0:
                i-=1
            format = picture.filename[i:]
            fileName=id+"_avatar"
            if format == '.jpg':
                fileName+=".jpg"
            elif format == '.png':
                fileName+=".png"
            #儲存圖片
            upload_path = os.path.join(BASEPATH,id,str(fileName))
            if picture:
                picture.save(upload_path)
        else:
            picture = ""
        phone_number=request.values['phone_number']#取得電話號碼
        print("bank,card",bankacc,creditcd)
        if bankacc == "":
            if creditcd == "":
                sql=f"insert into `member` values('{id}','{password}','{name}','{fileName}','{phone_number}',NULL,NULL,'{MANAGER_ID}');"
            else:
                sql=f"insert into `member` values('{id}','{password}','{name}','{fileName}','{phone_number}',NULL,'{creditcd}','{MANAGER_ID}');"
        else:
            if creditcd == "":
                sql=f"insert into `member` values('{id}','{password}','{name}','{fileName}','{phone_number}','{bankacc}',NULL,'{MANAGER_ID}');"
            else:
                sql=f"insert into `member` values('{id}','{password}','{name}','{fileName}','{phone_number}','{bankacc}','{creditcd}','{MANAGER_ID}');"
        cursor.execute(sql)
        #print(sql)
        
        connection.commit()

    return render_template("create_account.html",stat_id=stat_id,stat_bank=stat_bank,stat_card=stat_card)

#登入提交
@app.route("/login_submit",methods=['GET','POST'])
def login_submit():
    global IS_LOGIN
    global MANAGER_ID
    global MANAGER_PASSWORD
    global USER_ID
    global USER_PASSWORD
    cursor = connection.cursor()
    account = request.values['member_id']
    password = request.values['password']
    cursor.execute("SELECT * FROM `member`;")
    members_info = cursor.fetchall()
    i=0
    if account == MANAGER_ID and password == MANAGER_PASSWORD:
        IS_LOGIN = "0"
        USER_ID = account
        USER_PASSWORD = password
        #取得會員總數
        sql=f"SELECT COUNT(*) FROM `member`;"
        cursor.execute(sql)
        member_sum_fetch = cursor.fetchall()
        member_sum = 0
        if member_sum_fetch:
            member_sum = member_sum_fetch[0][0]
        #取得商品總數
        sql=f"SELECT COUNT(*) FROM `goods`;"
        cursor.execute(sql)
        goods_sum_fetch = cursor.fetchall()
        goods_sum = 0
        if goods_sum_fetch:
            goods_sum = goods_sum_fetch[0][0]
        #取得交易總金額
        sql=f"SELECT sum(`goods_price`) FROM `transaction_record_goods`;"
        cursor.execute(sql)
        price_sum_fetch = cursor.fetchall()
        price_sum = 0
        if price_sum_fetch:
            price_sum = price_sum_fetch[0][0]
        #取得被檢舉人資料
        report = []
        sql =f"SELECT `seller_id` ,`report_text`,`member_id` FROM `report`;"
        cursor.execute(sql)
        reported_id_fetch = cursor.fetchall()
        if reported_id_fetch:
            j=0
            print(reported_id_fetch)
            while j<len(reported_id_fetch):
                reported_id = reported_id_fetch[j][0]
                report_text = reported_id_fetch[j][1]
                mid = reported_id_fetch[i][2]
                report.append({"id":reported_id,"text":report_text,"mid":mid})
                j+=1
        no_report = "1"
        if report:
            no_report = "0"
        connection.commit()
        return render_template("manager_home.html",no_report=no_report,member_sum=member_sum,goods_sum=goods_sum,price_sum=price_sum,report=report,IS_LOGIN=IS_LOGIN,MANAGER_ID=MANAGER_ID)
    while i < len(members_info):
        if account == members_info[i][0]:
            if password == members_info[i][1]:
                IS_LOGIN="1"
                global USER_CARD
                global USER_NAME
                global USER_PHONENUMBER
                global USER_BANKACC
                global USER_AVATAR_SRC
                global SRC
                USER_ID = account
                USER_PASSWORD = password
                USER_NAME = members_info[i][2]
                user_avater_name = members_info[i][3]
                if user_avater_name:
                    USER_AVATAR_SRC = USER_AVATAR_SRC + "/" + USER_ID + "/" +user_avater_name
                USER_PHONENUMBER = members_info[i][4]
                USER_BANKACC = members_info[i][5]
                USER_CARD = members_info[i][6]
                #更新商品綜合評價
                sql=f"SELECT `goods_id` FROM `goods`;"
                cursor.execute(sql)
                goods_id_fetch = cursor.fetchall()
                if goods_id_fetch:
                    k=0
                    while k<len(goods_id_fetch):
                        sql=f"SELECT `star_rate` FROM `buy` WHERE `star_rate` <> -1 AND goods_id = {goods_id_fetch[k][0]};"
                        cursor.execute(sql)
                        goods_rate_up = cursor.fetchall()
                        avg = []
                        if goods_rate_up:
                            j=0
                            while j<len(goods_rate_up):
                                avg.append(int(goods_rate_up[j][0]))
                                j+=1
                            goods_avg = statistics.mean(avg)
                            goods_avg = round(goods_avg,1)
                            sql=f"UPDATE `goods` SET `goods_rate` = {goods_avg} WHERE `goods_id` = {goods_id_fetch[k][0]};"
                            cursor.execute(sql)
                        k+=1
                #取得商品
                sql="SELECT * FROM `goods` WHERE `goods_quantity` > 0 AND `supply_status` = 1 ;"
                cursor.execute(sql)
                goods_datas = cursor.fetchall()
                if goods_datas:
                    k=0
                    goods = []
                    while k<len(goods_datas):
                        goodsub = []
                        j=0
                        while j<4 and k<len(goods_datas):
                            member_id = goods_datas[k][0]
                            goods_id = str(goods_datas[k][1])
                            goods_name = goods_datas[k][2]
                            goods_picture = goods_datas[k][3]
                            if goods_picture:
                                goods_picture = SRC + "/" +member_id + "/" + goods_picture
                            else:
                                goods_picture = ""
                            goods_author = goods_datas[k][5]
                            goods_price = goods_datas[k][6]
                            goods_rate = goods_datas[k][9]
                            #商品分類
                            if str(goods_id[0])=="1":#書
                                sql=f"SELECT `category` FROM `goods_book_category`,`goods` WHERE `goods_book_id` = `goods_id` AND `goods_id` = {goods_id};"
                                cursor.execute(sql)
                                categories = cursor.fetchall()
                                goodsub.append({"member_id":member_id,"goods_id":goods_id,"goods_name":goods_name,"goods_picture":goods_picture,"goods_author":goods_author,"goods_price":goods_price,"goods_rate":goods_rate,"categories":categories})
                            elif str(goods_id[0])=="2":#CD 
                                sql=f"SELECT `category` FROM `goods_CD`,`goods` WHERE `goods_CD_id` = `goods_id` AND `goods_id` = {goods_id};"
                                cursor.execute(sql)
                                categories = cursor.fetchall()
                                goodsub.append({"member_id":member_id,"goods_id":goods_id,"goods_name":goods_name,"goods_picture":goods_picture,"goods_author":goods_author,"goods_price":goods_price,"goods_rate":goods_rate,"categories":categories})
                            k+=1
                            j+=1
                        goods.append(goodsub)
                        #取得評價前三高的商品圖片跟id
                        slideshow = []
                        sql=f"SELECT `goods_id`,`goods_picture`,`member_id` FROM `goods` WHERE `goods_quantity` > 0 AND `supply_status` = 1 ORDER BY `goods_rate` DESC LIMIT 3;"
                        cursor.execute(sql)
                        top3_fetch = cursor.fetchall()
                        if top3_fetch:
                            j=0
                            while j<len(top3_fetch):
                                top3_id = str(top3_fetch[j][0])
                                top3_picture = top3_fetch[j][1]
                                if top3_picture:
                                    top3_picture = SRC + "/" + str(top3_fetch[j][2]) + "/" + top3_picture
                                else:
                                    top3_picture = ""
                                j+=1
                                slideshow.append({"goods_id":top3_id,"goods_picture":top3_picture})
    
                return render_template('home.html',slideshow=slideshow,IS_LOGIN=IS_LOGIN,USER_NAME=USER_NAME,USER_AVATAR_SRC=USER_AVATAR_SRC,goods=goods)
            else:
                IS_LOGIN="Epass"
                return render_template('login.html',IS_LOGIN=IS_LOGIN)
        i+=1
    IS_LOGIN="Nname"
    return render_template('login.html',IS_LOGIN=IS_LOGIN)

#進入商品詳細頁面
@app.route("/go_to_goods_info",methods=['GET','POST'])
def go_to_goods_info():
    #print(request.form)
    #從網址列拿資料
    goods_id = str(request.args.get('gid'))
    #print(goods_id)
    global IS_LOGIN
    global USER_AVATAR_SRC
    global USER_NAME
    global USER_ID
    global SRC
    global is_stop_supply
    num_error="0"
    cursor = connection.cursor()
    #取得供貨狀態
    print(goods_id)
    sql=f"SELECT `supply_status` FROM `goods` WHERE `goods_id` = {goods_id};"
    cursor.execute(sql)
    supply_status_fetch = cursor.fetchall()
    if supply_status_fetch or supply_status_fetch[0][0] == 0:
        if supply_status_fetch[0][0] == 0:
            is_stop_supply = "1"
        else:
            is_stop_supply = "0"

    #更新商品綜合評價
    sql=f"SELECT `star_rate` FROM `buy` WHERE `star_rate` <> -1 AND goods_id = {goods_id};"
    cursor.execute(sql)
    goods_rate_up = cursor.fetchall()
    avg = []
    if goods_rate_up:
        i=0
        while i<len(goods_rate_up):
            avg.append(int(goods_rate_up[i][0]))
            i+=1
        goods_avg = statistics.mean(avg)
        goods_avg = round(goods_avg,1)
        sql=f"UPDATE `goods` SET `goods_rate` = {goods_avg} WHERE `goods_id` = {goods_id};"
        cursor.execute(sql)

    #取得商品資訊
    sql=f"SELECT * FROM `goods` WHERE `goods_id` = {goods_id};"
    cursor.execute(sql)
    goods_info = cursor.fetchall()
    seller_name = ""
    seller_picture = ""
    seller = {}
    if goods_info:
        seller_id = goods_info[0][0]
        if seller_id:
            sql=f"SELECT `name`,`picture` FROM `member` WHERE `member_id` = '{seller_id}';"
            cursor.execute(sql)
            seller_info = cursor.fetchall()
            if seller_info:
                seller_name = seller_info[0][0]
                seller_picture = seller_info[0][1]
                if seller_picture:
                    seller_picture = SRC + "/" +seller_id + "/" + seller_picture
                else:
                    seller_picture = ""
                if seller_name:
                    #建立賣家資訊字典
                    seller = {"seller_id":seller_id,"seller_name":seller_name,"seller_avatar":seller_picture}
        goods_name = goods_info[0][2]
        goods_picture = goods_info[0][3]
        if goods_picture:
            goods_picture = SRC + "/" +seller_id + "/" + goods_picture
        else:
            goods_picture = ""
        goods_describe = goods_info[0][4]
        goods_author = goods_info[0][5]
        goods_price = goods_info[0][6]
        goods_quantity = goods_info[0][7]
        goods_dates = goods_info[0][8]
        goods_rate = goods_info[0][9]
    #根據交易紀錄判斷是否可評價&檢舉
    can_star_rate = ""
    can_report = ""
    can_rate = ""
    #是否有買過
    sql=f"SELECT COUNT(*) FROM `buy` WHERE `member_id` = '{USER_ID}' AND `goods_id` = {goods_id};"
    cursor.execute(sql)
    bye_ed = cursor.fetchall()
    print(bye_ed)
    if bye_ed and bye_ed[0][0] > 0:
        print(bye_ed)
        #是否有檢舉過
        if seller_id:
            sql=f"SELECT COUNT(*) FROM `report` WHERE `member_id` = '{USER_ID}' AND `seller_id` = '{seller_id}';"
            cursor.execute(sql)
            reported = cursor.fetchall()
            if reported or reported[0][0] == 0:
                if reported[0][0] == 0:#如果沒檢舉過就可以檢舉
                    can_report = "1"

        #是否有評價過(按鈕)
        sql=f"SELECT COUNT(*) FROM `buy` WHERE `member_id` = '{USER_ID}' AND `goods_id` = {goods_id} AND `star_rate` <> -1;"
        cursor.execute(sql)
        srate = cursor.fetchall()
        if srate or srate[0][0] == 0:
            if srate[0][0] == 0:#如果沒評價過就可以評價
                can_star_rate = "1"
            
        #是否有評價過(文字)
        sql=f"SELECT COUNT(*) FROM `buy` WHERE `member_id` = '{USER_ID}' AND `goods_id` = {goods_id} AND `rate` IS NOT NULL;"
        cursor.execute(sql)
        trate = cursor.fetchall()
        if trate or trate[0][0] == 0:
            if trate[0][0] == 0:#如果沒評價過就可以評價
                can_rate = "1"

    #建立商品資訊字典
    goods = {}
    categories = []
    last_category = ""
    if goods_id[0]=="1":#書
        sql=f"SELECT `goods_book_publisher` FROM `goods_book` WHERE `goods_book_id` = {goods_id};"
        cursor.execute(sql)
        goods_book_publisher = cursor.fetchall()
        if not goods_book_publisher:
            goods_book_publisher = ""
        #取得分類
        sql=f"SELECT `category` FROM `goods_book_category` WHERE `goods_book_id` = {goods_id};"
        cursor.execute(sql)
        categories_fetch = cursor.fetchall()
        if categories_fetch:
            i=0
            while i<len(categories_fetch):
                categories.append(categories_fetch[i][0])
                i+=1
            last_category = categories[len(categories)-1]
        goods = {"goods_id":goods_id,"goods_name":goods_name,"goods_picture":goods_picture,"goods_describe":goods_describe,"goods_author":goods_author,"goods_price":goods_price,"goods_quantity":goods_quantity,"goods_dates":goods_dates,"goods_rate":goods_rate,"goods_book_publisher":goods_book_publisher[0][0],"categories":categories,"last_category":last_category}
                  
    elif goods_id[0]=="2":#CD
        #取得分類
        sql=f"SELECT `category` FROM `goods_CD` WHERE `goods_CD_id` = {goods_id};"
        cursor.execute(sql)
        categories_fetch = cursor.fetchall()
        if categories_fetch:
            i=0
            while i<len(categories_fetch):
                categories.append(categories_fetch[i][0])
                i+=1
            last_category = categories[len(categories)-1]
        goods = {"goods_id":goods_id,"goods_name":goods_name,"goods_picture":goods_picture,"goods_describe":goods_describe,"goods_author":goods_author,"goods_price":goods_price,"goods_quantity":goods_quantity,"goods_dates":goods_dates,"goods_rate":goods_rate,"categories":categories,"last_category":last_category}
    #取得評價文字
    rates = []
    sql = f"SELECT `member_id`,`rate` FROM `buy` WHERE `rate` IS NOT NULL AND `goods_id` = {goods_id};"
    cursor.execute(sql)
    rate_fetch = cursor.fetchall()
    if rate_fetch:
        i=0
        while i<len(rate_fetch):
            rates.append({"member_id":rate_fetch[i][0],"text":rate_fetch[i][1]})
            i+=1

    connection.commit()
    overflow = "0"
    return render_template("goods_info.html",num_error=num_error,is_stop_supply=is_stop_supply,rates=rates,can_star_rate=can_star_rate,can_report=can_report,overflow=overflow,IS_LOGIN=IS_LOGIN,USER_NAME=USER_NAME,USER_AVATAR_SRC=USER_AVATAR_SRC,goods=goods,can_rate=can_rate,seller=seller,USER_ID=USER_ID)

#新增商品提交
@app.route("/add_goods",methods=['GET','POST'])
def add_goods():
    global USER_ID
    global IS_LOGIN
    global USER_NAME
    global USER_AVATAR_SRC
    global SRC
    cursor = connection.cursor()
    #book_or_cd = 

    #商品資訊
    member_id = USER_ID
    goods_id = ""
    num_error="0"
    #booknum[0][0] int
    #booknum[0] tuple
    #booknum list
    #取得商品種類
    #goods_type = str(request.args.get('gtype'))
    #print(request.form)
    #print(goods_type)
    goods_quantity = int(request.values['goods_quantity'])
    if goods_quantity>0:
        goods_type = request.values['book_or_CD']
        goods_book_publisher = ""
        #書
        if goods_type == "book":
            cursor.execute("SELECT COUNT(*) FROM `goods_book`;")
            booknum = cursor.fetchall()
            if booknum or booknum[0][0] == 0:
                goods_id = str(booknum[0][0] + 1001)
                goods_book_publisher = request.values['goods_book_publisher']
                if not goods_book_publisher:
                    goods_book_publisher = "未知"
        #CD
        if goods_type == "CD":

            cursor.execute("SELECT COUNT(*) FROM `goods` WHERE goods_id >= 2000 AND goods_id <= 2999;")
            CDnum = cursor.fetchall()
            if CDnum or CDnum[0][0] == 0:
                goods_id = str(CDnum[0][0] + 2001)

        goods_name = request.values['goods_name']
        goods_describe = request.values['goods_describe']
        goods_author = request.values['goods_author']
        goods_price = request.values['goods_price']
        goods_rate = -1
        #取得上架時間
        localtime = time.localtime()
        goods_dates = time.strftime("%Y-%m-%d", localtime)
        #取得商品圖片
        global BASEPATH
        if not os.path.isdir(os.path.join(BASEPATH,USER_ID)):
            os.mkdir(os.path.join(BASEPATH,USER_ID))
        picture = request.files.get("goods_picture")
        format = ""
        if picture:
            i=len(picture.filename)-1
            while picture.filename[i] != "." and i>0:
                i-=1
            j=0
            format = picture.filename[i:]
        fileName = goods_id
        if format == '.jpg':
            fileName+=".jpg"
        elif format == '.png':
            fileName+=".png"
        upload_path = os.path.join(BASEPATH,USER_ID,str(fileName))
        if picture:
            picture.save(upload_path)
        #取得商品分類
        #書為0~12,CD為13~30
        add_categories = []
        if goods_type == "book":
            i=0
            while i<13:
                cname = f"{i}"
                check = cname in request.form
                if check:
                    cvalue = str(request.values[cname])
                    add_categories.append(cvalue)
                i+=1
        else:
            i=13
            while i<31:
                cname = f"{i}"
                check = cname in request.form
                if check:
                    cvalue = str(request.values[cname])
                    add_categories.append(cvalue)
                i+=1
        #取得商品新舊程度
        new_or_old = request.values['new_or_old']
        if not new_or_old:
            new_or_old = "未知"
        #取得商品是否接受競標
        can_bid = request.values['can_bid']
        #儲存商品資訊
        sql=f"insert into `goods` values('{member_id}',{goods_id},'{goods_name}','{fileName}','{goods_describe}','{goods_author}',{goods_price},{goods_quantity},'{goods_dates}',{goods_rate},1,{can_bid});"
        cursor.execute(sql)
        #儲存出版社
        if goods_type == "book":
            sql=f"insert into `goods_book` values({goods_id},'{goods_book_publisher}');"
            cursor.execute(sql)
        #儲存商品分類
        i=0
        while i<len(add_categories):
            if goods_type == "book":#書
                sql=f"insert into `goods_book_category` values({goods_id},'{add_categories[i]}');"
                cursor.execute(sql)
                if i==len(add_categories)-1:
                    sql=f"insert into `goods_book_category` values({goods_id},'{new_or_old}');"
                    cursor.execute(sql)
            else:
                sql=f"insert into `goods_CD` values({goods_id},'{add_categories[i]}');"
                cursor.execute(sql)
                if i==len(add_categories)-1:
                    sql=f"insert into `goods_book_category` values({goods_id},'{new_or_old}');"
                    cursor.execute(sql)
            i+=1
    else:
        num_error = "1"
    
    ########讀取商品資料
    if IS_LOGIN == "1":
        need_send = "0"
        id = request.args.get('id')
        seller = {}
        member_id = ""
        if id:#他人賣場
            member_id = id
            sql=f"SELECT `name`,`picture` FROM `member` WHERE `member_id` = '{member_id}';"
            cursor.execute(sql)
            seller_info = cursor.fetchall()
            if seller_info:
                seller_name = seller_info[0][0]
                seller_picture = seller_info[0][1]
                if seller_picture:
                    seller_picture = SRC + "/" + member_id + "/" + seller_picture
                else:
                    seller_picture = ""
                seller = {"seller_id":member_id,"seller_name":seller_name,"seller_picture":seller_picture}
        else:#本人
            member_id = USER_ID
            #判斷是否需出貨
            sql = f"SELECT `goods_status` FROM `transaction_record_goods` WHERE `transaction_record_goods`.`goods_id` IN (SELECT `goods`.`goods_id` FROM `goods` WHERE `goods`.`member_id` = '{member_id}');"
            cursor.execute(sql)
            goods_status_fetch = cursor.fetchall()
            if goods_status_fetch:
                i=0
                while i<len(goods_status_fetch):
                    goods_status = str(goods_status_fetch[i][0])
                    if goods_status == "0":
                        need_send = "1"
                        break
                    i+=1
            seller = {"seller_id":member_id,"seller_name":USER_NAME,"seller_picture":USER_AVATAR_SRC}
        #讀取商品資料
        sql=f"SELECT * FROM `goods` WHERE `member_id` = '{member_id}';"
        cursor.execute(sql)
        goods_datas = cursor.fetchall()
        goods = []

        if goods_datas:
            i=0
            while i<len(goods_datas):
                goodsub = []
                j=0
                while j<4 and i<len(goods_datas):
                    goods_id = str(goods_datas[i][1])
                    goods_name = goods_datas[i][2]
                    goods_picture = goods_datas[i][3]
                    if goods_picture:
                        goods_picture = SRC + "/" +member_id + "/" + goods_picture
                    else:
                        goods_picture = ""
                    goods_author = goods_datas[i][5]
                    goods_price = goods_datas[i][6]
                    goods_rate = goods_datas[i][9]
                    #商品分類
                    if str(goods_id[0])=="1":#書
                        sql=f"SELECT `category` FROM `goods_book_category`,`goods` WHERE `goods_book_id` = `goods_id` AND `goods_id` = {goods_id};"
                        cursor.execute(sql)
                        categories = cursor.fetchall()
                        goodsub.append({"goods_id":goods_id,"goods_name":goods_name,"goods_picture":goods_picture,"goods_author":goods_author,"goods_price":goods_price,"goods_rate":goods_rate,"categories":categories})
                    elif str(goods_id[0])=="2":#CD 
                        sql=f"SELECT `category` FROM `goods_CD`,`goods` WHERE `goods_CD_id` = `goods_id` AND `goods_id` = {goods_id};"
                        cursor.execute(sql)
                        categories = cursor.fetchall()
                        goodsub.append({"goods_id":goods_id,"goods_name":goods_name,"goods_picture":goods_picture,"goods_author":goods_author,"goods_price":goods_price,"goods_rate":goods_rate,"categories":categories})
                    i+=1
                    j+=1
                #print(goodsub)
                goods.append(goodsub)
                
        return render_template("seller.html",num_error=num_error,need_send=need_send,seller=seller,IS_LOGIN=IS_LOGIN,USER_ID=USER_ID,USER_CARD=USER_CARD,USER_NAME=USER_NAME,USER_AVATAR_SRC=USER_AVATAR_SRC,goods=goods)
    else:
        return render_template("seller.html",IS_LOGIN=IS_LOGIN)

#加入購物車
@app.route("/add_to_shopping_cart", methods=['POST','GET'])
def add_to_shopping_cart():
    global IS_LOGIN
    global USER_ID
    global USER_AVATAR_SRC
    global USER_NAME
    global is_stop_supply
    if IS_LOGIN == "":
        return render_template("shopping_cart.html",IS_LOGIN=IS_LOGIN)
    cursor = connection.cursor()
    goods_id = str(request.args.get('gid'))
    goods_amount = int(request.values['goods_amount'])
    overflow = "0"
    selected = "0"
    num_error = "0"
    #取得商品剩餘數量
    sql=f"SELECT `goods_quantity` FROM `goods` WHERE `goods_id` = {goods_id};"
    cursor.execute(sql)
    goods_max_amount = cursor.fetchall()
    if goods_max_amount:
        #判斷是否已選過
        sql=f"SELECT `goods_id` FROM `shopping_cart` WHERE `member_id` = '{USER_ID}';"
        cursor.execute(sql)
        select_fetch = cursor.fetchall()
        if select_fetch:
            i=0
            while i<len(select_fetch):
                if goods_id == str(select_fetch[i][0]):
                    selected = "1"
                    break
                i+=1
        #如果溢位或已選過就返回原本詳細頁面
        if (goods_max_amount[0][0] < goods_amount) or selected == "1" or goods_amount <1:
            if goods_amount<1:
                num_error = "1"
            if (goods_max_amount[0][0] < goods_amount):
                overflow = "1"
            ######################
            #更新商品綜合評價
            sql=f"SELECT `star_rate` FROM `buy` WHERE `star_rate` <> -1 AND goods_id = {goods_id};"
            cursor.execute(sql)
            goods_rate_up = cursor.fetchall()
            avg = []
            if goods_rate_up:
                i=0
                while i<len(goods_rate_up):
                    avg.append(int(goods_rate_up[i][0]))
                    i+=1
                goods_avg = statistics.mean(avg)
                goods_avg = round(goods_avg,1)
                sql=f"UPDATE `goods` SET `goods_rate` = {goods_avg} WHERE `goods_id` = {goods_id};"
                cursor.execute(sql)
            #取得商品資訊
            sql=f"SELECT * FROM `goods` WHERE `goods_id` = {goods_id};"
            cursor.execute(sql)
            goods_info = cursor.fetchall()
            seller_name = ""
            seller_picture = ""
            seller = {}
            if goods_info:
                seller_id = goods_info[0][0]
                if seller_id:
                    sql=f"SELECT `name`,`picture` FROM `member` WHERE `member_id` = '{seller_id}';"
                    cursor.execute(sql)
                    seller_info = cursor.fetchall()
                    if seller_info:
                        seller_name = seller_info[0][0]
                        seller_picture = seller_info[0][1]
                        if seller_picture:
                            seller_picture = SRC + "/" +seller_id + "/" + seller_picture
                        else:
                            seller_picture = ""
                        if seller_name:
                            #建立賣家資訊字典
                            seller = {"seller_id":seller_id,"seller_name":seller_name,"seller_avatar":seller_picture}
                goods_name = goods_info[0][2]
                goods_picture = goods_info[0][3]
                if goods_picture:
                    goods_picture = SRC + "/" +seller_id + "/" + goods_picture
                else:
                    goods_picture = ""
                goods_describe = goods_info[0][4]
                goods_author = goods_info[0][5]
                goods_price = goods_info[0][6]
                goods_quantity = goods_info[0][7]
                goods_dates = goods_info[0][8]
                goods_rate = goods_info[0][9]
            #根據交易紀錄判斷是否可評價
            can_star_rate = ""
            can_report = ""
            can_rate = ""
            #是否有買過
            sql=f"SELECT COUNT(*) FROM `buy` WHERE `member_id` = '{USER_ID}' AND `goods_id` = {goods_id};"
            cursor.execute(sql)
            bye_ed = cursor.fetchall()
            if bye_ed:
                if bye_ed[0][0] > 0:
                    #是否有檢舉過
                    if seller_id:
                        sql=f"SELECT COUNT(*) FROM `report` WHERE `member_id` = '{USER_ID}' AND `seller_id` = '{seller_id}';"
                        cursor.execute(sql)
                        reported = cursor.fetchall()
                        if reported or reported[0][0] == 0:
                            if reported[0][0] == 0:#如果沒檢舉過就可以檢舉
                                can_report = "1"

                    #是否有評價過(按鈕)
                    sql=f"SELECT COUNT(*) FROM `buy` WHERE `member_id` = '{USER_ID}' AND `goods_id` = {goods_id} AND `star_rate` <> -1;"
                    cursor.execute(sql)
                    srate = cursor.fetchall()
                    if srate or srate[0][0] == 0:
                        if srate[0][0] == 0:#如果沒評價過就可以評價
                            can_star_rate = "1"

                    #是否有評價過(文字)
                    sql=f"SELECT COUNT(*) FROM `buy` WHERE `member_id` = '{USER_ID}' AND `goods_id` = {goods_id} AND `rate` IS NOT NULL;"
                    cursor.execute(sql)
                    trate = cursor.fetchall()
                    if trate or trate[0][0] == 0:
                        if trate[0][0] == 0:#如果沒評價過就可以評價
                            can_rate = "1"
            
            #建立商品資訊字典
            goods = {}
            categories = []
            last_category = ""
            if goods_id[0]=="1":#書
                sql=f"SELECT `goods_book_publisher` FROM `goods_book` WHERE `goods_book_id` = {goods_id};"
                cursor.execute(sql)
                goods_book_publisher = cursor.fetchall()
                if not goods_book_publisher:
                    goods_book_publisher = ""
                #取得分類
                sql=f"SELECT `category` FROM `goods_book_category` WHERE `goods_book_id` = {goods_id};"
                cursor.execute(sql)
                categories_fetch = cursor.fetchall()
                if categories_fetch:
                    i=0
                    while i<len(categories_fetch):
                        categories.append(categories_fetch[i][0])
                        i+=1
                    last_category = categories[len(categories)-1]
                goods = {"goods_id":goods_id,"goods_name":goods_name,"goods_picture":goods_picture,"goods_describe":goods_describe,"goods_author":goods_author,"goods_price":goods_price,"goods_quantity":goods_quantity,"goods_dates":goods_dates,"goods_rate":goods_rate,"goods_book_publisher":goods_book_publisher[0][0],"categories":categories,"last_category":last_category}               
            elif goods_id[0]=="2":#CD
                #取得分類
                sql=f"SELECT `category` FROM `goods_CD` WHERE `goods_CD_id` = {goods_id};"
                cursor.execute(sql)
                categories_fetch = cursor.fetchall()
                if categories_fetch:
                    i=0
                    while i<len(categories_fetch):
                        categories.append(categories_fetch[i][0])
                        i+=1
                    last_category = categories[len(categories)-1]
                goods = {"goods_id":goods_id,"goods_name":goods_name,"goods_picture":goods_picture,"goods_describe":goods_describe,"goods_author":goods_author,"goods_price":goods_price,"goods_quantity":goods_quantity,"goods_dates":goods_dates,"goods_rate":goods_rate,"categories":categories,"last_category":last_category}    
            #取得評價文字
            rates = []
            sql = f"SELECT `member_id`,`rate` FROM `buy` WHERE `rate` IS NOT NULL AND `goods_id` = {goods_id};"
            cursor.execute(sql)
            rate_fetch = cursor.fetchall()
            if rate_fetch:
                i=0
                while i<len(rate_fetch):
                    rates.append({"member_id":rate_fetch[i][0],"text":rate_fetch[i][1]})
                    i+=1
            connection.commit()
            return render_template("goods_info.html",num_error=num_error,is_stop_supply=is_stop_supply,can_star_rate=can_star_rate,rates=rates,can_report=can_report,overflow=overflow,selected=selected,IS_LOGIN=IS_LOGIN,USER_NAME=USER_NAME,USER_AVATAR_SRC=USER_AVATAR_SRC,goods=goods,can_rate=can_rate,seller=seller,USER_ID=USER_ID)
            ######################溢位結束
    
    #插入購物車
    goods_id = str(request.args.get('gid'))
    sql = f"SELECT `goods_name`,`goods_price`,`goods_picture` FROM `goods` WHERE `goods_id` = {goods_id};"
    cursor.execute(sql)
    insertfetch = cursor.fetchall()
    if insertfetch:
        goods_name = insertfetch[0][0]
        goods_price = int(insertfetch[0][1])
        goods_picture = insertfetch[0][2]
        if not goods_picture:
            goods_picture = ""
        goods_sum_price = goods_amount * goods_price
        sql = f"insert into `shopping_cart` values('{USER_ID}',{goods_id},'{goods_name}',{goods_sum_price},'{goods_picture}',{goods_amount});"
        cursor.execute(sql)

    ####取得購物車資料
    sql=f"SELECT * FROM `shopping_cart` WHERE `member_id` = '{USER_ID}';"
    cursor.execute(sql)
    shopping_datas = cursor.fetchall()
    goods_id = ""
    goods = []
    no_goods = "1"
    all_sum_price = 0
    if shopping_datas:
        i=0
        while i<len(shopping_datas):
            goods_id = str(shopping_datas[i][1])
            sql = f"SELECT `member_id` FROM `goods` WHERE `goods_id` = {goods_id};"
            cursor.execute(sql)
            member_id_fetch = cursor.fetchall()
            member_id = ""
            if member_id_fetch:
                member_id = member_id_fetch[0][0]
            goods_name = shopping_datas[i][2]
            goods_sum_price = shopping_datas[i][3]
            all_sum_price += goods_sum_price
            goods_picture = shopping_datas[i][4]
            if goods_picture:
                goods_picture = SRC + "/" + member_id + "/" + goods_picture
            else:
                goods_picture = ""
            goods_amount = shopping_datas[i][5]
            goods_price = int(goods_sum_price / goods_amount)
            #取得物品剩餘數量
            sql = f"SELECT `goods_quantity` FROM `goods` WHERE `goods_id` = {goods_id};"
            cursor.execute(sql)
            goods_quantity_fetch = cursor.fetchall()
            goods_quantity = ""
            if goods_quantity_fetch:
                goods_quantity = str(goods_quantity_fetch[0][0])
            goods.append({"goods_id":goods_id,"goods_name":goods_name,"goods_sum_price":goods_sum_price,"goods_price":goods_price,"goods_picture":goods_picture,"goods_amount":goods_amount,"goods_quantity":goods_quantity})
            i+=1
    if goods:
        no_goods = "0"
    connection.commit()
    return render_template("shopping_cart.html",all_sum_price=all_sum_price,IS_LOGIN=IS_LOGIN,USER_NAME=USER_NAME,USER_AVATAR_SRC=USER_AVATAR_SRC,goods=goods,no_goods=no_goods)

#檢舉提交
@app.route("/report", methods=['POST','GET'])
def report():
    #print(request.form)
    #從網址列拿資料
    goods_id = str(request.args.get('gid'))
    member_id = str(request.args.get('mid'))
    seller_id = str(request.args.get('sid'))
    #print(goods_id)
    global IS_LOGIN
    global USER_AVATAR_SRC
    global USER_NAME
    global USER_ID
    global SRC
    global is_stop_supply
    cursor = connection.cursor()

    #檢舉
    report_text = request.values['report_text']
    #儲存檢舉資訊
    print(report_text)
    if report_text:
        sql=f"insert into `report` values('{member_id}','{seller_id}','{report_text}');"
        cursor.execute(sql)
    
    #更新商品綜合評價
    sql=f"SELECT `star_rate` FROM `buy` WHERE `star_rate` <> -1 AND goods_id = {goods_id};"
    cursor.execute(sql)
    goods_rate_up = cursor.fetchall()
    avg = []
    if goods_rate_up:
        i=0
        while i<len(goods_rate_up):
            avg.append(int(goods_rate_up[i][0]))
            i+=1
        goods_avg = statistics.mean(avg)
        goods_avg = round(goods_avg,1)
        sql=f"UPDATE `goods` SET `goods_rate` = {goods_avg} WHERE `goods_id` = {goods_id};"
        cursor.execute(sql)

    #取得商品資訊
    sql=f"SELECT * FROM `goods` WHERE `goods_id` = {goods_id};"
    cursor.execute(sql)
    goods_info = cursor.fetchall()
    seller_name = ""
    seller_picture = ""
    seller = {}
    if goods_info:
        seller_id = goods_info[0][0]
        if seller_id:
            sql=f"SELECT `name`,`picture` FROM `member` WHERE `member_id` = '{seller_id}';"
            cursor.execute(sql)
            seller_info = cursor.fetchall()
            if seller_info:
                seller_name = seller_info[0][0]
                seller_picture = seller_info[0][1]
                if seller_picture:
                    seller_picture = SRC + "/" +seller_id + "/" + seller_picture
                else:
                    seller_picture = ""
                if seller_name:
                    #建立賣家資訊字典
                    seller = {"seller_id":seller_id,"seller_name":seller_name,"seller_avatar":seller_picture}
        goods_name = goods_info[0][2]
        goods_picture = goods_info[0][3]
        if goods_picture:
            goods_picture = SRC + "/" +seller_id + "/" + goods_picture
        else:
            goods_picture = ""
        goods_describe = goods_info[0][4]
        goods_author = goods_info[0][5]
        goods_price = goods_info[0][6]
        goods_quantity = goods_info[0][7]
        goods_dates = goods_info[0][8]
        goods_rate = goods_info[0][9]
    #根據交易紀錄判斷是否可評價&檢舉
    can_star_rate = ""
    can_report = ""
    can_rate = ""
    #是否有買過
    sql=f"SELECT COUNT(*) FROM `buy` WHERE `member_id` = '{USER_ID}' AND `goods_id` = {goods_id};"
    cursor.execute(sql)
    bye_ed = cursor.fetchall()
    if bye_ed:
        if bye_ed[0][0] > 0:
            #是否有評價過(按鈕)
            sql=f"SELECT COUNT(*) FROM `buy` WHERE `member_id` = '{USER_ID}' AND `goods_id` = {goods_id} AND `star_rate` <> -1;"
            cursor.execute(sql)
            srate = cursor.fetchall()
            if srate or srate[0][0] == 0:
                if srate[0][0] == 0:#如果沒評價過就可以評價
                    can_star_rate = "1"
            
            #是否有評價過(文字)
            sql=f"SELECT COUNT(*) FROM `buy` WHERE `member_id` = '{USER_ID}' AND `goods_id` = {goods_id} AND `rate` IS NOT NULL;"
            cursor.execute(sql)
            trate = cursor.fetchall()
            if trate or trate[0][0] == 0:
                if trate[0][0] == 0:#如果沒評價過就可以評價
                    can_rate = "1"

    #建立商品資訊字典
    goods = {}
    categories = []
    last_category = ""
    if goods_id[0]=="1":#書
        sql=f"SELECT `goods_book_publisher` FROM `goods_book` WHERE `goods_book_id` = {goods_id};"
        cursor.execute(sql)
        goods_book_publisher = cursor.fetchall()
        if not goods_book_publisher:
            goods_book_publisher = ""
        #取得分類
        sql=f"SELECT `category` FROM `goods_book_category` WHERE `goods_book_id` = {goods_id};"
        cursor.execute(sql)
        categories_fetch = cursor.fetchall()
        if categories_fetch:
            i=0
            while i<len(categories_fetch):
                categories.append(categories_fetch[i][0])
                i+=1
            last_category = categories[len(categories)-1]
        goods = {"goods_id":goods_id,"goods_name":goods_name,"goods_picture":goods_picture,"goods_describe":goods_describe,"goods_author":goods_author,"goods_price":goods_price,"goods_quantity":goods_quantity,"goods_dates":goods_dates,"goods_rate":goods_rate,"goods_book_publisher":goods_book_publisher[0][0],"categories":categories,"last_category":last_category}
                  
    elif goods_id[0]=="2":#CD
        #取得分類
        sql=f"SELECT `category` FROM `goods_CD` WHERE `goods_CD_id` = {goods_id};"
        cursor.execute(sql)
        categories_fetch = cursor.fetchall()
        if categories_fetch:
            i=0
            while i<len(categories_fetch):
                categories.append(categories_fetch[i][0])
                i+=1
            last_category = categories[len(categories)-1]
        goods = {"goods_id":goods_id,"goods_name":goods_name,"goods_picture":goods_picture,"goods_describe":goods_describe,"goods_author":goods_author,"goods_price":goods_price,"goods_quantity":goods_quantity,"goods_dates":goods_dates,"goods_rate":goods_rate,"categories":categories,"last_category":last_category}
    #取得評價文字
    rates = []
    sql = f"SELECT `member_id`,`rate` FROM `buy` WHERE `rate` IS NOT NULL AND `goods_id` = {goods_id};"
    cursor.execute(sql)
    rate_fetch = cursor.fetchall()
    if rate_fetch:
        i=0
        while i<len(rate_fetch):
            rates.append({"member_id":rate_fetch[i][0],"text":rate_fetch[i][1]})
            i+=1

    connection.commit()
    overflow = "0"
    return render_template("goods_info.html",is_stop_supply=is_stop_supply,rates=rates,can_star_rate=can_star_rate,can_report=can_report,overflow=overflow,IS_LOGIN=IS_LOGIN,USER_NAME=USER_NAME,USER_AVATAR_SRC=USER_AVATAR_SRC,goods=goods,can_rate=can_rate,seller=seller,USER_ID=USER_ID)

#暫停供貨提交
@app.route("/stop_supply", methods=['POST','GET'])
def stop_supply():
    #print(request.form)
    #從網址列拿資料
    global is_stop_supply
    cursor = connection.cursor()
    status = str(request.args.get('sta'))
    goods_id = str(request.args.get('gid'))
    if status == "1":
        is_stop_supply = "1"
        sql = f"UPDATE `goods` SET `supply_status` = 0 WHERE `goods_id` = {goods_id};"
        cursor.execute(sql)
    else:
        is_stop_supply = "0"
        sql = f"UPDATE `goods` SET `supply_status` = 1 WHERE `goods_id` = {goods_id};"
        cursor.execute(sql)
    #print(goods_id)
    
    global IS_LOGIN
    global USER_AVATAR_SRC
    global USER_NAME
    global USER_ID
    global SRC
    
    
    #更新商品綜合評價
    sql=f"SELECT `star_rate` FROM `buy` WHERE `star_rate` <> -1 AND goods_id = {goods_id};"
    cursor.execute(sql)
    goods_rate_up = cursor.fetchall()
    avg = []
    if goods_rate_up:
        i=0
        while i<len(goods_rate_up):
            avg.append(int(goods_rate_up[i][0]))
            i+=1
        goods_avg = statistics.mean(avg)
        goods_avg = round(goods_avg,1)
        sql=f"UPDATE `goods` SET `goods_rate` = {goods_avg} WHERE `goods_id` = {goods_id};"
        cursor.execute(sql)

    #取得商品資訊
    sql=f"SELECT * FROM `goods` WHERE `goods_id` = {goods_id};"
    cursor.execute(sql)
    goods_info = cursor.fetchall()
    seller_name = ""
    seller_picture = ""
    seller = {}
    if goods_info:
        seller_id = goods_info[0][0]
        if seller_id:
            sql=f"SELECT `name`,`picture` FROM `member` WHERE `member_id` = '{seller_id}';"
            cursor.execute(sql)
            seller_info = cursor.fetchall()
            if seller_info:
                seller_name = seller_info[0][0]
                seller_picture = seller_info[0][1]
                if seller_picture:
                    seller_picture = SRC + "/" +seller_id + "/" + seller_picture
                else:
                    seller_picture = ""
                if seller_name:
                    #建立賣家資訊字典
                    seller = {"seller_id":seller_id,"seller_name":seller_name,"seller_avatar":seller_picture}
        goods_name = goods_info[0][2]
        goods_picture = goods_info[0][3]
        if goods_picture:
            goods_picture = SRC + "/" +seller_id + "/" + goods_picture
        else:
            goods_picture = ""
        goods_describe = goods_info[0][4]
        goods_author = goods_info[0][5]
        goods_price = goods_info[0][6]
        goods_quantity = goods_info[0][7]
        goods_dates = goods_info[0][8]
        goods_rate = goods_info[0][9]
    #根據交易紀錄判斷是否可評價&檢舉
    can_star_rate = ""
    can_report = ""
    can_rate = ""
    #是否有買過
    sql=f"SELECT COUNT(*) FROM `buy` WHERE `member_id` = '{USER_ID}' AND `goods_id` = {goods_id};"
    cursor.execute(sql)
    bye_ed = cursor.fetchall()
    if bye_ed:
        if bye_ed[0][0] > 0:
            #是否有檢舉過
            if seller_id:
                sql=f"SELECT COUNT(*) FROM `report` WHERE `member_id` = '{USER_ID}' AND `seller_id` = '{seller_id}';"
                cursor.execute(sql)
                reported = cursor.fetchall()
                if reported or reported[0][0] == 0:
                    if reported[0][0] == 0:#如果沒檢舉過就可以檢舉
                        can_report = "1"

            #是否有評價過(按鈕)
            sql=f"SELECT COUNT(*) FROM `buy` WHERE `member_id` = '{USER_ID}' AND `goods_id` = {goods_id} AND `star_rate` <> -1;"
            cursor.execute(sql)
            srate = cursor.fetchall()
            if srate or srate[0][0] == 0:
                if srate[0][0] == 0:#如果沒評價過就可以評價
                    can_star_rate = "1"
            
            #是否有評價過(文字)
            sql=f"SELECT COUNT(*) FROM `buy` WHERE `member_id` = '{USER_ID}' AND `goods_id` = {goods_id} AND `rate` IS NOT NULL;"
            cursor.execute(sql)
            trate = cursor.fetchall()
            if trate or trate[0][0] == 0:
                if trate[0][0] == 0:#如果沒評價過就可以評價
                    can_rate = "1"

    #建立商品資訊字典
    goods = {}
    categories = []
    last_category = ""
    if goods_id[0]=="1":#書
        sql=f"SELECT `goods_book_publisher` FROM `goods_book` WHERE `goods_book_id` = {goods_id};"
        cursor.execute(sql)
        goods_book_publisher = cursor.fetchall()
        if not goods_book_publisher:
            goods_book_publisher = ""
        #取得分類
        sql=f"SELECT `category` FROM `goods_book_category` WHERE `goods_book_id` = {goods_id};"
        cursor.execute(sql)
        categories_fetch = cursor.fetchall()
        if categories_fetch:
            i=0
            while i<len(categories_fetch):
                categories.append(categories_fetch[i][0])
                i+=1
            last_category = categories[len(categories)-1]
        goods = {"goods_id":goods_id,"goods_name":goods_name,"goods_picture":goods_picture,"goods_describe":goods_describe,"goods_author":goods_author,"goods_price":goods_price,"goods_quantity":goods_quantity,"goods_dates":goods_dates,"goods_rate":goods_rate,"goods_book_publisher":goods_book_publisher[0][0],"categories":categories,"last_category":last_category}
                  
    elif goods_id[0]=="2":#CD
        #取得分類
        sql=f"SELECT `category` FROM `goods_CD` WHERE `goods_CD_id` = {goods_id};"
        cursor.execute(sql)
        categories_fetch = cursor.fetchall()
        if categories_fetch:
            i=0
            while i<len(categories_fetch):
                categories.append(categories_fetch[i][0])
                i+=1
            last_category = categories[len(categories)-1]
        goods = {"goods_id":goods_id,"goods_name":goods_name,"goods_picture":goods_picture,"goods_describe":goods_describe,"goods_author":goods_author,"goods_price":goods_price,"goods_quantity":goods_quantity,"goods_dates":goods_dates,"goods_rate":goods_rate,"categories":categories,"last_category":last_category}
    #取得評價文字
    rates = []
    sql = f"SELECT `member_id`,`rate` FROM `buy` WHERE `rate` IS NOT NULL AND `goods_id` = {goods_id};"
    cursor.execute(sql)
    rate_fetch = cursor.fetchall()
    if rate_fetch:
        i=0
        while i<len(rate_fetch):
            rates.append({"member_id":rate_fetch[i][0],"text":rate_fetch[i][1]})
            i+=1

    connection.commit()
    overflow = "0"
    return render_template("goods_info.html",is_stop_supply=is_stop_supply,rates=rates,can_star_rate=can_star_rate,can_report=can_report,overflow=overflow,IS_LOGIN=IS_LOGIN,USER_NAME=USER_NAME,USER_AVATAR_SRC=USER_AVATAR_SRC,goods=goods,can_rate=can_rate,seller=seller,USER_ID=USER_ID)

#刪除商品
@app.route("/delete_goods", methods=['POST','GET'])
def delete_goods():
    global IS_LOGIN
    global USER_AVATAR_SRC
    global USER_NAME
    global SRC
    cursor = connection.cursor()
    #刪除
    goods_id = str(request.args.get('gid'))
    sql = f"DELETE FROM `goods` WHERE `goods_id` = {goods_id};"
    cursor.execute(sql)
    #更新商品綜合評價
    sql=f"SELECT `goods_id` FROM `goods`;"
    cursor.execute(sql)
    goods_id_fetch = cursor.fetchall()
    if goods_id_fetch:
        k=0
        while k<len(goods_id_fetch):
            sql=f"SELECT `star_rate` FROM `buy` WHERE `star_rate` <> -1 AND goods_id = {goods_id_fetch[k][0]};"
            cursor.execute(sql)
            goods_rate_up = cursor.fetchall()
            avg = []
            if goods_rate_up:
                j=0
                while j<len(goods_rate_up):
                    avg.append(int(goods_rate_up[j][0]))
                    j+=1
                goods_avg = statistics.mean(avg)
                goods_avg = round(goods_avg,1)
                sql=f"UPDATE `goods` SET `goods_rate` = {goods_avg} WHERE `goods_id` = {goods_id_fetch[k][0]};"
                cursor.execute(sql)
            k+=1
    #取得資料庫所有商品資料
    sql="SELECT * FROM `goods` WHERE `goods_quantity` > 0 AND `supply_status` = 1;"
    cursor.execute(sql)
    goods_datas = cursor.fetchall()
    if goods_datas:
        i=0
        goods = []
        while i<len(goods_datas):
            goodsub = []
            j=0
            while j<4 and i<len(goods_datas):
                member_id = goods_datas[i][0]
                goods_id = str(goods_datas[i][1])
                goods_name = goods_datas[i][2]
                goods_picture = goods_datas[i][3]
                if goods_picture:
                    goods_picture = SRC + "/" +member_id + "/" + goods_picture
                else:
                    goods_picture = ""
                goods_author = goods_datas[i][5]
                goods_price = goods_datas[i][6]
                goods_rate = goods_datas[i][9]
                #商品分類
                if str(goods_id[0])=="1":#書
                    sql=f"SELECT `category` FROM `goods_book_category`,`goods` WHERE `goods_book_id` = `goods_id` AND `goods_id` = {goods_id};"
                    cursor.execute(sql)
                    categories = cursor.fetchall()
                    goodsub.append({"member_id":member_id,"goods_id":goods_id,"goods_name":goods_name,"goods_picture":goods_picture,"goods_author":goods_author,"goods_price":goods_price,"goods_rate":goods_rate,"categories":categories})
                elif str(goods_id[0])=="2":#CD 
                    sql=f"SELECT `category` FROM `goods_CD`,`goods` WHERE `goods_CD_id` = `goods_id` AND `goods_id` = {goods_id};"
                    cursor.execute(sql)
                    categories = cursor.fetchall()
                    goodsub.append({"member_id":member_id,"goods_id":goods_id,"goods_name":goods_name,"goods_picture":goods_picture,"goods_author":goods_author,"goods_price":goods_price,"goods_rate":goods_rate,"categories":categories})
                i+=1
                j+=1
            goods.append(goodsub)
    #取得評價前三高的商品圖片跟id
    slideshow = []
    sql=f"SELECT `goods_id`,`goods_picture`,`member_id` FROM `goods` WHERE `goods_quantity` > 0 AND `supply_status` = 1 ORDER BY `goods_rate` DESC LIMIT 3;"
    cursor.execute(sql)
    top3_fetch = cursor.fetchall()
    if top3_fetch:
        i=0
        while i<len(top3_fetch):
            top3_id = str(top3_fetch[i][0])
            top3_picture = top3_fetch[i][1]
            if top3_picture:
                top3_picture = SRC + "/" + str(top3_fetch[i][2]) + "/" + top3_picture
            else:
                top3_picture = ""
            i+=1
            slideshow.append({"goods_id":top3_id,"goods_picture":top3_picture})
    connection.commit()
    return render_template("home.html",slideshow=slideshow,IS_LOGIN=IS_LOGIN,USER_NAME=USER_NAME,USER_AVATAR_SRC=USER_AVATAR_SRC,goods=goods)

#提交數字評價
@app.route("/update_star_rate", methods=['POST','GET'])
def update_star_rate():
    global IS_LOGIN
    global USER_AVATAR_SRC
    global USER_NAME
    global USER_ID
    global SRC
    global is_stop_supply
    cursor = connection.cursor()

    goods_star_rate = request.values['goods_star_rate']
    goods_id = str(request.args.get('gid'))
    sql = f"SELECT `transaction_id` FROM `buy` WHERE `member_id` = '{USER_ID}' AND `goods_id` = {goods_id};"
    cursor.execute(sql)
    transaction_ids = cursor.fetchall()
    transaction_id = ""
    if transaction_ids:
        transaction_id = transaction_ids[0][0]
    sql = f"UPDATE `buy` SET `star_rate` = {goods_star_rate} WHERE `member_id` = '{USER_ID}' AND `goods_id` = {goods_id} AND `transaction_id` = {transaction_id};"
    cursor.execute(sql)
    
    #更新商品綜合評價
    sql=f"SELECT `star_rate` FROM `buy` WHERE `star_rate` <> -1 AND goods_id = {goods_id};"
    cursor.execute(sql)
    goods_rate_up = cursor.fetchall()
    avg = []
    if goods_rate_up:
        i=0
        while i<len(goods_rate_up):
            avg.append(int(goods_rate_up[i][0]))
            i+=1
        goods_avg = statistics.mean(avg)
        goods_avg = round(goods_avg,1)
        sql=f"UPDATE `goods` SET `goods_rate` = {goods_avg} WHERE `goods_id` = {goods_id};"
        cursor.execute(sql)

    #取得商品資訊
    sql=f"SELECT * FROM `goods` WHERE `goods_id` = {goods_id};"
    cursor.execute(sql)
    goods_info = cursor.fetchall()
    seller_name = ""
    seller_picture = ""
    seller = {}
    if goods_info:
        seller_id = goods_info[0][0]
        if seller_id:
            sql=f"SELECT `name`,`picture` FROM `member` WHERE `member_id` = '{seller_id}';"
            cursor.execute(sql)
            seller_info = cursor.fetchall()
            if seller_info:
                seller_name = seller_info[0][0]
                seller_picture = seller_info[0][1]
                if seller_picture:
                    seller_picture = SRC + "/" +seller_id + "/" + seller_picture
                else:
                    seller_picture = ""
                if seller_name:
                    #建立賣家資訊字典
                    seller = {"seller_id":seller_id,"seller_name":seller_name,"seller_avatar":seller_picture}
        goods_name = goods_info[0][2]
        goods_picture = goods_info[0][3]
        if goods_picture:
            goods_picture = SRC + "/" +seller_id + "/" + goods_picture
        else:
            goods_picture = ""
        goods_describe = goods_info[0][4]
        goods_author = goods_info[0][5]
        goods_price = goods_info[0][6]
        goods_quantity = goods_info[0][7]
        goods_dates = goods_info[0][8]
        goods_rate = goods_info[0][9]
    #根據交易紀錄判斷是否可評價&檢舉
    can_star_rate = ""
    can_report = ""
    can_rate = ""
    #是否有買過
    sql=f"SELECT COUNT(*) FROM `buy` WHERE `member_id` = '{USER_ID}' AND `goods_id` = {goods_id};"
    cursor.execute(sql)
    bye_ed = cursor.fetchall()
    if bye_ed:
        if bye_ed[0][0] > 0:
            #是否有檢舉過
            if seller_id:
                sql=f"SELECT COUNT(*) FROM `report` WHERE `member_id` = '{USER_ID}' AND `seller_id` = '{seller_id}';"
                cursor.execute(sql)
                reported = cursor.fetchall()
                if reported or reported[0][0] == 0:
                    if reported[0][0] == 0:#如果沒檢舉過就可以檢舉
                        can_report = "1"
            
            #是否有評價過(文字)
            sql=f"SELECT COUNT(*) FROM `buy` WHERE `member_id` = '{USER_ID}' AND `goods_id` = {goods_id} AND `rate` IS NOT NULL;"
            cursor.execute(sql)
            trate = cursor.fetchall()
            if trate or trate[0][0] == 0:
                if trate[0][0] == 0:#如果沒評價過就可以評價
                    can_rate = "1"

    #建立商品資訊字典
    goods = {}
    categories = []
    last_category = ""
    if goods_id[0]=="1":#書
        sql=f"SELECT `goods_book_publisher` FROM `goods_book` WHERE `goods_book_id` = {goods_id};"
        cursor.execute(sql)
        goods_book_publisher = cursor.fetchall()
        if not goods_book_publisher:
            goods_book_publisher = ""
        #取得分類
        sql=f"SELECT `category` FROM `goods_book_category` WHERE `goods_book_id` = {goods_id};"
        cursor.execute(sql)
        categories_fetch = cursor.fetchall()
        if categories_fetch:
            i=0
            while i<len(categories_fetch):
                categories.append(categories_fetch[i][0])
                i+=1
            last_category = categories[len(categories)-1]
        goods = {"goods_id":goods_id,"goods_name":goods_name,"goods_picture":goods_picture,"goods_describe":goods_describe,"goods_author":goods_author,"goods_price":goods_price,"goods_quantity":goods_quantity,"goods_dates":goods_dates,"goods_rate":goods_rate,"goods_book_publisher":goods_book_publisher[0][0],"categories":categories,"last_category":last_category}
                  
    elif goods_id[0]=="2":#CD
        #取得分類
        sql=f"SELECT `category` FROM `goods_CD` WHERE `goods_CD_id` = {goods_id};"
        cursor.execute(sql)
        categories_fetch = cursor.fetchall()
        if categories_fetch:
            i=0
            while i<len(categories_fetch):
                categories.append(categories_fetch[i][0])
                i+=1
            last_category = categories[len(categories)-1]
        goods = {"goods_id":goods_id,"goods_name":goods_name,"goods_picture":goods_picture,"goods_describe":goods_describe,"goods_author":goods_author,"goods_price":goods_price,"goods_quantity":goods_quantity,"goods_dates":goods_dates,"goods_rate":goods_rate,"categories":categories,"last_category":last_category}
    #取得評價文字
    rates = []
    sql = f"SELECT `member_id`,`rate` FROM `buy` WHERE `rate` IS NOT NULL AND `goods_id` = {goods_id};"
    cursor.execute(sql)
    rate_fetch = cursor.fetchall()
    if rate_fetch:
        i=0
        while i<len(rate_fetch):
            rates.append({"member_id":rate_fetch[i][0],"text":rate_fetch[i][1]})
            i+=1

    connection.commit()
    overflow = "0"
    return render_template("goods_info.html",is_stop_supply=is_stop_supply,rates=rates,can_star_rate=can_star_rate,can_report=can_report,overflow=overflow,IS_LOGIN=IS_LOGIN,USER_NAME=USER_NAME,USER_AVATAR_SRC=USER_AVATAR_SRC,goods=goods,can_rate=can_rate,seller=seller,USER_ID=USER_ID)

#提交文字評價
@app.route("/add_text_rate", methods=['POST','GET'])
def add_text_rate():
    global IS_LOGIN
    global USER_AVATAR_SRC
    global USER_NAME
    global USER_ID
    global SRC
    global is_stop_supply
    cursor = connection.cursor()

    goods_text_rate = request.values['goods_text_rate']
    goods_id = str(request.args.get('gid'))
    sql = f"SELECT `transaction_id` FROM `buy` WHERE `member_id` = '{USER_ID}' AND `goods_id` = {goods_id};"
    cursor.execute(sql)
    transaction_ids = cursor.fetchall()
    transaction_id = ""
    if transaction_ids:
        transaction_id = transaction_ids[0][0]
    sql = f"UPDATE `buy` SET `rate` = '{goods_text_rate}' WHERE `member_id` = '{USER_ID}' AND `goods_id` = {goods_id} AND `transaction_id` = {transaction_id};"
    cursor.execute(sql)
    
    #更新商品綜合評價
    sql=f"SELECT `star_rate` FROM `buy` WHERE `star_rate` <> -1 AND goods_id = {goods_id};"
    cursor.execute(sql)
    goods_rate_up = cursor.fetchall()
    avg = []
    if goods_rate_up:
        i=0
        while i<len(goods_rate_up):
            avg.append(int(goods_rate_up[i][0]))
            i+=1
        goods_avg = statistics.mean(avg)
        goods_avg = round(goods_avg,1)
        sql=f"UPDATE `goods` SET `goods_rate` = {goods_avg} WHERE `goods_id` = {goods_id};"
        cursor.execute(sql)

    #取得商品資訊
    sql=f"SELECT * FROM `goods` WHERE `goods_id` = {goods_id};"
    cursor.execute(sql)
    goods_info = cursor.fetchall()
    seller_name = ""
    seller_picture = ""
    seller = {}
    if goods_info:
        seller_id = goods_info[0][0]
        if seller_id:
            sql=f"SELECT `name`,`picture` FROM `member` WHERE `member_id` = '{seller_id}';"
            cursor.execute(sql)
            seller_info = cursor.fetchall()
            if seller_info:
                seller_name = seller_info[0][0]
                seller_picture = seller_info[0][1]
                if seller_picture:
                    seller_picture = SRC + "/" +seller_id + "/" + seller_picture
                else:
                    seller_picture = ""
                if seller_name:
                    #建立賣家資訊字典
                    seller = {"seller_id":seller_id,"seller_name":seller_name,"seller_avatar":seller_picture}
        goods_name = goods_info[0][2]
        goods_picture = goods_info[0][3]
        if goods_picture:
            goods_picture = SRC + "/" +seller_id + "/" + goods_picture
        else:
            goods_picture = ""
        goods_describe = goods_info[0][4]
        goods_author = goods_info[0][5]
        goods_price = goods_info[0][6]
        goods_quantity = goods_info[0][7]
        goods_dates = goods_info[0][8]
        goods_rate = goods_info[0][9]
    #根據交易紀錄判斷是否可評價&檢舉
    can_star_rate = ""
    can_report = ""
    can_rate = ""
    #是否有買過
    sql=f"SELECT COUNT(*) FROM `buy` WHERE `member_id` = '{USER_ID}' AND `goods_id` = {goods_id};"
    cursor.execute(sql)
    bye_ed = cursor.fetchall()
    if bye_ed:
        if bye_ed[0][0] > 0:
            #是否有檢舉過
            if seller_id:
                sql=f"SELECT COUNT(*) FROM `report` WHERE `member_id` = '{USER_ID}' AND `seller_id` = '{seller_id}';"
                cursor.execute(sql)
                reported = cursor.fetchall()
                if reported or reported[0][0] == 0:
                    if reported[0][0] == 0:#如果沒檢舉過就可以檢舉
                        can_report = "1"

            #是否有評價過(按鈕)
            sql=f"SELECT COUNT(*) FROM `buy` WHERE `member_id` = '{USER_ID}' AND `goods_id` = {goods_id} AND `star_rate` <> -1;"
            cursor.execute(sql)
            srate = cursor.fetchall()
            if srate or srate[0][0] == 0:
                if srate[0][0] == 0:#如果沒評價過就可以評價
                    can_star_rate = "1"

    #建立商品資訊字典
    goods = {}
    categories = []
    last_category = ""
    if goods_id[0]=="1":#書
        sql=f"SELECT `goods_book_publisher` FROM `goods_book` WHERE `goods_book_id` = {goods_id};"
        cursor.execute(sql)
        goods_book_publisher = cursor.fetchall()
        if not goods_book_publisher:
            goods_book_publisher = ""
        #取得分類
        sql=f"SELECT `category` FROM `goods_book_category` WHERE `goods_book_id` = {goods_id};"
        cursor.execute(sql)
        categories_fetch = cursor.fetchall()
        if categories_fetch:
            i=0
            while i<len(categories_fetch):
                categories.append(categories_fetch[i][0])
                i+=1
            last_category = categories[len(categories)-1]
        goods = {"goods_id":goods_id,"goods_name":goods_name,"goods_picture":goods_picture,"goods_describe":goods_describe,"goods_author":goods_author,"goods_price":goods_price,"goods_quantity":goods_quantity,"goods_dates":goods_dates,"goods_rate":goods_rate,"goods_book_publisher":goods_book_publisher[0][0],"categories":categories,"last_category":last_category}
                  
    elif goods_id[0]=="2":#CD
        #取得分類
        sql=f"SELECT `category` FROM `goods_CD` WHERE `goods_CD_id` = {goods_id};"
        cursor.execute(sql)
        categories_fetch = cursor.fetchall()
        if categories_fetch:
            i=0
            while i<len(categories_fetch):
                categories.append(categories_fetch[i][0])
                i+=1
            last_category = categories[len(categories)-1]
        goods = {"goods_id":goods_id,"goods_name":goods_name,"goods_picture":goods_picture,"goods_describe":goods_describe,"goods_author":goods_author,"goods_price":goods_price,"goods_quantity":goods_quantity,"goods_dates":goods_dates,"goods_rate":goods_rate,"categories":categories,"last_category":last_category}
    #取得評價文字
    rates = []
    sql = f"SELECT `member_id`,`rate` FROM `buy` WHERE `rate` IS NOT NULL AND `goods_id` = {goods_id};"
    cursor.execute(sql)
    rate_fetch = cursor.fetchall()
    if rate_fetch:
        i=0
        while i<len(rate_fetch):
            rates.append({"member_id":rate_fetch[i][0],"text":rate_fetch[i][1]})
            i+=1

    connection.commit()
    overflow = "0"
    return render_template("goods_info.html",is_stop_supply=is_stop_supply,rates=rates,can_star_rate=can_star_rate,can_report=can_report,overflow=overflow,IS_LOGIN=IS_LOGIN,USER_NAME=USER_NAME,USER_AVATAR_SRC=USER_AVATAR_SRC,goods=goods,can_rate=can_rate,seller=seller,USER_ID=USER_ID)

#修改商品提交
@app.route("/set_goods", methods=['POST','GET'])
def set_goods():
    goods_id = str(request.args.get('gid'))
    print(goods_id)
    global IS_LOGIN
    global USER_AVATAR_SRC
    global USER_NAME
    global USER_ID
    global SRC
    global is_stop_supply
    cursor = connection.cursor()
    num_error = "0"
    ###########################

    #商品資訊
    member_id = USER_ID
    #booknum[0][0] int
    #booknum[0] tuple
    #booknum list
    #取得商品種類
    #goods_type = str(request.args.get('gtype'))
    #print(request.form)
    #print(goods_type)
    goods_quantity = int(request.values['goods_quantity'])
    if goods_quantity>0:
        goods_price = request.values['goods_price']    
        sql=f"SELECT `goods_rate` FROM `goods` WHERE `goods_id` = {goods_id};"
        cursor.execute(sql)
        goods_rate_supply = cursor.fetchall()
        goods_rate = ""
        if goods_rate_supply:
            goods_rate = goods_rate_supply[0][0]
        #取得商品新舊程度
        new_or_old = request.values['new_or_old']
        if not new_or_old:
            new_or_old = "未知"  
        #取得商品是否接受競標
        can_bid = request.values['can_bid']
        #儲存商品資訊
        print(goods_id)
        sql = f"UPDATE `goods` SET `goods_price`= {goods_price} ,`goods_quantity` = {goods_quantity},`can_bid` = {can_bid} WHERE `goods_id` = {goods_id};"
        cursor.execute(sql)
        #更新商品新舊
        if goods_id[0]=="1":
            sql = f"UPDATE `goods_book_category` SET `category`= '{new_or_old}' WHERE `goods_book_id` = {goods_id} AND `category` IN ('全新','9成新','5成新','3成新','未知');"
            cursor.execute(sql)
        else:
            sql = f"UPDATE `goods_CD` SET `category`= '{new_or_old}' WHERE `goods_CD_id` = {goods_id} AND `category` IN ('全新','9成新','5成新','3成新','未知');"
            cursor.execute(sql)
    else:
        num_error="1"
    ###########################
    #print(request.form)
    #從網址列拿資料
    #更新商品綜合評價
    sql=f"SELECT `star_rate` FROM `buy` WHERE `star_rate` <> -1 AND goods_id = {goods_id};"
    cursor.execute(sql)
    goods_rate_up = cursor.fetchall()
    avg = []
    if goods_rate_up:
        i=0
        while i<len(goods_rate_up):
            avg.append(int(goods_rate_up[i][0]))
            i+=1
        goods_avg = statistics.mean(avg)
        goods_avg = round(goods_avg,1)
        sql=f"UPDATE `goods` SET `goods_rate` = {goods_avg} WHERE `goods_id` = {goods_id};"
        cursor.execute(sql)
    #取得商品資訊
    sql=f"SELECT * FROM `goods` WHERE `goods_id` = {goods_id};"
    cursor.execute(sql)
    goods_info = cursor.fetchall()
    seller_name = ""
    seller_picture = ""
    seller = {}
    if goods_info:
        seller_id = goods_info[0][0]
        if seller_id:
            sql=f"SELECT `name`,`picture` FROM `member` WHERE `member_id` = '{seller_id}';"
            cursor.execute(sql)
            seller_info = cursor.fetchall()
            if seller_info:
                seller_name = seller_info[0][0]
                seller_picture = seller_info[0][1]
                if seller_picture:
                    seller_picture = SRC + "/" +seller_id + "/" + seller_picture
                else:
                    seller_picture = ""
                if seller_name:
                    #建立賣家資訊字典
                    seller = {"seller_id":seller_id,"seller_name":seller_name,"seller_avatar":seller_picture}
        goods_name = goods_info[0][2]
        goods_picture = goods_info[0][3]
        if goods_picture:
            goods_picture = SRC + "/" +seller_id + "/" + goods_picture
        else:
            goods_picture = ""
        goods_describe = goods_info[0][4]
        goods_author = goods_info[0][5]
        goods_price = goods_info[0][6]
        goods_quantity = goods_info[0][7]
        goods_dates = goods_info[0][8]
        goods_rate = goods_info[0][9]
    #根據交易紀錄判斷是否可評價&檢舉
    can_star_rate = ""
    can_report = ""
    can_rate = ""
    #是否有買過
    sql=f"SELECT COUNT(*) FROM `buy` WHERE `member_id` = '{USER_ID}' AND `goods_id` = {goods_id};"
    cursor.execute(sql)
    bye_ed = cursor.fetchall()
    if bye_ed:
        if bye_ed[0][0] > 0:
            #是否有檢舉過
            if seller_id:
                sql=f"SELECT COUNT(*) FROM `report` WHERE `member_id` = '{USER_ID}' AND `seller_id` = '{seller_id}';"
                cursor.execute(sql)
                reported = cursor.fetchall()
                if reported or reported[0][0] == 0:
                    if reported[0][0] == 0:#如果沒檢舉過就可以檢舉
                        can_report = "1"

            #是否有評價過(按鈕)
            sql=f"SELECT COUNT(*) FROM `buy` WHERE `member_id` = '{USER_ID}' AND `goods_id` = {goods_id} AND `star_rate` <> -1;"
            cursor.execute(sql)
            srate = cursor.fetchall()
            if srate or srate[0][0] == 0:
                if srate[0][0] == 0:#如果沒評價過就可以評價
                    can_star_rate = "1"
            
            #是否有評價過(文字)
            sql=f"SELECT COUNT(*) FROM `buy` WHERE `member_id` = '{USER_ID}' AND `goods_id` = {goods_id} AND `rate` IS NOT NULL;"
            cursor.execute(sql)
            trate = cursor.fetchall()
            if trate or trate[0][0] == 0:
                if trate[0][0] == 0:#如果沒評價過就可以評價
                    can_rate = "1"

    #建立商品資訊字典
    goods = {}
    categories = []
    last_category = ""
    if goods_id[0]=="1":#書
        sql=f"SELECT `goods_book_publisher` FROM `goods_book` WHERE `goods_book_id` = {goods_id};"
        cursor.execute(sql)
        goods_book_publisher = cursor.fetchall()
        if not goods_book_publisher:
            goods_book_publisher = ""
        #取得分類
        sql=f"SELECT `category` FROM `goods_book_category` WHERE `goods_book_id` = {goods_id};"
        cursor.execute(sql)
        categories_fetch = cursor.fetchall()
        if categories_fetch:
            i=0
            while i<len(categories_fetch):
                categories.append(categories_fetch[i][0])
                i+=1
            last_category = categories[len(categories)-1]
        goods = {"goods_id":goods_id,"goods_name":goods_name,"goods_picture":goods_picture,"goods_describe":goods_describe,"goods_author":goods_author,"goods_price":goods_price,"goods_quantity":goods_quantity,"goods_dates":goods_dates,"goods_rate":goods_rate,"goods_book_publisher":goods_book_publisher[0][0],"categories":categories,"last_category":last_category}
                  
    elif goods_id[0]=="2":#CD
        #取得分類
        sql=f"SELECT `category` FROM `goods_CD` WHERE `goods_CD_id` = {goods_id};"
        cursor.execute(sql)
        categories_fetch = cursor.fetchall()
        if categories_fetch:
            i=0
            while i<len(categories_fetch):
                categories.append(categories_fetch[i][0])
                i+=1
            last_category = categories[len(categories)-1]
        goods = {"goods_id":goods_id,"goods_name":goods_name,"goods_picture":goods_picture,"goods_describe":goods_describe,"goods_author":goods_author,"goods_price":goods_price,"goods_quantity":goods_quantity,"goods_dates":goods_dates,"goods_rate":goods_rate,"categories":categories,"last_category":last_category}
    #取得評價文字
    rates = {}
    sql = f"SELECT `member_id`,`rate` FROM `buy` WHERE `rate` IS NOT NULL AND `goods_id` = {goods_id};"
    cursor.execute(sql)
    rate_fetch = cursor.fetchall()
    if rate_fetch:
        i=0
        while i<len(rate_fetch):
            rates.append({"member_id":rate_fetch[i][0],"text":rate_fetch[i][1]})
            i+=1

    connection.commit()
    overflow = "0"
    return render_template("goods_info.html",num_error=num_error,is_stop_supply=is_stop_supply,rates=rates,can_star_rate=can_star_rate,can_report=can_report,overflow=overflow,IS_LOGIN=IS_LOGIN,USER_NAME=USER_NAME,USER_AVATAR_SRC=USER_AVATAR_SRC,goods=goods,can_rate=can_rate,seller=seller,USER_ID=USER_ID)

#刪除購物車
@app.route("/delete_shopping_cart_goods", methods=['POST','GET'])
def delete_shopping_cart_goods():

    global IS_LOGIN
    global USER_AVATAR_SRC
    global USER_NAME
    global USER_ID
    cursor = connection.cursor()
    #刪除購物車
    goods_id = str(request.args.get('gid'))
    sql=f"DELETE FROM `shopping_cart` WHERE `goods_id` = {goods_id} AND `member_id` = '{USER_ID}';"
    cursor.execute(sql)

    #取得會員購物車資料
    sql=f"SELECT * FROM `shopping_cart` WHERE `member_id` = '{USER_ID}';"
    cursor.execute(sql)
    shopping_datas = cursor.fetchall()
    goods_id = ""
    goods = []
    no_goods = "1"
    all_sum_price = 0
    if shopping_datas:
        i=0
        while i<len(shopping_datas):
            goods_id = str(shopping_datas[i][1])
            sql = f"SELECT `member_id` FROM `goods` WHERE `goods_id` = {goods_id};"
            cursor.execute(sql)
            member_id_fetch = cursor.fetchall()
            member_id = ""
            if member_id_fetch:
                member_id = member_id_fetch[0][0]
            goods_name = shopping_datas[i][2]
            goods_sum_price = shopping_datas[i][3]
            all_sum_price += goods_sum_price
            goods_picture = shopping_datas[i][4]
            if goods_picture:
                goods_picture = SRC + "/" + member_id + "/" + goods_picture
            else:
                goods_picture = ""
            goods_amount = shopping_datas[i][5]
            goods_price = int(goods_sum_price / goods_amount)
            #取得物品剩餘數量
            sql = f"SELECT `goods_quantity` FROM `goods` WHERE `goods_id` = {goods_id};"
            cursor.execute(sql)
            goods_quantity_fetch = cursor.fetchall()
            goods_quantity = ""
            if goods_quantity_fetch:
                goods_quantity = str(goods_quantity_fetch[0][0])
            goods.append({"goods_id":goods_id,"goods_name":goods_name,"goods_sum_price":goods_sum_price,"goods_price":goods_price,"goods_picture":goods_picture,"goods_amount":goods_amount,"goods_quantity":goods_quantity})
            i+=1
    if goods:
        no_goods = "0"
    connection.commit()
    return render_template("shopping_cart.html",all_sum_price=all_sum_price,IS_LOGIN=IS_LOGIN,USER_NAME=USER_NAME,USER_AVATAR_SRC=USER_AVATAR_SRC,goods=goods,no_goods=no_goods)

#修改購物車
@app.route("/set_amount", methods=['POST','GET'])
def set_amount():

    global IS_LOGIN
    global USER_AVATAR_SRC
    global USER_NAME
    global USER_ID
    cursor = connection.cursor()
    #修改購物車
    overflow = "0"
    goods_id = str(request.args.get('gid'))
    new_goods_amount = int(request.values['goods_amount'])

    if new_goods_amount == 0:#數量為0則刪除
        sql=f"DELETE FROM `shopping_cart` WHERE `goods_id` = {goods_id} AND `member_id` = '{USER_ID}';"
        cursor.execute(sql)
    else:
        sql = f"SELECT `goods_quantity` FROM `goods` WHERE `goods_id` = {goods_id};"
        cursor.execute(sql)
        quantity_flow_fetch = cursor.fetchall()
        if quantity_flow_fetch:
            max_amount = quantity_flow_fetch[0][0]
            if not max_amount<new_goods_amount:#沒有溢位
                sql=f"SELECT * FROM `shopping_cart` WHERE `member_id` = '{USER_ID}' AND `goods_id` = {goods_id};"
                cursor.execute(sql)
                change_fetch = cursor.fetchall()
                if change_fetch:#03總價,05數量
                    old_sum_price = int(change_fetch[0][3])
                    old_goods_amount = int(change_fetch[0][5])
                    single_price = old_sum_price / old_goods_amount
                    new_sum_price = new_goods_amount * single_price
                    sql=f"UPDATE `shopping_cart` SET `goods_price` = {new_sum_price},`goods_amount` = {new_goods_amount} WHERE `member_id` = '{USER_ID}' AND `goods_id` = {goods_id};"
                    cursor.execute(sql)
            else:
                overflow = "1"
    
    #取得會員購物車資料
    sql=f"SELECT * FROM `shopping_cart` WHERE `member_id` = '{USER_ID}';"
    cursor.execute(sql)
    shopping_datas = cursor.fetchall()
    goods_id = ""
    goods = []
    no_goods = "1"
    all_sum_price = 0
    if shopping_datas:
        i=0
        while i<len(shopping_datas):
            goods_id = str(shopping_datas[i][1])
            sql = f"SELECT `member_id` FROM `goods` WHERE `goods_id` = {goods_id};"
            cursor.execute(sql)
            member_id_fetch = cursor.fetchall()
            member_id = ""
            if member_id_fetch:
                member_id = member_id_fetch[0][0]
            goods_name = shopping_datas[i][2]
            goods_sum_price = shopping_datas[i][3]
            all_sum_price += goods_sum_price
            goods_picture = shopping_datas[i][4]
            if goods_picture:
                goods_picture = SRC + "/" + member_id + "/" + goods_picture
            else:
                goods_picture = ""
            goods_amount = shopping_datas[i][5]
            goods_price = int(goods_sum_price / goods_amount)
            #取得物品剩餘數量
            sql = f"SELECT `goods_quantity` FROM `goods` WHERE `goods_id` = {goods_id};"
            cursor.execute(sql)
            goods_quantity_fetch = cursor.fetchall()
            goods_quantity = ""
            if goods_quantity_fetch:
                goods_quantity = str(goods_quantity_fetch[0][0])

            goods.append({"goods_id":goods_id,"goods_name":goods_name,"goods_sum_price":goods_sum_price,"goods_price":goods_price,"goods_picture":goods_picture,"goods_amount":goods_amount,"goods_quantity":goods_quantity})
            i+=1
    if goods:
        no_goods = "0"
    connection.commit()
    return render_template("shopping_cart.html",all_sum_price=all_sum_price,overflow=overflow,IS_LOGIN=IS_LOGIN,USER_NAME=USER_NAME,USER_AVATAR_SRC=USER_AVATAR_SRC,goods=goods,no_goods=no_goods)

#結帳
@app.route("/pay", methods=['POST','GET'])
def pay():
    global IS_LOGIN
    global USER_AVATAR_SRC
    global USER_NAME
    global USER_ID
    global SRC
    global USER_CARD
    cursor = connection.cursor()
    pay_type = request.values['COD_or_Ccard']
    no_credit_card = "0"
    if pay_type=="Ccard":
        if USER_CARD == "":
            no_credit_card="1"
    if no_credit_card == "1":
        #無法使用信用卡,進入帳號頁面
        #取得已結束交易紀錄
        transaction = []        
        sql=f"SELECT * FROM `transaction_record` WHERE `member_id` = '{USER_ID}' AND `transaction_status` = 3;"
        cursor.execute(sql)
        transaction_record_fetch = cursor.fetchall()
        if transaction_record_fetch:
            i=0
            #取得每筆交易的所有商品
            while i<len(transaction_record_fetch):
                transaction_id = transaction_record_fetch[i][1]
                buy_date = transaction_record_fetch[i][2]
                finish_date = transaction_record_fetch[i][4]
                sql=f"SELECT * FROM `transaction_record_goods` WHERE `transaction_id` = {transaction_id};"
                cursor.execute(sql)
                goods_fetch = cursor.fetchall()
                goods = []
                if goods_fetch:
                    
                    j=0
                    goods_sum_price = 0
                    while j<len(goods_fetch):
                        goods_sum_price += goods_fetch[j][3]
                        j+=1
                    j=0
                    
                    while j<len(goods_fetch):
                        print(goods_fetch[j])
                        goods_id = goods_fetch[j][1]
                        goods_name = goods_fetch[j][2]
                        goods_amount = goods_fetch[j][4]
                        goods.append({"goods_id":goods_id,"goods_name":goods_name,"goods_amount":goods_amount})
                        j+=1
                transaction.append({"transaction_id":transaction_id,"goods":goods,"goods_sum_price":goods_sum_price,"buy_date":buy_date,"finish_date":finish_date,"last_goods_id":goods_fetch[len(goods_fetch)-1][1]})
                i+=1
                
        user = {"id":USER_ID,"password":USER_PASSWORD,"name":USER_NAME,"phone_number":USER_PHONENUMBER,"bank_account":USER_BANKACC,"credit_card":USER_CARD,"picture":USER_AVATAR_SRC}
        return render_template("account.html",no_credit_card=no_credit_card,transaction=transaction,IS_LOGIN=IS_LOGIN,user=user,USER_NAME=USER_NAME,USER_AVATAR_SRC=USER_AVATAR_SRC)

    bid = str(request.args.get('bid'))

    #產生交易紀錄id並紀錄除了領貨時間的所有資訊
    #插入transaction_record
    sql=f"SELECT COUNT(*) FROM `transaction_record`;"
    cursor.execute(sql)
    transaction_id_fetch = cursor.fetchall()
    transaction_id = ""
    need_sub = 0
    if transaction_id_fetch or transaction_id_fetch[0][0]==0:
        transaction_id = str(int(transaction_id_fetch[0][0]) + 10000)
        sql=f"SELECT COUNT(*) FROM `transaction_record` WHERE `transaction_id` = {transaction_id};"
        cursor.execute(sql)
        repeat_id_fetch = cursor.fetchall()
        if repeat_id_fetch and repeat_id_fetch[0][0]>0:
            transaction_id = 10000
            need_sub = 1
        while repeat_id_fetch and repeat_id_fetch[0][0]>0:
            sql=f"SELECT COUNT(*) FROM `transaction_record` WHERE `transaction_id` = {transaction_id};"
            cursor.execute(sql)
            repeat_id_fetch = cursor.fetchall()
            transaction_id += 1
        if need_sub == 1:
            transaction_id -= 1
    localtime = datetime.datetime.now()
    buy_date = localtime.strftime("%Y-%m-%d %H:%M:%S")
    arrival_date = random_arrival_date(localtime)
    if bid != "0":
        sql=f"SELECT `max_price` FROM `bid` WHERE `bid_id` = {bid};"
        cursor.execute(sql)
        max_price_fetch = cursor.fetchall()
        if max_price_fetch:
            sql=f"insert into `transaction_record` values('{USER_ID}',{transaction_id},'{buy_date}','{arrival_date}',NULL,{max_price_fetch[0][0]},1);"
            cursor.execute(sql)
            

    else:
        sql=f"SELECT SUM(`goods_price`) FROM `shopping_cart` WHERE `member_id` = '{USER_ID}';"
        cursor.execute(sql)
        total_price_fetch = cursor.fetchall()
        total_price = ""
        if total_price_fetch:
            total_price = str(total_price_fetch[0][0])
        sql=f"insert into `transaction_record` values('{USER_ID}',{transaction_id},'{buy_date}','{arrival_date}',NULL,{total_price},0);"
        cursor.execute(sql)
    #插入transaction_record_goods
    
    if bid != "0":
        sql=f"SELECT `bid_goods_id`,`max_price` FROM `bid` WHERE `bid_id` = {bid};"
        cursor.execute(sql)
        goods_id_fetch = cursor.fetchall()
        if goods_id_fetch:
            sql=f"SELECT `goods_name` FROM `goods` WHERE `goods_id` = {goods_id_fetch[0][0]};"
            cursor.execute(sql)
            goods_name_fetch = cursor.fetchall()
            sql=f"insert into `transaction_record_goods` values({transaction_id},{goods_id_fetch[0][0]},'{goods_name_fetch[0][0]}',{goods_id_fetch[0][1]},1,1);"
            cursor.execute(sql)
            sql =f"UPDATE `goods` SET `supply_status` = 1 WHERE `goods_id` = {goods_id_fetch[0][0]};"
            cursor.execute(sql)
            sql =f"insert into `buy` values('{USER_ID}',{goods_id_fetch[0][0]},{transaction_id},-1,NULL);"
            cursor.execute(sql)
    else:
        #from會員購物車資料
        sql=f"SELECT * FROM `shopping_cart` WHERE `member_id` = '{USER_ID}';"
        cursor.execute(sql)
        shopping_cart_fetch = cursor.fetchall()
        shopping_cart_goods_id =""
        shopping_cart_goods_name =""
        shopping_cart_sum_price =""
        shopping_cart_amount =""
        if shopping_cart_fetch:
            i=0
            while i<len(shopping_cart_fetch):
                shopping_cart_goods_id = shopping_cart_fetch[i][1]
                shopping_cart_goods_name= shopping_cart_fetch[i][2]
                shopping_cart_sum_price= shopping_cart_fetch[i][3]
                shopping_cart_amount= shopping_cart_fetch[i][5]
                #更新商品數量
                sql=f"UPDATE `goods` SET `goods_quantity` = `goods_quantity` - {shopping_cart_amount} WHERE `goods_id` = {shopping_cart_goods_id};"
                cursor.execute(sql)
                sql=f"insert into `transaction_record_goods` values({transaction_id},{shopping_cart_goods_id},'{shopping_cart_goods_name}',{shopping_cart_sum_price},{shopping_cart_amount},0);"
                cursor.execute(sql)
                #插入buy
                sql =f"insert into `buy` values('{USER_ID}',{shopping_cart_goods_id},{transaction_id},-1,NULL);"
                cursor.execute(sql)
                i+=1

    if bid != "0":#刪除競標
        sql=f"DELETE FROM `bid` WHERE `bid_id` = {bid};"
        cursor.execute(sql)
    else:###刪除購物車
        sql=f"DELETE FROM `shopping_cart` WHERE `member_id` = '{USER_ID}';"
        cursor.execute(sql)
    ###############################取得資料庫所有商品資料
    #更新商品綜合評價
    sql=f"SELECT `goods_id` FROM `goods`;"
    cursor.execute(sql)
    goods_id_fetch = cursor.fetchall()
    if goods_id_fetch:
        k=0
        while k<len(goods_id_fetch):
            sql=f"SELECT `star_rate` FROM `buy` WHERE `star_rate` <> -1 AND goods_id = {goods_id_fetch[k][0]};"
            cursor.execute(sql)
            goods_rate_up = cursor.fetchall()
            avg = []
            if goods_rate_up:
                j=0
                while j<len(goods_rate_up):
                    avg.append(int(goods_rate_up[j][0]))
                    j+=1
                goods_avg = statistics.mean(avg)
                goods_avg = round(goods_avg,1)
                sql=f"UPDATE `goods` SET `goods_rate` = {goods_avg} WHERE `goods_id` = {goods_id_fetch[k][0]};"
                cursor.execute(sql)
            k+=1
    #
    sql="SELECT * FROM `goods` WHERE `goods_quantity` > 0 AND `supply_status` = 1;"
    cursor.execute(sql)
    goods_datas = cursor.fetchall()
    if goods_datas:
        i=0
        goods = []
        while i<len(goods_datas):
            goodsub = []
            j=0
            while j<4 and i<len(goods_datas):
                member_id = goods_datas[i][0]
                goods_id = str(goods_datas[i][1])
                goods_name = goods_datas[i][2]
                goods_picture = goods_datas[i][3]
                if goods_picture:
                    goods_picture = SRC + "/" +member_id + "/" + goods_picture
                else:
                    goods_picture = ""
                goods_author = goods_datas[i][5]
                goods_price = goods_datas[i][6]
                goods_rate = goods_datas[i][9]
                #商品分類
                if str(goods_id[0])=="1":#書
                    sql=f"SELECT `category` FROM `goods_book_category`,`goods` WHERE `goods_book_id` = `goods_id` AND `goods_id` = {goods_id};"
                    cursor.execute(sql)
                    categories = cursor.fetchall()
                    goodsub.append({"member_id":member_id,"goods_id":goods_id,"goods_name":goods_name,"goods_picture":goods_picture,"goods_author":goods_author,"goods_price":goods_price,"goods_rate":goods_rate,"categories":categories})
                elif str(goods_id[0])=="2":#CD 
                    sql=f"SELECT `category` FROM `goods_CD`,`goods` WHERE `goods_CD_id` = `goods_id` AND `goods_id` = {goods_id};"
                    cursor.execute(sql)
                    categories = cursor.fetchall()
                    goodsub.append({"member_id":member_id,"goods_id":goods_id,"goods_name":goods_name,"goods_picture":goods_picture,"goods_author":goods_author,"goods_price":goods_price,"goods_rate":goods_rate,"categories":categories})
                i+=1
                j+=1
            goods.append(goodsub)
            #取得評價前三高的商品圖片跟id
            slideshow = []
            sql=f"SELECT `goods_id`,`goods_picture`,`member_id` FROM `goods` WHERE `goods_quantity` > 0 AND `supply_status` = 1 ORDER BY `goods_rate` DESC LIMIT 3;"
            cursor.execute(sql)
            top3_fetch = cursor.fetchall()
            if top3_fetch:
                k=0
                while k<len(top3_fetch):
                    top3_id = str(top3_fetch[k][0])
                    top3_picture = top3_fetch[k][1]
                    if top3_picture:
                        top3_picture = SRC + "/" + str(top3_fetch[k][2]) + "/" + top3_picture
                    else:
                        top3_picture = ""
                    k+=1
                    slideshow.append({"goods_id":top3_id,"goods_picture":top3_picture})
    
    order_success = "1"
    connection.commit()
    return render_template("home.html",slideshow=slideshow,order_success=order_success,IS_LOGIN=IS_LOGIN,USER_NAME=USER_NAME,USER_AVATAR_SRC=USER_AVATAR_SRC,goods=goods)

#賣家寄出商品
@app.route("/send_goods", methods=['POST','GET'])
def send_goods():
    global IS_LOGIN
    global USER_AVATAR_SRC
    global USER_NAME
    global USER_CARD
    global USER_ID
    global SRC
    cursor = connection.cursor()
    #######寄出商品,將所有該賣家的商品狀況設為1(已打包)
    sql=f"UPDATE `transaction_record_goods` SET `goods_status` = 1 WHERE `goods_status` = 0 AND `transaction_record_goods`.`goods_id` IN (SELECT `goods`.`goods_id` FROM `goods` WHERE `member_id` = '{USER_ID}');"
    cursor.execute(sql)
    print("寄出")
    #判斷有更新到的交易是否已寄出所有商品
    sql =f"SELECT `transaction_record_goods`.`transaction_id` FROM `transaction_record_goods`,`transaction_record` WHERE `transaction_record_goods`.`goods_id` IN (SELECT `goods`.`goods_id` FROM `goods` WHERE `member_id` = '{USER_ID}') AND `transaction_record`.`transaction_status` = 0;"
    cursor.execute(sql)
    transaction_id_fetch = cursor.fetchall()
    print(transaction_id_fetch)
    if transaction_id_fetch:
        i=0
        while i<len(transaction_id_fetch):
            sql =f"SELECT COUNT(*) FROM `transaction_record_goods` WHERE `transaction_id` = {transaction_id_fetch[i][0]} AND `goods_status` = 1;"
            cursor.execute(sql)
            pack_num = cursor.fetchall()
            sql=f"SELECT COUNT(*) FROM `transaction_record_goods` WHERE `transaction_id` = {transaction_id_fetch[i][0]};"
            cursor.execute(sql)
            goods_num = cursor.fetchall()
            if pack_num and goods_num and (pack_num[0][0] == goods_num[0][0]):#如果沒有未寄出商品則出貨
                print("p,g",pack_num[0][0],goods_num[0][0])
                sql=f"UPDATE `transaction_record` SET `transaction_status` = 1 WHERE `transaction_id` = {transaction_id_fetch[i][0]} AND `transaction_status` = 0;"
                cursor.execute(sql)
            i+=1

    #sql=f"SELECT COUNT(*) FROM `transaction_record_goods` WHERE `goods_status` = 0;"
    ########讀取商品資料
    if IS_LOGIN == "1":
        need_send = "0"
        id = request.args.get('id')
        seller = {}
        member_id = ""
        if id:#他人賣場
            member_id = id
            sql=f"SELECT `name`,`picture` FROM `member` WHERE `member_id` = '{member_id}';"
            cursor.execute(sql)
            seller_info = cursor.fetchall()
            if seller_info:
                seller_name = seller_info[0][0]
                seller_picture = seller_info[0][1]
                if seller_picture:
                    seller_picture = SRC + "/" + member_id + "/" + seller_picture
                else:
                    seller_picture = ""
                seller = {"seller_id":member_id,"seller_name":seller_name,"seller_picture":seller_picture}
        else:#本人
            member_id = USER_ID
            #判斷是否需出貨
            sql = f"SELECT `goods_status` FROM `transaction_record_goods` WHERE `transaction_record_goods`.`goods_id` IN (SELECT `goods`.`goods_id` FROM `goods` WHERE `goods`.`member_id` = '{member_id}');"
            cursor.execute(sql)
            goods_status_fetch = cursor.fetchall()
            if goods_status_fetch:
                i=0
                while i<len(goods_status_fetch):
                    goods_status = str(goods_status_fetch[i][0])
                    if goods_status == "0":
                        need_send = "1"
                        break
                    i+=1
            seller = {"seller_id":member_id,"seller_name":USER_NAME,"seller_picture":USER_AVATAR_SRC}
        #讀取商品資料
        sql=f"SELECT * FROM `goods` WHERE `member_id` = '{member_id}';"
        cursor.execute(sql)
        goods_datas = cursor.fetchall()
        goods = []

        if goods_datas:
            i=0
            while i<len(goods_datas):
                goodsub = []
                j=0
                while j<4 and i<len(goods_datas):
                    goods_id = str(goods_datas[i][1])
                    goods_name = goods_datas[i][2]
                    goods_picture = goods_datas[i][3]
                    if goods_picture:
                        goods_picture = SRC + "/" +member_id + "/" + goods_picture
                    else:
                        goods_picture = ""
                    goods_author = goods_datas[i][5]
                    goods_price = goods_datas[i][6]
                    goods_rate = goods_datas[i][9]
                    #商品分類
                    if str(goods_id[0])=="1":#書
                        sql=f"SELECT `category` FROM `goods_book_category`,`goods` WHERE `goods_book_id` = `goods_id` AND `goods_id` = {goods_id};"
                        cursor.execute(sql)
                        categories = cursor.fetchall()
                        goodsub.append({"goods_id":goods_id,"goods_name":goods_name,"goods_picture":goods_picture,"goods_author":goods_author,"goods_price":goods_price,"goods_rate":goods_rate,"categories":categories})
                    elif str(goods_id[0])=="2":#CD 
                        sql=f"SELECT `category` FROM `goods_CD`,`goods` WHERE `goods_CD_id` = `goods_id` AND `goods_id` = {goods_id};"
                        cursor.execute(sql)
                        categories = cursor.fetchall()
                        goodsub.append({"goods_id":goods_id,"goods_name":goods_name,"goods_picture":goods_picture,"goods_author":goods_author,"goods_price":goods_price,"goods_rate":goods_rate,"categories":categories})
                    i+=1
                    j+=1
                #print(goodsub)
                goods.append(goodsub)
        connection.commit()      
        return render_template("seller.html",need_send=need_send,seller=seller,IS_LOGIN=IS_LOGIN,USER_CARD=USER_CARD,USER_NAME=USER_NAME,USER_AVATAR_SRC=USER_AVATAR_SRC,goods=goods,USER_ID=USER_ID)
    else:
        return render_template("seller.html",IS_LOGIN=IS_LOGIN)

chat_id_list=[]
chat_id_info = []

@app.route("/chat.html", methods=['POST','GET'])
def chat():
    global IS_LOGIN
    global USER_AVATAR_SRC
    global USER_NAME
    global USER_CARD
    global USER_ID
    global SRC
    global chat_id_list
    global chat_id_info
    cursor = connection.cursor()
    need_sub = 0
    can_chat = "0"
    if IS_LOGIN=="1":
        consult_id = "0"
        cid = str(request.args.get('cid'))
        need_sub = 0
        type = str(request.args.get('type'))
        if type=="0":#送出訊息
            sql=f"SELECT COUNT(*) FROM `consult`;"
            cursor.execute(sql)
            consult_id_num = cursor.fetchall()
            if consult_id_num or consult_id_num[0][0] == 0:
                consult_id = str(int(consult_id_num[0][0])+100000)
                sql=f"SELECT COUNT(*) FROM `consult` WHERE `consult_id` = {consult_id};"
                cursor.execute(sql)
                repeat_id_fetch = cursor.fetchall()
                if repeat_id_fetch and repeat_id_fetch[0][0]>0:
                    consult_id = 100000
                    need_sub = 1
                while repeat_id_fetch and repeat_id_fetch[0][0]>0:
                    sql=f"SELECT COUNT(*) FROM `consult` WHERE `consult_id` = {consult_id};"
                    cursor.execute(sql)
                    repeat_id_fetch = cursor.fetchall()
                    consult_id += 1
                if need_sub == 1:
                    consult_id -= 1
                
            text=str(request.values['chat_text'])
            localtime = time.localtime()
            chat_time = time.strftime("%Y-%m-%d %H:%M:%S", localtime)
            sql=f"insert into `consult` values({consult_id},'{USER_ID}','{cid}','{text}','{chat_time}');"
            cursor.execute(sql)

        if type=="1":#重新取得USER所有聯絡人id
            chat_id_list=[]
            if cid != "0":
                chat_id_list.append(cid)
            sql=f"SELECT `receive_id`,`sender_id` FROM `consult` WHERE (`receive_id` = '{USER_ID}' OR `sender_id` = '{USER_ID}') AND (`receive_id` <> '{MANAGER_ID}' AND `sender_id` <> '{MANAGER_ID}');"
            cursor.execute(sql)
            chat_id_fetch = cursor.fetchall()
            if chat_id_fetch:
                i=0
                while i<len(chat_id_fetch):
                    j=0
                    is_repeat = 0
                    print("chat_id_fetch",chat_id_fetch[i][1],chat_id_fetch[i][0])
                    if chat_id_fetch[i][0] == USER_ID:
                        while j<len(chat_id_list):
                            if chat_id_list[j] == chat_id_fetch[i][1]:
                                is_repeat = 1
                                break
                            j+=1
                        if is_repeat == 0:
                            chat_id_list.append(str(chat_id_fetch[i][1]))
                    else:
                        while j<len(chat_id_list):
                            if chat_id_list[j] == chat_id_fetch[i][0]:
                                is_repeat = 1
                                break
                            j+=1
                        if is_repeat == 0:
                            chat_id_list.append(str(chat_id_fetch[i][0]))
                    i+=1
            #取得所有聯絡人暱稱及頭像
            chat_id_info = []
            i=0
            name_ = ""
            picture_ = ""

            while i<len(chat_id_list):
                print("chat_id_list",chat_id_list[i])
                sql=f"SELECT `name`,`picture` FROM `member` WHERE `member_id` = '{chat_id_list[i]}';"
                cursor.execute(sql)
                name_and_picture_fetch = cursor.fetchall()
                if name_and_picture_fetch:
                    name_ = name_and_picture_fetch[0][0]
                    picture_ = name_and_picture_fetch[0][1]
                    if picture_:
                        picture_ = SRC + "/" + chat_id_list[i] + "/" + picture_
                    else:
                        picture_ = ""
                chat_id_info.append({"id":chat_id_list[i],"name":name_,"picture":picture_})
                i+=1
        if chat_id_info:
            can_chat = "1"



        #取得對方所有訊息
        all_chat_text = []
        if can_chat == "1":
            if cid == "0":
                cid = chat_id_list[0]
            sql=f"SELECT * FROM `consult` WHERE `receive_id` = '{cid}' AND `sender_id` = '{USER_ID}';"
            cursor.execute(sql)
            right_text_fetch = cursor.fetchall()
            sql=f"SELECT * FROM `consult` WHERE `receive_id` = '{USER_ID}' AND `sender_id` = '{cid}';"
            cursor.execute(sql)
            left_text_fetch = cursor.fetchall()
            i=0
            j=0
            sql = f"SELECT `name` FROM `member` WHERE `member_id` = '{cid}';"
            cursor.execute(sql)
            cname_fetch = cursor.fetchall()
            if cname_fetch:
                cname = cname_fetch[0][0]
            while i<len(right_text_fetch) and j<len(left_text_fetch):
                if right_text_fetch[i][4]<left_text_fetch[j][4]:            
                    all_chat_text.append({"text":right_text_fetch[i][3],"side":"right","name":USER_NAME})
                    i+=1
                else:
                    all_chat_text.append({"text":left_text_fetch[j][3],"side":"left","name":cname})
                    j+=1
            while i<len(right_text_fetch):
                all_chat_text.append({"text":right_text_fetch[i][3],"side":"right","name":USER_NAME})
                i+=1
            while j<len(left_text_fetch):
                all_chat_text.append({"text":left_text_fetch[j][3],"side":"left","name":cname})
                j+=1
        
        
        
        connection.commit()
        return render_template("chat.html",can_chat=can_chat,cid=cid,chat_id_info=chat_id_info,all_chat_text=all_chat_text,IS_LOGIN=IS_LOGIN,USER_AVATAR_SRC=USER_AVATAR_SRC,USER_NAME=USER_NAME,USER_ID=USER_ID)
    else:
        return render_template("chat.html",can_chat=can_chat,IS_LOGIN=IS_LOGIN)


@app.route("/manager_chat.html", methods=['POST','GET'])
def manager_chat():
    global IS_LOGIN
    global USER_AVATAR_SRC
    global USER_NAME
    global USER_CARD
    global USER_ID
    global SRC
    global MANAGER_ID
    global chat_id_list
    global chat_id_info
    cursor = connection.cursor()
    need_sub = 0
    if IS_LOGIN=="0":
        consult_id = "0"
        cid = str(request.args.get('cid'))
        type = str(request.args.get('type'))
        if type=="0":#送出訊息
            sql=f"SELECT COUNT(*) FROM `consult`;"
            cursor.execute(sql)
            consult_id_num = cursor.fetchall()
            if consult_id_num or consult_id_num[0][0] == 0:
                consult_id = str(int(consult_id_num[0][0])+100000)
                sql=f"SELECT COUNT(*) FROM `consult` WHERE `consult_id` = {consult_id};"
                cursor.execute(sql)
                repeat_id_fetch = cursor.fetchall()
                if repeat_id_fetch and repeat_id_fetch[0][0]>0:
                    consult_id = 100000
                    need_sub = 1
                while repeat_id_fetch and repeat_id_fetch[0][0]>0:
                    sql=f"SELECT COUNT(*) FROM `consult` WHERE `consult_id` = {consult_id};"
                    cursor.execute(sql)
                    repeat_id_fetch = cursor.fetchall()
                    consult_id += 1
                if need_sub == 1:
                    consult_id -= 1

            text=str(request.values['chat_text'])
            localtime = time.localtime()
            chat_time = time.strftime("%Y-%m-%d %H:%M:%S", localtime)
            sql=f"insert into `consult` values({consult_id},'{USER_ID}','{cid}','{text}','{chat_time}');"
            cursor.execute(sql)

        #取得MANAGER所有聯絡人id
        if type=="1":
            chat_id_list=[]
            sql=f"SELECT `receive_id`,`sender_id` FROM `consult` WHERE `receive_id` = '{MANAGER_ID}' OR `sender_id` = '{MANAGER_ID}';"
            cursor.execute(sql)
            chat_id_fetch = cursor.fetchall()
            print("maid:",chat_id_fetch)
            if chat_id_fetch:
                i=0
                while i<len(chat_id_fetch):
                    j=0
                    is_repeat = 0
                    print("chat_id_fetch",chat_id_fetch[i][1],chat_id_fetch[i][0])
                    if chat_id_fetch[i][0] == MANAGER_ID:
                        while j<len(chat_id_list):
                            if chat_id_list[j] == chat_id_fetch[i][1]:
                                is_repeat = 1
                                break
                            j+=1
                        if is_repeat == 0:
                            chat_id_list.append(str(chat_id_fetch[i][1]))
                    else:
                        while j<len(chat_id_list):
                            if chat_id_list[j] == chat_id_fetch[i][0]:
                                is_repeat = 1
                                break
                            j+=1
                        if is_repeat == 0:
                            chat_id_list.append(str(chat_id_fetch[i][0]))
                    i+=1
            #取得所有聯絡人暱稱及頭像
            chat_id_info = []
            i=0
            name_ = ""
            picture_ = ""

            while i<len(chat_id_list):
                print("chat_id_list",chat_id_list[i])
                sql=f"SELECT `name`,`picture` FROM `member` WHERE `member_id` = '{chat_id_list[i]}';"
                cursor.execute(sql)
                name_and_picture_fetch = cursor.fetchall()
                if name_and_picture_fetch:
                    name_ = name_and_picture_fetch[0][0]
                    picture_ = name_and_picture_fetch[0][1]
                    if picture_:
                        picture_ = SRC + "/" + chat_id_list[i] + "/" + picture_
                    else:
                        picture_ = ""
                chat_id_info.append({"id":chat_id_list[i],"name":name_,"picture":picture_})
                i+=1
            if chat_id_info:
                print("cidinfo",chat_id_info)
                cid = chat_id_info[0]['id']
        
        #取得對方所有訊息
        all_chat_text = []
        print("cid",cid)
        sql=f"SELECT * FROM `consult` WHERE `receive_id` = '{cid}' AND `sender_id` = '{MANAGER_ID}';"
        cursor.execute(sql)
        right_text_fetch = cursor.fetchall()
        sql=f"SELECT * FROM `consult` WHERE `receive_id` = '{MANAGER_ID}' AND `sender_id` = '{cid}';"
        cursor.execute(sql)
        left_text_fetch = cursor.fetchall()
        i=0
        j=0
        sql = f"SELECT `name` FROM `member` WHERE `member_id` = '{cid}';"
        cursor.execute(sql)
        cname_fetch = cursor.fetchall()
        if cname_fetch:
            cname = cname_fetch[0][0]
        while i<len(right_text_fetch) and j<len(left_text_fetch):
            if right_text_fetch[i][4]<left_text_fetch[j][4]:            
                all_chat_text.append({"text":right_text_fetch[i][3],"side":"right"})
                i+=1
            else:
                all_chat_text.append({"text":left_text_fetch[j][3],"side":"left","name":cname})
                j+=1
        while i<len(right_text_fetch):
            all_chat_text.append({"text":right_text_fetch[i][3],"side":"right"})
            i+=1
        while j<len(left_text_fetch):
            all_chat_text.append({"text":left_text_fetch[j][3],"side":"left","name":cname})
            j+=1
        
        connection.commit()
        can_chat = "0"
        print("cidid_info",chat_id_info)
        if chat_id_info:
            can_chat = "1"
        print(can_chat)
        return render_template("manager_chat.html",can_chat=can_chat,cid=cid,chat_id_info=chat_id_info,all_chat_text=all_chat_text,IS_LOGIN=IS_LOGIN,USER_AVATAR_SRC=USER_AVATAR_SRC,USER_NAME=USER_NAME,USER_ID=USER_ID)
    else:
        return render_template("manager_chat.html",IS_LOGIN=IS_LOGIN)

@app.route("/customer_service.html", methods=['POST','GET'])
def customer_service():
    global IS_LOGIN
    global USER_AVATAR_SRC
    global USER_NAME
    global USER_CARD
    global USER_ID
    global SRC
    global MANAGER_ID
    global chat_id_list
    global chat_id_info
    cursor = connection.cursor()
    need_sub = 0
    if IS_LOGIN=="1":
        consult_id = "0"
        type = str(request.args.get('type'))
        if type=="0":#送出訊息
            sql=f"SELECT COUNT(*) FROM `consult`;"
            cursor.execute(sql)
            consult_id_num = cursor.fetchall()
            if consult_id_num or consult_id_num[0][0] == 0:
                consult_id = str(int(consult_id_num[0][0])+100000)
                sql=f"SELECT COUNT(*) FROM `consult` WHERE `consult_id` = {consult_id};"
                cursor.execute(sql)
                repeat_id_fetch = cursor.fetchall()
                if repeat_id_fetch and repeat_id_fetch[0][0]>0:
                    consult_id = 100000
                    need_sub = 1
                while repeat_id_fetch and repeat_id_fetch[0][0]>0:
                    sql=f"SELECT COUNT(*) FROM `consult` WHERE `consult_id` = {consult_id};"
                    cursor.execute(sql)
                    repeat_id_fetch = cursor.fetchall()
                    consult_id += 1
                if need_sub == 1:
                    consult_id -= 1
            text=str(request.values['chat_text'])
            localtime = time.localtime()
            chat_time = time.strftime("%Y-%m-%d %H:%M:%S", localtime)
            sql=f"insert into `consult` values({consult_id},'{USER_ID}','000000','{text}','{chat_time}');"
            cursor.execute(sql)
        
        #取得對方所有訊息
        all_chat_text = []
        sql=f"SELECT * FROM `consult` WHERE `receive_id` = '{MANAGER_ID}' AND `sender_id` = '{USER_ID}';"
        cursor.execute(sql)
        right_text_fetch = cursor.fetchall()
        sql=f"SELECT * FROM `consult` WHERE `receive_id` = '{USER_ID}' AND `sender_id` = '{MANAGER_ID}';"
        cursor.execute(sql)
        left_text_fetch = cursor.fetchall()
        i=0
        j=0
        while i<len(right_text_fetch) and j<len(left_text_fetch):
            if right_text_fetch[i][4]<left_text_fetch[j][4]:            
                all_chat_text.append({"text":right_text_fetch[i][3],"side":"right","name":USER_NAME})
                i+=1
            else:
                all_chat_text.append({"text":left_text_fetch[j][3],"side":"left"})
                j+=1
        while i<len(right_text_fetch):
            all_chat_text.append({"text":right_text_fetch[i][3],"side":"right","name":USER_NAME})
            i+=1
        while j<len(left_text_fetch):
            all_chat_text.append({"text":left_text_fetch[j][3],"side":"left"})
            j+=1
        
        #取得USER所有聯絡人id
        if type=="1":
            #取得所有聯絡人暱稱及頭像
            chat_id_info = []
            chat_id_info.append({"id":MANAGER_ID})
        connection.commit()
        return render_template("customer_service.html",cid=MANAGER_ID,chat_id_info=chat_id_info,all_chat_text=all_chat_text,IS_LOGIN=IS_LOGIN,USER_AVATAR_SRC=USER_AVATAR_SRC,USER_NAME=USER_NAME,USER_ID=USER_ID)
    else:
        return render_template("customer_service.html",IS_LOGIN=IS_LOGIN)


####test
#@app.route("/submit", methods=['POST','GET'])
#def submit():
#    firstname = request.values['firstname']
#    lastname = request.values['lastname']
#    return render_template('submit.html',**locals())
#@app.route("/form")
#def form():
#    return render_template('form.html')
app.run()