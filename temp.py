# Import needed libraries
import json
import requests
# Actual request
req = requests.get('http://10.0.0.135:5001/channel/measurement/latest', timeout=10)
data = req.json()
print('Response: \n{}'.format(json.dumps(data, indent=2)))
