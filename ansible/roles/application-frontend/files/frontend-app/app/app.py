from flask import Flask, render_template
import controller

app = Flask(__name__)
# Index
@app.route('/')
def index():
    return render_template('home.html',searched=False)

# About
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/stateCount')
def stateCount():
    filepath = controller.GetLocalGig()

    return render_template('home.html', path=filepath, searched= True)

@app.route('/income_tweets')
def stateCount():
    filepath = controller.GetLocalGig()

    return render_template('home.html', path=filepath, searched= True)


if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')

