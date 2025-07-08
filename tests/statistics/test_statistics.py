#! ../env/bin/python
# -*- coding: utf-8 -*-
from tests.conftest import login_as_admin, testapp


# For all the statistics tests the following things apply:
# - We need to be logged in as admin, since the statistics are an admin only function
# - We need to first visit the statistics page itself, since we are setting two variables to their inital values there (yam_valid and year_only_valid)
# - We capture the session to assert the values are correct
class TestStatistics:
    def test_generate_year_and_month_invalid(self, testapp):
        login_as_admin(testapp)
        testapp.get('/statistics/')
        testapp.post('/statistics/generate_year_and_month', data={
            'yearSelect': '2024',
            'monthSelect': '01',
            'yearOnly': 2024
        }, follow_redirects=True)

        with testapp.session_transaction() as sess:
            assert sess.get('yam_valid') == False
            assert sess.get('year_only_valid') == False

    def test_generate_year_and_month_valid(self, testapp):
        login_as_admin(testapp)
        testapp.get('/statistics/')
        testapp.post('/statistics/generate_year_and_month', data={
            'yearSelect': '2025',
            'monthSelect': '01',
            'yearOnly': 2024
        }, follow_redirects=True)

        with testapp.session_transaction() as sess:
            assert sess.get('yam_valid') == True
            assert sess.get('year_only_valid') == False

    def test_generate_year_only_invalid(self, testapp):
        login_as_admin(testapp)
        testapp.get('/statistics/')
        testapp.post('/statistics/generate_year_only', data={
            'yearSelect': '2024',
            'monthSelect': '01',
            'yearOnly': 2024
        }, follow_redirects=True)

        with testapp.session_transaction() as sess:
            assert sess.get('year_only_valid') == False
            assert sess.get('yam_valid') == False

    def test_generate_year_only_valid(self, testapp):
        login_as_admin(testapp)
        testapp.get('/statistics/')
        testapp.post('/statistics/generate_year_only', data={
            'yearSelect': '2024',
            'monthSelect': '01',
            'yearOnly': 2025
        }, follow_redirects=True)

        with testapp.session_transaction() as sess:
            assert sess.get('year_only_valid') == True
            assert sess.get('yam_valid') == False

