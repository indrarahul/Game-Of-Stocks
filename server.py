from flask import Flask, jsonify,request
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from flask_cors import CORS
import json, urllib.request
from urllib.error import HTTPError, URLError
import datetime

app = Flask(__name__)
app.config['MONGO_DBNAME'] = 'Stock'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/Stock'
mongo = PyMongo(app)
CORS(app)
API_KEY = "P__qP96smNyE9xmgRxxY"
urli = "https://www.quandl.com/api/v3/datasets/NSE/"

def fetch1(ticker,startDate,endDate,Open,stocks):
	startIndex = 0
	endIndex = 0
	
	result = []
	priceHis = []
	for field in stocks.find():
		lent = len(field['priceHistory'][0])
		if(field['ticker']==ticker):
			if(startDate!=''):
				while(startDate < field['priceHistory'][0][startIndex]['Date'] and startIndex <= lent):
					startIndex += 1
			if(endDate!=''):
				while(endDate < field['priceHistory'][0][endIndex]['Date'] and endIndex <= lent):
					endIndex += 1
			elif(endDate==''):
				endIndex = lent-1
			if(Open=='1'):
				priceHis = field['priceHistory'][0][startIndex:endIndex+1]
			else:
				for i in field['priceHistory'][0]:
					del i['Open']
				priceHis = field['priceHistory'][0][startIndex:endIndex+1]
			result.append({ 'ticker' : field['ticker'] , 'priceHistory' : priceHis, 'createdDate' : field['createdDate'] })
	return result



def fetch(ticker):
	try:
		url = urllib.request.urlopen(urli + ticker + '.json?api_key=' + API_KEY)
		data = json.loads(url.read().decode())
	except HTTPError:
		return "Error"
	except URLError:
		return "Error"

	priceHis = []
	for i in data['dataset']['data']:
		 priceHis.append({ 'Date' : i[0], 'Open' : i[1], 'Close' : i[5]})
	result = []
	time = str(datetime.datetime.now()).split(' ')[0]
	result.append({ 'ticker' : ticker , 'priceHistory' : priceHis, 'createdDate' : time })
	return result


@app.route('/api/stock', methods=['GET'])
def get_stock():
	stocks = mongo.db.stock
	ticker = request.args.get('ticker')
	startDate = request.args.get('startDate')
	endDate = request.args.get('endDate')
	Open = request.args.get('Open')
	if(startDate==None):
		startDate = ''
	if(endDate==None):
		endDate = ''
	result = []
	result = fetch1(ticker,startDate,endDate,Open,stocks)
	if(result==[]):
		result = fetch(ticker)
		if(result=="Error"):
			return "URL Error"
		stocks.insert({'ticker':result[0]['ticker'], 'priceHistory': [result[0]['priceHistory']] , 'createdDate':result[0]['createdDate']})
	result = fetch1(ticker,startDate,endDate,Open,stocks)
	return jsonify(result)

if __name__ == "__main__":
	app.run(host='0.0.0.0')