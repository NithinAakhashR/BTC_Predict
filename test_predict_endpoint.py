import urllib.request
import json

req = urllib.request.Request(
    'http://127.0.0.1:5000/predict_daily',
    data=b'{}',
    headers={'Content-Type': 'application/json'},
    method='POST'
)

try:
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = resp.read().decode('utf-8')
        print(data[:1200])
except Exception as e:
    print('ERROR', type(e).__name__, e)
