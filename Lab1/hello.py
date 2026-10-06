# ===================== PART 1 =====================
# msg = "Roll a dice by Zeina Sleiman!"
# print(msg)

# ===================== PART 2 =====================
# from flask import Flask
#
# app = Flask(__name__)
#
# @app.route('/')
# def hello_world():
#     return 'Hello World by Zeina Sleiman!'

# ===================== PART 3 =====================
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')
