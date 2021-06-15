import json
import re
import time

import requests

from src.utils.authenticator import Authenticator
from src.utils.utilities import Utilities


class SisenseApiHandler:

    def __init__(self):
        self.util = Utilities()
        self.auth = Authenticator()
        self.token = self.auth.get_token()
        self.headers = {"Authorization": "Bearer " + str(self.token),
                        'Content-Type': 'application/json'}

    def get(self, dashboard_id, widget_id):
        widget_jaql = {}
        try:
            url = SisenseApiHandler.get_widget_jaql_endpoint(self, dashboard_id, widget_id)
            response = requests.get(url, headers=self.headers)
            assert response.status_code == 200
            parsed_response = response.json()
            panels = parsed_response['metadata']['panels']
            widget_jaql['metadata'] = self.frame_jaql(panels)
        except requests.exceptions.RequestException as err:
            print('Error Occurred while GET request!' + str(err))
        return widget_jaql

    def post(self, data_source, payload):
        act_dict = {}
        try:
            url = SisenseApiHandler.get_endpoint(self, data_source)
            response = requests.post(url, data=json.dumps(payload), headers=self.headers)
            assert response.status_code == 200
            act_dict = self.response_parser(response)
        except requests.exceptions.RequestException as err:
            print('Error Occurred while POST request!' + str(err))
        return act_dict

    def build_cube(self, dashboard):
        try:
            print('Building ElastiCube...')
            data_model_id = self.util.get_widgets_id_mapping(dashboard)['data_model_id']
            url = self.auth.get_base_url() + 'v2/builds'
            body = {
                "datamodelId": data_model_id,
                "buildType": "full",
                "rowLimit": 0,
                "schemaOrigin": "latest"
            }
            response = requests.post(url, data=json.dumps(body), headers=self.headers)
            assert response.status_code == 201
            build_id = response.json()['oid']
            self.wait_till_build_completed(build_id)
        except requests.exceptions.RequestException as err:
            print('Error Occurred while building cube!' + str(err))

    def wait_till_build_completed(self, build_id):
        build_status = 'building'
        while build_status == 'building':
            time.sleep(30)
            build_status = self.get_build_status(build_id)
        if build_status == 'failed':
            assert False, 'ElastiCube build FAILED!'
        else:
            print('ElastiCube build successful!')

    def get_build_status(self, build_id):
        url = self.auth.get_base_url() + 'v2/builds/' + build_id
        response = requests.get(url, headers=self.headers)
        assert response.status_code == 200
        return response.json()['status']

    def response_parser(self, response):
        response = response.json()
        headers = response['headers']
        values = response['values']
        list_output = []
        resp = {}
        for idx, value in enumerate(values):
            if type(values[idx]) is list:
                resp = {}
                for i, item in enumerate(value):
                    header = self.format_header(headers[i])
                    resp[header.lower()] = self.format_value(header, str(item['data']))
                list_output.append(resp)
            else:
                header = self.format_header(headers[idx])
                resp[header.lower()] = self.format_value(header, str(values[idx]['data']))
        if not list_output:
            list_output.append(resp)
        return list_output

    def format_header(self, header):
        header = re.sub(r'[^a-zA-Z0-9\s-]', '', header).strip()
        while header[0].isdigit():
            header = re.sub('^[0-9]', '', header).strip()
        header = re.sub(r'[\s-]+', '_', header)
        header = header.rstrip('_')
        return header

    def format_value(self, header, value):
        value = self.util.extract_month_year(value) if 'months_in_date' == header.lower() else self.util.extract_date(
            value)
        value = '0' if value == 'N\\A' else value
        value = self.util.round_off(value)
        return value

    def assert_response_status_code(self, status_code):
        assert status_code == 200

    def get_widget_jaql_endpoint(self, dashboard_id, widget_id):
        return self.auth.get_base_url() + "dashboards/{0}/widgets/{1}".format(dashboard_id, widget_id)

    def get_endpoint(self, data_source):
        return self.auth.get_base_url() + "datasources/{0}/jaql".format(data_source)

    def frame_jaql(self, panels):
        jaql_list = []
        for panel in panels:
            for item in panel['items']:
                if ("disabled" in item and not item['disabled']) or ("disabled" not in item):
                    jaql_list.append({"jaql": item["jaql"]})
        return jaql_list
