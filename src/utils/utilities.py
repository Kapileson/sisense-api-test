from datetime import datetime
import json
import os
from os import listdir
from os.path import isfile, join

from src.utils import gcs_handler


class Utilities:
    resources_root_path = 'resources/'
    sis_date_format = '%Y-%m-%dT%H:%M:%S'
    environment = os.getenv('ENVIRONMENT').lower()
    url = json.load(open("resources/environment.json"))[environment]

    @staticmethod
    def get_list_of_all_files(folder_name):
        files = [f for f in listdir(folder_name) if isfile(join(folder_name, f))]
        return files

    @staticmethod
    def get_file_lines(path):
        file = open(path, 'r')
        text = file.read().splitlines()
        lines = [f for f in text if f.strip() != '']
        return lines

    @staticmethod
    def round_off(data):
        try:
            flt_val = float(data)
            flt_val = 0 if flt_val == -0.0 else flt_val
            return str(round(float(f'{flt_val:f}'), 2))
        except ValueError:
            return data

    @staticmethod
    def change_none_to_zero(value):
        value = str(value)
        return '0' if value is None or value == 'None' else value

    @staticmethod
    def divide_numbers(num1, num2):
        numerator = Utilities.change_none_to_zero(num1)
        denominator = Utilities.change_none_to_zero(num2)
        return Utilities.round_off(str(float(numerator) / float(denominator))) \
            if denominator not in ['0', '0.0'] else '0.0'

    @staticmethod
    def replace_all(char_list, replace_char, text):
        for char in char_list:
            text = text.replace(char, replace_char)
        return text

    @staticmethod
    def replace_list_of_text(search_list, replace_list, text):
        for search_text, replace_text in zip(search_list, replace_list):
            text = text.replace(str(search_text), str(replace_text))
        return text

    def extract_date(self, text):
        try:
            date = datetime.strptime(text, self.sis_date_format)
            return date.strftime('%d/%m/%Y')
        except ValueError:
            return text

    def extract_month_year(self, text):
        try:
            date = datetime.strptime(text, self.sis_date_format)
            return str(date.month) + '/' + str(date.year)
        except ValueError:
            return text

    def extract_month(self, text):
        try:
            date = datetime.strptime(text, self.sis_date_format)
            return str(date.month)
        except ValueError:
            return text

    @staticmethod
    def read_file_as_json(folder_name, dashboard, widget):
        with open(folder_name + "/" + dashboard + "/" + widget, 'r') as data_file:
            json_object = json.load(data_file)
        return json_object

    @staticmethod
    def get_test_data(dashboard):
        return json.loads(gcs_handler.get_test_data_from_gcs('bucket_name', dashboard + '.json'))

    @staticmethod
    def get_dashboards():
        dashboards = os.getenv('DASHBOARD_NAME').split(',')
        if len(dashboards) == 0:
            raise RuntimeError("Env Variable[DASHBOARD_NAME] empty!")
        return dashboards

    @staticmethod
    def get_dim_mapping(dashboard):
        return json.load(open(Utilities.resources_root_path + dashboard + '/mappings/dim.json'))

    @staticmethod
    def get_widgets_id_mapping(dashboard):
        widgets_id = json.load(open(Utilities.resources_root_path + dashboard + '/mappings/widgets_id.json'))
        return widgets_id[Utilities.environment]

    @staticmethod
    def get_applicable_filters_mapping(dashboard):
        return json.load(open(Utilities.resources_root_path + dashboard + '/mappings/applicable_filters.json', 'r'))

    def init_test_data(self, dashboard):
        test_data_lst = self.get_test_data(dashboard)
        data_source = test_data_lst[0]['Data Source']
        test_data_objects = []

        for index in range(1, len(test_data_lst)):
            from src.utils.comparator import Comparator
            comparator_object = Comparator(data_source, dashboard, test_data_lst[index])
            test_data_objects.append((dashboard + "[Test_Data_Set " + str(index) + "]",
                                      {"attribute": comparator_object}))
        return test_data_objects
