import httplib2
import sys
import base64
from price import *
import pprint
import json
import time
from datetime import datetime
from datetime import date
import random
import pickle
import pymysql


import configparser
config = configparser.ConfigParser()
config.read('/aicsvc/app/config.ini')
api_key = config['BITHUMB']['connect_key']
api_secret = config['BITHUMB']['secret_key']
myip = config['MYSQL']['myip']
myport = config['MYSQL']['myport']
myid = config['MYSQL']['myid']
mypw = config['MYSQL']['mypw']
# print(myport);

starttime = datetime.now()
timestemp = datetime.now().strftime('%Y-%m-%d %H:%M')

api = XCoinAPI(api_key, api_secret);

connmysql = pymysql.connect(myip, myid, mypw, db='coin', charset='utf8', port=23306)
curs = connmysql.cursor(pymysql.cursors.DictCursor)

sql = "select `NAME` from INFO"
curs.execute(sql)
rows = curs.fetchall()
random.shuffle(rows)

for i in rows:
    i = i['NAME']
    a = 0  # 회전 수
    b = 0  # 반구매 지수
    c = 0  # 구매 지수
    d = 0  # 구매 대기 지수
    o = 0
    r = 0
    rgParams = {
        "currency": i
    };
    xcoinresult = api.xcoinApiCall("/info/balance", rgParams);
    xcoinprice = xcoinresult['data']["xcoin_last"]
    xcoin = xcoinresult['data']["total_%s" % i.lower()]
    totalwon = xcoinresult['data']["total_krw"]
    xcoinstatus = xcoinresult['status']
    if xcoinstatus != '0000':
        totalwon = 0
    elif totalwon < 99000:
        buylimitcost = totalwon
        buylimitcost = float(buylimitcost)
        xcoinprice = float(xcoinprice)

    else:
        buylimitcost = 99000
        xcoinprice = float(xcoinprice)

    memcosts = round(( buylimitcost / xcoinprice  ) - 0.0001 , 3)
    # memcosts = round(memcosts, 3)
    print(memcosts);

    buycost = memcosts * xcoinprice
    buycost = int(float(buycost) * 10000) / 10000
    print(buycost);

    limitsql = "select `BUYLIMIT`,`AGE`,`BUYCOST`,`HAVECOIN` from INFO where NAME = '%s'" % i
    curs.execute(limitsql)
    limitcost = curs.fetchall()
    limit = limitcost[0]['BUYLIMIT']
    age = limitcost[0]['AGE']
    limit = float(limit)
    age = int(age)

    print(i, " 코인 구매 요청 수 : ", memcosts, "개, 최소구매 코인 수 : ", limit, "원, 사용 예상 금액 : ", buycost , "원, 기존구매 횟수 : ", age);


    while a < 10:
        # time.sleep(1)
        if b >= 5:  # 반구매 5 이상 정지
            break
        else:
            pass

        try:
            rgParams = {
                "currency": ""
            };
            priceurl = api.xcoinApiCall("/public/transaction_history/" + i, rgParams);
            pricestatus = priceurl['status']
            if pricestatus != '0000' :
                print(pricestatus['message']);
                chat = "code ERR %s " %pricestatus
                send(chat)
            else:

                for s in range(0, 19):
                    sprice = float(priceurl['data'][s]['price'])
                    sum1 = 0
                    sum1 = sum1 + sprice
                sum1 = int(sum1) / 20

                if a == 0:
                    matchprice = sum1
                    print(i , " 첫번째 대비값 : ", matchprice, ", 첫번째 수집값 : ", sum1);
                elif a == 9:
                    print(" 구매여력 : ", buylimitcost, " 현금 : ", totalwon, " 구매수치 : ", c);
                    print("");
                else:
                    pass


            if matchprice < sum1:
                a = a + 1
                c = c + 1
                matchprice = sum1

            elif matchprice == sum1:
                a = a + 1
                if d == 3:
                    c = c - 1
                    d = 1
                else:
                    d = d + 1
            else:
                a = a + 1
                b = b + 1
                matchprice = sum1


            memchk = memcosts * 100000
            limitchk = limit * 100000


            # print("구매가능액 : ", memcosts, "최하 구매코인 : ", limit, "AGE 값 : ", age, "보유현금 : ", totalwon, " o = ", o);


            timesql = " SELECT * FROM coin.MAIMAIDATA where NAME='%s' order by NO desc  limit 0,10 " %i


            if  memchk < limitchk or  totalwon < 10000  or age > 1 or memcosts == 0.0 or memcosts == 0 :  # 구매 가능 코인이 최소 구매 코인보다 많거나 age 가 2보다 작으면
                # print(i, " 구매 없음");
                pass
            elif  c > 6 or o >= 10:
                print("구매 가능 : ", memchk, ", 구매 제한 : ", limitchk);
                print("------------------구매시작------------------");
                rgParams = {
                    "currency": i, "units": memcosts
                };
                buyresult = api.xcoinApiCall("/trade/market_buy", rgParams);  # 구매 명령
                buystatus = buyresult['status']
                # print("aaaa", buyresult);

                if buystatus != '0000':  # 응답 정상여부
                    print("비정상 코드 : ", buystatus);  # 에러 메세지 출력
                    chat = "buy Err %s " %buystatus
                    send(chat)
                else:
                    c = 0
                    a = 9
                    ### 구매 요청 정보 ###

                    contid = buyresult['data'][0]['cont_id']
                    buyunits = buyresult['data'][0]['units']
                    buyprice = buyresult['data'][0]['price']
                    buyfee = buyresult['data'][0]['fee']
                    buyunits = float(buyunits)
                    buyprice = float(buyprice)
                    buyfee = float(buyfee)

                    if age > 0 :
                        agecost = age + 1
                    else :
                        agecost = 1


                    rgParams = {
                        "currency": i
                    };
                    coinresult = api.xcoinApiCall("/info/balance", rgParams);
                    coinstatus = coinresult['status']
                    if coinstatus != '0000':
                        chat = " U Need clearing COIN , %s failed updating coin information" %i
                        send(chat)
                    else:
                        coincost = coinresult['data']["xcoin_last"]
                        havecoin = coinresult['data']["total_%s" % i.lower()]
                        my_price = float(coincost) * float(havecoin)

                        coincost = int(float(coincost) * 10000) / 10000
                        havecoin = int(float(havecoin) * 10000) / 10000
                        my_price = int(float(my_price) * 10000) / 10000

                        sqldata = "`AGE` = %s, `NEWCOST` = %s, `BUYCOST` = %s, `HAVECOIN` = %s, `BUYDATE` = '%s'" % ( agecost, my_price, coincost, havecoin, timestemp)
                        sql = "update `coin`.`INFO` set  %s where NAME = '%s' " % (sqldata, i)

                        curs.execute(sql)
                        connmysql.commit()

                    sobi = (buyunits * buyprice) + buyfee
                    print("구매가 : " , sobi);
                    chat = " %s 구매 예상 사용 금액 : %s" % (i, sobi)
                    send(chat)
            else:
                pass
        except Exception as e:
            print(e);
            chat = "구매 Err : %s  " %i
            send(chat)
            # print("xcoinresult : ", xcoinresult );
            # print("wonresult : ", wonresult);
            # print("priceurl : ", priceurl);
            # print("buyresult : ", buyresult);
            # print("coinresult : ", coinresult);
            # chat = "Exception : %s " % e
            # send(chat)
            pass


############################################################################################################################################################################################################################################################################################################################################################################################################
#############################################################################################################################################################################################################################################################################################################################################################################################################
#############################################################################################################################################################################################################################################################################################################################################################################################################
#############################################################################################################################################################################################################################################################################################################################################################################################################
#############################################################################################################################################################################################################################################################################################################################################################################################################
#############################################################################################################################################################################################################################################################################################################################################################################################################
#############################################################################################################################################################################################################################################################################################################################################################################################################
#############################################################################################################################################################################################################################################################################################################################################################################################################
#############################################################################################################################################################################################################################################################################################################################################################################################################

connmysql.close()
endtime=datetime.now()
print(datetime.now());
playtime = endtime - starttime
print("소요시간 : " ,playtime);
sys.exit(0);

