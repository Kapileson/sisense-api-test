import os

from google.cloud import bigquery

from src.utils.utilities import Utilities


class BigQueryHandler:
    date_range = [os.getenv('START_DATE'), os.getenv('END_DATE')]
    client = bigquery.Client()
    test_data = {}

    def construct_test_data(self, test_data):
        test_data_dict = {}
        for k, v in test_data.items():
            for qry_param_nm in v['QueryParamNm']:
                test_data_dict[qry_param_nm] = {'Values': v['Values'], 'ParamCond': v['ParamCond'], 'Type': v['Type']}
        self.test_data = test_data_dict

    def construct_test_data_with_applicable_filters(self, test_data, query_name, applicable_filters):
        test_data_dict = {}
        for k, v in test_data.items():
            if k in applicable_filters[query_name]:
                for qry_param_nm in v['QueryParamNm']:
                    test_data_dict[qry_param_nm] = {'Values': v['Values'], 'ParamCond': v['ParamCond'], 'Type': v['Type']}
        self.test_data = test_data_dict

    def execute(self, query, append_test_data=True):
        if append_test_data:
            query = self.construct_query(query)
        headers = []
        list_output = []
        query_job = self.client.query(query)
        for row in   query_job:
            if len(headers) == 0:
                headers = [f for f in row.keys()]
            result = {}
            if len(headers) > 1:
                for header in headers:
                    result[header.lower()] = BigQueryHandler.format_value(row[header])
            else:
                header = headers[0]
                result[header.lower()] = BigQueryHandler.format_value(row[header])
            list_output.append(result)
        return list_output

    # Construct a query with where conditions
    def construct_query(self, query):
        cond_lst = [self.construct_query_condition(self.test_data)]
        query = query.replace('where', '') if cond_lst[0] == '' else query
        return query.format(*cond_lst)

    @staticmethod
    def construct_query_condition(test_data):
        mul_cond = ''
        for k, v in test_data.items():
            values = v['Values']
            if 'all' not in values and '' != values[0].strip():
                param_cond = v['ParamCond']
                if param_cond == 'in':
                    if v['Type'] == 'integer':
                        cond = k + " in(" + "','".join(values).strip() + ")"
                    else:
                        cond = k + " in('" + "','".join(values).strip() + "')"
                elif param_cond == 'between':
                    cond = k + ' between ' + values[0].replace('-', '') + ' and ' \
                           + values[1].replace('-', '')
                else:
                    cond = k + " " + param_cond + values[0]
                mul_cond += " and " + cond if mul_cond != '' else cond
        return mul_cond

    @staticmethod
    def format_value(value):
        value = Utilities.change_none_to_zero(str(value))
        value = Utilities.round_off(value)
        return value

    @staticmethod
    def formatted_query(file_path):
        query = open(file_path, 'r').read()
        return " ".join([s.strip() for s in query.splitlines()])
