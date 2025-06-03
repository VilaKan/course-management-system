#! ../env/bin/python
# -*- coding: utf-8 -*-
from tests.conftest import login_as_admin, testapp

class TestURLs:
    def test_statistics_home(self, testapp):
        rv = testapp.get('/statistics')
        assert rv.status_code == 308

    def test_statistics_home_logged_in(self, testapp):
        login_as_admin(testapp)
        rv = testapp.get('/statistics/')
        assert 200 == rv.status_code