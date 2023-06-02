from mock_request_api import update, add_metric_to_bucket
from ryte import extract_data_for_x_days, update_ryte
from flask import Flask, request, jsonify


app = Flask(__name__)

@app.route('/createGA', methods=['POST'])
def timespan_api():
    data = request.get_json()
    print(data)
    days = data.get('days')
    metric = data.get('metric')
    buc = data.get('bucket')
    metricForm = data.get('metricForm')
    displayedDays = data.get('displayedDays')
    add_metric_to_bucket(days, metric, buc, metricForm, displayedDays)
    return jsonify({'message': 'Data has been written to InfluxDB'}), 200

@app.route('/updateGA', methods=['POST'])
def update_metrics():
    data = request.get_json()
    print(data)
    buc = data.get('bucket')
    update(buc)
    return jsonify({'message': 'Data has been written to InfluxDB'}), 200

@app.route('/createRyte', methods=['POST'])
def create_ryte():
    data = request.get_json()
    print(data)
    days = data.get('days')
    bucket = data.get('bucket')
    attributeList = data.get('attributeList')
    api_key = data.get('api_key')
    project = data.get('project')
    extract_data_for_x_days(bucket, attributeList, days, api_key, project)
    return jsonify({'message': 'Data has been written to InfluxDB'}), 200

@app.route('/updateRyte', methods=['POST'])
def update_ryte():
    data = request.get_json()
    print(data)
    bucket = data.get('bucket')
    attributeList = data.get('attributeList')
    api_key = data.get('api_key')
    project = data.get('project')
    update(bucket, attributeList, api_key, project)
    return jsonify({'message': 'Data has been written to InfluxDB'}), 200

if __name__ == '__main__':
  app.run(debug=True)
  