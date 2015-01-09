from werkzeug.utils import parse_cookie


class FlaskTestCaseMixin(object):
    """
    The FlaskTestCaseMixin replicates some of the testing methods available in
    the ``TestCase`` class from ``flask.ext.testing``, as we want to be able to
    access the Flask.Response object in some cases.
    """

    def _request(self, method, *args, **kwargs):
        """
        Execute HTTP method with provided args and kwargs. ``content_type`` is
        set to "application/json" by default, as the API expects JSON in most
        requests. Also, the test cases should follow redirects by default.

        :param method: HTTP method to use (i.e. 'get', 'post', 'put', etc.)
        :return:
        """
        kwargs.setdefault('content_type', 'application/json')
        kwargs.setdefault('follow_redirects', True)
        return method(*args, **kwargs)

    def get(self, *args, **kwargs):
        return self._request(self.client.get, *args, **kwargs)

    def post(self, *args, **kwargs):
        return self._request(self.client.post, *args, **kwargs)

    def put(self, *args, **kwargs):
        return self._request(self.client.put, *args, **kwargs)

    def delete(self, *args, **kwargs):
        return self._request(self.client.delete, *args, **kwargs)

    def get_cookies(self, response):
        """
        Parse cookies from Flask Response.

        :param response:
        :return: dict with cookie values
        """
        cookies = {}
        for value in response.headers.get_all('Set-Cookie'):
            cookies.update(parse_cookie(value))
        return cookies

    def assert_status_code(self, response, status_code):
        """
        Assert status code of a Flask test client response

        :param response: test client response object
        :param status_code: expected status code
        :return: Flask.Response
        """
        self.assertEquals(status_code, response.status_code)
        return response

    def assert_content_type(self, response, content_type):
        """
        Assert the content-type of a Flask test client response

        :param response: The test client response object
        :param content_type: The expected content type
        :return: Flask.Response
        """
        self.assertEquals(content_type, response.headers.get('Content-Type'))
        return response

    def assert_ok(self, response):
        return self.assert_status_code(response, 200)

    def assert_bad_request(self, response):
        return self.assert_status_code(response, 400)

    def assert_unauthorized(self, response):
        return self.assert_status_code(response, 401)

    def assert_forbidden(self, response):
        return self.assert_status_code(response, 403)

    def assert_not_found(self, response):
        return self.assert_status_code(response, 404)

    def assert_json(self, response):
        """
        JSON response
        :param response: Flask.Response
        :return: Flask.Response
        """
        return self.assert_content_type(response, 'application/json')

    def assert_ok_html(self, response):
        """
        200 OK HTML response
        :param response: Flask.Response
        :return: Flask.Response
        """
        return self.assert_ok(
            self.assert_content_type(response, 'text/html; charset=utf-8')
        )

    def assert_ok_json(self, response):
        """
        200 OK JSON response
        :param response: Flask.Response
        :return: Flask.Response
        """
        return self.assert_ok(self.assert_json(response))

    def assert_bad_request_json(self, response):
        """
        Assert 400 Bad Request JSON response
        :param response: Flask.Response
        :return: Flask.Response
        """
        return self.assert_bad_request(self.assert_json(response))

    def assert_cookie(self, response, name):
        """
        Assert that the response contains a cookie with the specified name
        :param response: Flask.Response
        :param name: name of the cookie
        :return: Flask.Response
        """
        self.assertIn(name, self.get_cookies(response))
        return response

    def assert_cookie_equals(self, response, name, value):
        """
        Asserts that the response contains a cookie with the specified value
        :param response: Flask.Response
        :param name: name of the cookie
        :param value: value of the cookie
        :return: Flask.Response
        """
        self.assertEquals(value, self.get_cookies(response).get(name, None))
        return response
