import pymysql
from database import Base, engine
from pymysql import cursors

# 본인 mysql의 user이름, password, db이름 작성
conn = pymysql.connect(host='127.0.0.1', user='root', password='1234', db='Capstone', charset='utf8')
cursor = conn.cursor(cursors.DictCursor)
Base.metadata.create_all(bind=engine)

# 사용자 DB에서 사용자 ID 확인
def UserDBCheck(userID) :
    query = "SELECT * FROM user where id = %s"
    cursor.execute(query, (userID))
    result = cursor.fetchall()
    return result