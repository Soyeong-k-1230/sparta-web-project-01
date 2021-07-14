import os
import requests
import xmltodict, json
from flask import Flask, render_template
from dotenv import load_dotenv
from datetime import date

load_dotenv(verbose=True)
app = Flask(__name__)
API_KEY = os.getenv('API_KEY')
BASE_URL = 'http://www.kopis.or.kr/openApi/restful/pblprfr?service=' + API_KEY

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

# API 역할을 하는 부분
def get_performance_list():
    return ''

if __name__ == "__main__":
    app.run(debug=True)
