from flask import Flask, render_template
import requests

app = Flask(__name__)
API_KEY = "4c63018be1fc4d10a6118f339347226f"

# HTML 화면 보여주기
@app.route("/")
def main():
    return render_template('index.html')

@app.route("/performance")
def performance():
    return render_template('performance.html')

# API 역할을 하는 부분
def get_performance_list():
    return ''

if __name__ == "__main__":
    app.run()
