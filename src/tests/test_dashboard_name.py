from src.utils.utilities import Utilities

comparator_obj = Utilities().init_test_data('dashboard_name')


class TestDashboard:
    testdata = comparator_obj

    def test_widget(self, attribute):
        attribute.compare('widget_name')
