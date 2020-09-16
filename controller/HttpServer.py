from flask import Flask, render_template, jsonify, request
from model.Prices import CandleData
from model.Indicators import  Indicators

PORT = 8700
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

@app.route('/webapi/oanda/', methods=["POST"])
def oanda():
    #d = request.get_data()
    #json = request.json
    #json2 = request.get_json()
    form = request.form
    currency = form['currency']
    length = form['length']
    timeframe = form['timeframe']
    size = int(form['extra_size'])
    items = form.items()
    dict = {}
    for key, value in items:
        dict[key] = value
    extra = []
    for i in range(size):
        key = 'extra[' + str(i) + '][number]'
        number = dict[key]
        key = 'extra[' + str(i) + '][method]'
        method = dict[key]
        key = 'extra[' + str(i) + '][window]'
        window = int(dict[key])
        extra.append([number, method, window])

    data = CandleData(currency, timeframe)
    candles = data.loadData(limit=length)
    indicators = Indicators(candles)
    dic = data.value
    for number, method, window in extra:
        if method == 'sma':
            d = indicators.sma(window)
            dic[number] = d
    return jsonify(dic), 200

@app.route('/webapi/oandafx2/', methods=['GET'])
def dataSource2():
    currency = request.args.get('currency')
    length = request.args.get('length')
    timeframe = request.args.get('timeframe')
    data = CandleData(currency, timeframe)
    candles = data.loadData(limit=length)
    dic = data.value
    return jsonify(dic), 200

def start():
    app.run(host='127.0.0.1', port=PORT, threaded=True)