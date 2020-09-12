from flask import Flask, render_template, jsonify, request
from model.Prices import CandleData

PORT = 9000
app = Flask(__name__, template_folder='../view')

@app.teardown_appcontext
def removeSession(ex=None):
    from model.PriceDB import Session
    Session.remove()

@app.route('/')
def index():
    return render_template('./candlechart.html')
    app.logger.info('index')
    #data = CandleData('USD_JPY', 'M1')
    #candles = data.loadData(limit=20)
    #return render_template('./chart.html', candles=candles)

@app.route('/webapi/oandafx/', methods=['GET'])
def dataSource():
    currency = request.args.get('currency')
    length = request.args.get('length')
    timeframe = request.args.get('timeframe')
    data = CandleData(currency, timeframe)
    candles = data.loadData(limit=length)
    d = data.value
    return jsonify(data.value), 200

def start():
    app.run(host='127.0.0.1', port=PORT, threaded=True)