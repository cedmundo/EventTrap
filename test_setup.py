import unittest

from settings import settings

old_test_run = unittest.result.TestResult.startTestRun


def start_test_run(self):
    assert "test" in settings.database_name, "Database does not contain the name 'test' which should do"
    old_test_run(self)


unittest.result.TestResult.startTestRun = start_test_run
