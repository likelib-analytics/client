#Configuration

DATETIME_FORMAT = '%Y/%d/%m %H:%M:%S'
DATETIME_FORMAT_CHARTS = '%Y-%d-%m-%H:%M:%S'

EXPLORER_API_URL = 'http://localhost:8080/api/v1/explorer/'
EXPLORER_ITEM_LIMIT = 50

CHARTS_API_URL = 'http://0.0.0.0:8080/api/v1/analytics/'
CHART_INTERVAL_MAP = {
	'1m' : 60,
	'1h' : 3600,
	'1d' : 86400
}

CHART_POINTS_AMOUNT = 100

COMMON_API_URL = 'http://0.0.0.0:8080/api/v1/'