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
AWARD_BASE_URL = 'http://www.kopis.or.kr/openApi/restful/prfawad?service=' + API_KEY
client = MongoClient('localhost', 27017)
db = client.dbarts

with open('genre.json') as genre_json:
    genre_data = json.load(genre_json)

with open('area.json') as area_json:
    area_data = json.load(area_json)

# Date
today = date.today()
st_date = '&stdate=' + today.strftime("%Y0101")
ed_date = '&eddate=' + today.strftime("%Y1231")


def get_performances(url):
    r = requests.get(url)
    obj = xmltodict.parse(r.text)
    performances = []

    if not obj['dbs']:
        return []

    if type(obj['dbs']['db']) is list:
        for performance in obj['dbs']['db']:
            data = json.dumps(performance, ensure_ascii=False)
            performances.append(json.loads(data))
    else:
        performances.append(json.loads( json.dumps(obj['dbs']['db'], ensure_ascii=False)))

    return performances

# HTML 화면 보여주기
@app.route("/")
def main():
    url = BASE_URL + st_date + ed_date + '&cpage=1&rows=10&prfstate=02&signgucode=11&signgucodesub=1111'
    performances = get_performances(url)

    return render_template('index.html', performances=performances)

@app.route("/performance")
def performance():
    total_performances = {}

    # this month
    url_month = BASE_URL + st_date + ed_date + '&cpage=1&rows=12&prfstate=02'
    total_performances['month'] = get_performances(url_month)
    # 뮤지컬
    url_musical = BASE_URL + st_date + ed_date + '&cpage=1&rows=12&prfstate=02&shcate=AAAB&signgucode=11&signgucodesub=1111'
    total_performances['musical'] = get_performances(url_musical)
    # 연극
    url_play = BASE_URL + st_date + ed_date + '&cpage=1&rows=12&prfstate=02&shcate=AAAA'
    total_performances['play'] = get_performances(url_play)
    # 클래식
    url_classic = BASE_URL + st_date + ed_date + '&cpage=1&rows=12&prfstate=02&shcate=CCCA|CCCB'
    total_performances['classic'] = get_performances(url_classic)
    # 무용
    # url_ballet = BASE_URL + st_date + ed_date + '&cpage=1&rows=12&prfstate=02&shcate=CCCB'
    # total_performances['ballet'] = get_performances(url_ballet)
    # kids
    url_kids = BASE_URL + st_date + ed_date + '&cpage=1&rows=12&prfstate=02&signgucode=11&signgucodesub=1111&kidstate=Y'
    total_performances['kids'] = get_performances(url_kids)
    # Awards Winning
    url_awards = AWARD_BASE_URL + st_date + ed_date + '&cpage=1&rows=12&prfstate=02'
    total_performances['awards'] = get_performances(url_awards)

    return render_template('performance.html', performances=total_performances)

@app.route("/performance_detail/<id>")
def performance_detail(id):
    url = 'http://www.kopis.or.kr/openApi/restful/pblprfr/%s?service=' % id + API_KEY
    performance = get_performances(url)
    imgs = performance[0]['styurls']['styurl']
    if performance[0]['styurls'] and type(performance[0]['styurls']['styurl']) != list:
        imgs = [performance[0]['styurls']['styurl']]

    return render_template('performance_detail.html', performance=performance[0], imgs=imgs)

@app.route("/recommend")
def recommend():
    return render_template('recommend.html', genres=genre_data.keys(), areas=area_data.keys())

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

@app.route('/search', methods=['GET'])
def search_performance():
    nums = 20
    keyword = request.args.get('keyword').strip()
    rows = '&rows=' + str(nums)
    url = BASE_URL + st_date + ed_date + '&cpage=1' + rows + '&prfstate=02&shprfnm=%s' % keyword
    performances = get_performances(url)

    return jsonify({'all_performances': performances})

@app.route('/recommendation', methods=['GET'])
def recommend_performance():
    nums = 20
    rows = '&rows=' + str(nums)
    url = BASE_URL + st_date + ed_date + '&cpage=1' + rows + '&prfstate=02'
    genre = request.args.get('genre')
    area = request.args.get('area')
    kids = request.args.get('kids')
    if genre:
        url += '&shcate=' + genre_data[genre]
    if area:
        url += '&signgucode=' + str(area_data[area])
    if kids == 'true':
        url += '&kidstate=Y'

    performances = get_performances(url)

    return jsonify({'all_performances': performances})


if __name__ == "__main__":
    app.run(debug=True)

