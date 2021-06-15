import os

from src.utils.sisense_api_handler import SisenseApiHandler


def pytest_generate_tests(metafunc):
    argnames = []
    idlist = []
    argvalues = []
    for testdata in metafunc.cls.testdata:
        idlist.append(testdata[0])
        items = testdata[1].items()
        argnames = [x[0] for x in items]
        argvalues.append([x[1] for x in items])
    metafunc.parametrize(argnames, argvalues, ids=idlist, scope="class")


def pytest_html_report_title(report):
    report.title = "Sisense sanity test"


def pytest_html_results_table_html(report, data):
    if report.passed:
        del data[:]


def pytest_configure(config):
    if is_master(config):
        dashboard = os.getenv('DASHBOARD_NAME')
        SisenseApiHandler().build_cube(dashboard)


def is_master(config):
    """True if the code running the given pytest.config object is running in a xdist master
    node or not running xdist at all.
    """
    return not hasattr(config, 'slaveinput')
