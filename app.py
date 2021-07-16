import os
import requests
import xmltodict, json
from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv
from datetime import date
from pymongo import MongoClient

load_dotenv(verbose=True)
app = Flask(__name__)
API_KEY = os.getenv('API_KEY')
BASE_URL = 'http://www.kopis.or.kr/openApi/restful/pblprfr?service=' + API_KEY

client = MongoClient('localhost', 27017)
db = client.dbarts

# HTML 화면 보여주기
@app.route("/")
def main():
    today = date.today()
    st_date = '&stdate=' + today.strftime("%Y%m01")
    ed_date = '&eddate=' + today.strftime("%Y%m31")
    r = requests.get(BASE_URL + st_date + ed_date + '&cpage=1&rows=10&prfstate=02&signgucode=11&signgucodesub=1111')
    obj = xmltodict.parse(r.text)
    performances = []

    for performance in obj['dbs']['db']:
        data = json.dumps(performance, ensure_ascii=False)
        performances.append(json.loads(data))

    return render_template('index.html', performances=performances)

@app.route("/performance")
def performance():
    return render_template('performance.html')

@app.route("/recommend")
def recommend():
    return render_template('recommend.html')

@app.route("/board")
def board():
    return render_template('board.html')

# API 역할을 하는 부분
@app.route('/comment', methods=['POST'])
def write_comment():
    name = request.form['name']
    content = request.form['content']
    today = date.today()

    obj = {
        'name': name,
        'content': content,
        'date': today.strftime("%Y/%m/%d")
    }
    db.comment.insert_one(obj)
    return jsonify({'msg': '저장이 완료되었습니다!'})

@app.route('/comment', methods=['GET'])
def read_comments():
    comments = list(db.comment.find({}, {'_id': False}))
    return jsonify({'all_comments': comments})


if __name__ == "__main__":
    app.run(debug=True)

