from src.utils.big_query_handler import BigQueryHandler
from src.utils.jaql_constructor import JaqlConstructor
from src.utils.sisense_api_handler import SisenseApiHandler
from src.utils.utilities import Utilities


class Comparator:

    def __init__(self, data_source, dashboard, test_data):
        self.data_source = data_source
        self.dashboard = dashboard
        self.test_data = test_data
        self.big_query = BigQueryHandler()
        self.util = Utilities()
        self.sisense = SisenseApiHandler()
        self.widgets_id = self.util.get_widgets_id_mapping(dashboard)
        self.applicable_filters = self.util.get_applicable_filters_mapping(dashboard)
        self.query_name = None

    def assert_equals(self, expected, actual_row, categories, header):
        actual = actual_row[header]
        category_val = [actual_row[f] for f in categories] if categories is not None else None
        assert actual == expected, \
            'Failed at Row ' + str(category_val) + ' Column [' + header + '] ' \
            '\n Expected [' + expected + '] & Actual [' + actual + ']'

    def get_sisense_data(self, widget):
        json_obj = JaqlConstructor(self.dashboard) \
            .construct_jaql(self.widgets_id, widget, self.test_data, self.query_name, self.applicable_filters)
        return self.sisense.post(self.data_source, json_obj)

    def get_big_query_data(self, widget):
        query = self.big_query.formatted_query('resources/' + self.dashboard + '/queries/' + widget + '.sql')
        if '->' in query:
            key_val = query.split('->', 1)
            self.query_name = key_val[0]
            query = key_val[1]
        if self.query_name is None:
            self.big_query.construct_test_data(self.test_data)
        else:
            self.big_query.construct_test_data_with_applicable_filters(self.test_data, self.query_name,
                                                                       self.applicable_filters)
        return self.big_query.execute(query)

    def compare(self, widget, categories=None):
        expected = self.get_big_query_data(widget)
        actual = self.get_sisense_data(widget)
        for exp_row in expected:
            act_row = self.get_matched_record(exp_row, actual, categories)
            for header in exp_row.keys():
                self.assert_equals(exp_row[header], act_row, categories, header)

    @staticmethod
    def get_matched_record(exp_row, actual, categories):
        if categories is not None and len(actual) > 1:
            flag = False
            for act_row in actual:
                for col in categories:
                    if act_row[col] == exp_row[col]:
                        flag = True
                    else:
                        flag = False
                        break
                if flag:
                    return act_row
            if not flag:
                assert False, 'Record [' + str(exp_row) + '] is not there in Sisense'
        else:
            return actual[0]
