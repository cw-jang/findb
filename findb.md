# 개인용 파이낸스 DB (MySQL+crontab)

개인용 파이낸스 DB구축 데이터 입니다. 다음과 같은 table로 구성되어 있습니다.

* stock_master : 전종목 코드와 이름
* stock_desc : 전종목 부가 정보 
* stock_finstate : 전종목 재무제표 (네이버 파이낸스)
* stock_price : 전종목 전기간(상장이후 일일 시고저종+거래량)
* stock_dart : 금감원 전자공시의 공시보고서 링크 전체

# 설치와 초기 데이터 구축

```bash
# check your working directory
$ cd ~/workspace/
$ pwd
/home/ubuntu/workspace

# git 저장소 클론 (.py 프로그램들)
$ git clone https://gist.github.com/d103b7677376030fd24de8f87ca59de7 findb 
$ cd findb

# MySQL 데이터 다운로드 및 리스토어
$ wget -O findb_dump.sql.gz "https://googledrive.com/host/0B2Op0f7i-jUEMGJ0bzFNMmYxa3M"
$ gunzip < findb_dump.sql.gz | mysql -u admin -p
```

# MySQL DB 데이터 확인
```bash
plusjune:~/workspace/findb (master) $ mysql-ctl cli

mysql> use findb;
Reading table information for completion of table and column names
You can turn off this feature to get a quicker startup with -A

Database changed
mysql> show tables;
+-----------------+
| Tables_in_findb |
+-----------------+
| stock_dart      |
| stock_desc      |
| stock_finstate  |
| stock_master    |
| stock_price     |
+-----------------+
5 rows in set (0.00 sec)

mysql> select count(*) from stock_price;
+----------+
| count(*) |
+----------+
|  6025305 |
+----------+
1 row in set (0.00 sec)
```


# 주기적 크롤링 (crontab 등록)

```bash
# 종목 코드와 종목명(stock_master): 매월 1일, 06시 10분 
10 6 1 * * /home/ubuntu/workspace/findb/stock_master.py  

# 종목 부가정보(stock_desc) 매월 1일, 06시 10분 
20 6 1 * * /home/ubuntu/workspace/findb/stock_desc.py  

# 재무제표(stock_finstate) 매월 1일, 06시 10분 
30 6 1 * * /home/ubuntu/workspace/findb/stock_finstate.py  

# 가격(stock_price), 매일 18시
0 18 * * * /home/ubuntu/workspace/findb/stock_price.py

# 전자공시(dart), 매일 06시~18시 15분 마다
15 6-18 * * * /home/ubuntu/workspace/findb/stock_dart.py
```



