#! ../env/bin/python
# -*- coding: utf-8 -*-

class TestURLs:
    def test_statistics_home(self, testapp):
        rv = testapp.get('/statistics')
        assert rv.status_code == 308

    def test_statistics_home_logged_in(self, testapp):
        rv = testapp.post('/login', data=dict(
            username='admin@test.de',
            password="test"
        ), follow_redirects=True)

        rv = testapp.get('/books/')
        assert 200 == rv.status_code