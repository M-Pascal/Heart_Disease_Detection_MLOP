from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('retrain.html')

@app.route('/Prediction')
def prediction():
    return render_template('form.html')

@app.route('/form')
def form():
    return render_template('form.html')

@app.route('/visualize')
def visualize():
    return render_template('visualization.html')


@app.route('/retrain')
def retrain():
    return render_template('retrain.html')

if __name__ == '__main__':
    app.run(debug=True)
