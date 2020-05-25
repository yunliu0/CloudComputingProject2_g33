import controller
from flask import Flask, render_template, flash, redirect, url_for, session, request, logging, send_from_directory

app = Flask(__name__, static_url_path='')

# Index
@app.route('/')
def index():
    filepath = controller.GetLocalGig()
    return render_template('home.html',path=filepath)

# About
@app.route('/about')
def about():
    return render_template('about.html')

# Scenario
@app.route('/scenario', methods=['GET', 'POST'])
def scenario():
    if request.method == 'POST':
        id = request.form['id']
        if id == "yun":
            return render_template('about.html')
        if id == "rohan":
            return render_template('about.html')
        if id == "alvin":
            return render_template('about.html')

def income_tweets():
    filepath = controller.get_income_tweet()
    return render_template('income_tweet.html', path=filepath)

def business_popularity():
    filepath = controller.get_business_pop_location()
    fp2 = controller.get_business_popularity()
    return render_template('tweet_pop.html', vic_fp=filepath[0], nsw_fp=filepath[1],
    wa_fp=filepath[2], sa_fp=filepath[3], nt_fp=filepath[4], act_fp=filepath[5],
    qld_fp=filepath[6], tas_fp=filepath[7], overall=fp2)

def unemployment_tweets():
    filepath = controller.get_unemployment_tweet()
    return render_template('unemp_tweet.html', path=filepath)

#Getting css file
@app.route('/content/<path:path>')
def serve_css(path):
    return send_from_directory('content', path)

#Getting img file
@app.route('/img/<path:path>')
def serve_img(path):
    return send_from_directory('img', path)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')


