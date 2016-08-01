


# 개인용 파이낸스 DB (MySQL+crontab)

개인용 파이낸스 DB구축에 기반이 될만한 DB와 데이터 입니다. 다음과 같은 table로 구성되어 있습니다.

* stock_master : 전종목 코드와 이름
* stock_desc : 전종목 부가 정보 
* stock_price : 전종목 전기간(상장이후 일일 시고저종+거래량)
* stock_dart : 금감원 전자공시의 공시보고서 링크 전체


```bash
# check your working directory
$ cd ~/workspace/
$ pwd
/home/ubuntu/workspace

# cloning from git reposity
$ git clone https://gist.github.com/d103b7677376030fd24de8f87ca59de7 findb 
$ cd findb

# mysql data restore
$ wget -O findb_dump.sql.gz "https://googledrive.com/host/0B2Op0f7i-jUEMGJ0bzFNMmYxa3M"
$ gunzip < findb_dump.sql.gz | mysql -u admin -p

```