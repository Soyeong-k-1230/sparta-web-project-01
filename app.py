from flask import Flask, render_template
import requests
import xmltodict, json

app = Flask(__name__)
API_KEY = "4c63018be1fc4d10a6118f339347226f"

# HTML 화면 보여주기
@app.route("/")
def main():
    r = requests.get('http://www.kopis.or.kr/openApi/restful/pblprfr?service=4c63018be1fc4d10a6118f339347226f&stdate=20210601&eddate=20210731&cpage=1&rows=10&prfstate=02&signgucode=11&signgucodesub=1111')
    obj = xmltodict.parse(r.text)
    data = json.dumps(obj['dbs']['db'], ensure_ascii=False)
    # print(obj_json)
    return render_template('index.html', data=data)

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
