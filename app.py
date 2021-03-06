from flask import Flask, abort, render_template, request, jsonify
import requests as r
import json
import datetime
from urllib.parse import quote_plus

app = Flask(__name__)
app.config.from_pyfile('settings.py')


#To count the age of blocks and transactions
def timestamp_difference(current, timestamp):
    difference = current - datetime.datetime.strptime(timestamp, app.config['DATETIME_FORMAT'])
    difference = difference.total_seconds()
    if difference < 60:
        return str(int(difference)) + ' sec'
    elif difference < 3600:
        return str(int(round(difference/ 60))) + ' min'
    elif difference < 86400:
        return str(int(round(difference/ 3600))) + ' hours'
    elif difference < 2592000:
        return  str(int(round(difference/ 86400))) + ' days'
    else:
        return 'more than a month'

#To get the lists of latest blocks and transactions for explorer
def get_explorer_data():
    current = datetime.datetime.now();
    transactions = r.get(app.config['EXPLORER_API_URL']+'_transactions?limit='+str(app.config['EXPLORER_ITEM_LIMIT'])).json()
    blocks = r.get(app.config['EXPLORER_API_URL']+'_blocks?limit='+str(app.config['EXPLORER_ITEM_LIMIT'])).json()
    for tn in transactions:
        tn['plain_date'] = tn['dt']
        tn['dt'] = timestamp_difference(current, tn['dt'])
    for block in blocks:
        block['plain_date'] = block['dt']
        block['dt'] = timestamp_difference(current, block['dt'])
    data = {
        'blocks' : blocks,
        'transactions' : transactions,
    }
    return data


#To collect data that is supposed to by displayed in analytics
def get_analytics_data():
	return 1


#Single Block page
def get_block(block_depth):
    block = r.get(app.config['COMMON_API_URL']+'_search_detailed', 
                  params={'search': block_depth, 'search_type': 'blocks'}).json()
    transactions_data = r.get(app.config['COMMON_API_URL']+'_block_history', 
                              params={'block': block_depth}).json()
    data = {
        'block' : block,
        'transactions': transactions_data['transactions']
    }
    return data 


#Single Transaction page
def get_transaction(txn_hash):
    encoded_hash = quote_plus(txn_hash)
    tnx = r.get(app.config['COMMON_API_URL']+'_search_detailed?search='+str(encoded_hash)+'&search_type=transactions').json()
    data = {
        'transaction' : tnx
    }
    return data	


#Single Address page
def get_address(address_name):
    address_transactions = r.get(app.config['COMMON_API_URL']+'_search_detailed', 
                                 params={'search': address_name, 'search_type': 'address'}).json()
    address_balance = r.get(app.config['COMMON_API_URL']+'_balance', 
                                 params={'address': address_name}).json()
    data = {
        'address_transactions' : address_transactions,
        'address_balance': address_balance
    }
    return data

#Saerch results accirding to the searchword
def get_search_results(searchword):
    search_endpoint = app.config['COMMON_API_URL']+'_search'
    addresses = r.get(search_endpoint, params={'search': searchword, 'search_type': 'address'}).json()
    tnx = r.get(search_endpoint, params={'search': searchword, 'search_type': 'transactions'}).json()
    blocks = r.get(search_endpoint, params={'search': searchword, 'search_type': 'blocks'}).json()
    data = {
        'blocks' : blocks['data'],
        'tnx' : tnx['data'],
        'addresses' : addresses['data']
    }
    return data


#Explorer (homepage)
@app.route('/')
def explorer():
    return render_template('explorer.html', data=get_explorer_data())


#Analytics
@app.route('/analytics')
def analytics():
    return render_template('analytics.html', data=get_analytics_data())


@app.route('/block/<block_depth>/')
def single_block(block_depth):
    data = get_block(block_depth)
    if not data['block']:
        abort(404)
    return render_template('block.html', data=data['block'][0], block_depth = block_depth,
                           transactions=data['transactions'])


@app.route('/transaction/<path:txn_id>/')
def single_transaction(txn_id):
    data = get_transaction(txn_id)
    if not data['transaction']:
        abort(404)
    return render_template('transaction.html', data=data['transaction'][0], txn_id = txn_id)


@app.route('/address/<address_name>/')
def single_address(address_name):
    data = get_address(address_name)
    if not data['address_transactions']:
        abort(404)
    return render_template('address.html', data=data['address_transactions'], 
                           address_name=address_name, address_balance=data['address_balance']['balance'])

@app.route('/search', methods=['POST', 'GET'])
def search():
    searchword = request.args.get('searchword', default='', type=str)
    return render_template('search.html', data=get_search_results(searchword), searchword = searchword)

@app.route('/_metrics', methods=['POST', 'GET'])
def metrics():
    #from_timestamp = request.args.get('from_timestamp', default = '', type = str);
    #to_timestamp = request.args.get('to_timestamp', default = '', type = str);
    interval = request.args.get('interval', default = '1h', type = str)
    metric_name = request.args.get('metric_name', default = 'transaction_volume', type = str)
    mode = request.args.get('mode', default = 'live', type = str)
    call_address = app.config['CHARTS_API_URL'] + '_metric?'
    call_address += 'from_timestamp=2020-07-23 00:00:00'
    call_address += f'&to_timestamp={datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}' 
    call_address += '&interval=' + interval
    call_address += '&metric_name=' + metric_name
    call_address += '&mode=' + mode
    data = r.get(call_address).json()
    results = {
        'metric' : metric_name,
        'interval' : interval,
        'x_name' : 'dt',
        'y_name' : 'value',
        'json_data' : data
    }
    return results

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


if __name__ == '__main__':
    port = app.config['PORT']
    app.run(debug=True, host='0.0.0.0', port=port)