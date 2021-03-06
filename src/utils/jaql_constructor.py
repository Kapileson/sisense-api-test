import json

from src.utils.sisense_api_handler import SisenseApiHandler
from src.utils.utilities import Utilities


class JaqlConstructor:

    def __init__(self, dashboard):
        self.util = Utilities()
        self.widget_jaql = {}
        self.dim = self.util.get_dim_mapping(dashboard)

    @staticmethod
    def construct_test_data(test_data):
        test_data_dict = {}
        for k, v in test_data.items():
            test_data_dict[k] = {'Values': v['Values'], 'FilterCond': v['FilterCond']}
        return test_data_dict

    @staticmethod
    def construct_test_data_with_applicable_filters(test_data, query_name, applicable_filters):
        test_data_dict = {}
        for k, v in test_data.items():
            if k in applicable_filters[query_name]:
                test_data_dict[k] = {'Values': v['Values'], 'FilterCond': v['FilterCond']}
        return test_data_dict

    def add_filter(self, filter_name, values):
        filter_json = json.load(open("resources/filter_template.json", 'r'))
        if 'date' in filter_name.lower():
            filter_json['jaql']['level'] = 'days'
            filter_json['jaql']['firstday'] = 'mon'
        (table, column) = self.dim[filter_name].split('.')
        filter_json['jaql']['table'] = table
        filter_json['jaql']['column'] = column
        filter_json['jaql']['dim'] = "[{0}]".format(self.dim[filter_name])

        test_data = values['Values']
        filter_cond = values['FilterCond']
        if len(filter_cond) > 1:
            if 'all' not in test_data and '' != test_data[0].strip():
                for i in range(len(filter_cond)):
                    filter_json['jaql']['filter'][filter_cond[i]] = test_data[i]
            else:
                filter_json['jaql']['filter']['all'] = 'true'
        else:
            if 'all' not in test_data and '' != test_data[0].strip():
                if len(test_data) > 1:
                    filter_json['jaql']['filter'][filter_cond[0]] = test_data
                else:
                    filter_json['jaql']['filter'][filter_cond[0]] = test_data[0]
            else:
                filter_json['jaql']['filter']['all'] = 'true'
        self.widget_jaql['metadata'].append(filter_json)

    def construct_jaql(self, widgets_id, widget, test_data, query_name, applicable_filters):
        self.get_widget_jaql(widgets_id, widget)
        if query_name is not None:
            constructed_test_data = self.construct_test_data_with_applicable_filters(test_data, query_name,
                                                                                     applicable_filters)
        else:
            constructed_test_data = self.construct_test_data(test_data)
        for k, v in constructed_test_data.items():
            self.add_filter(k, v)
        return self.widget_jaql

    def get_widget_jaql(self, widgets_id, widget):
        self.widget_jaql = SisenseApiHandler().get(widgets_id['dashboard_id'], widgets_id[widget])
