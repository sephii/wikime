import requests


class AuthenticationError(StandardError):
    pass


class ConfluenceSession(object):
    def __init__(self, hostname, auth):
        self.hostname = hostname

        self.session = requests.Session()
        self._authenticate(auth)

    def _authenticate(self, auth):
        response = self.session.post(
            'https://{0}/dologin.action'.format(self.hostname),
            data={
                'login': 'Log In',
                'os_destination': '/homepage.action',
                'os_username': auth[0],
                'os_password': auth[1],
            }, allow_redirects=False)

        if response.status_code != 302:
            raise AuthenticationError(response.headers['X-Seraph-LoginReason'])

    def get_page(self, url):
        return self.session.get(self.url)

    def get_pages_with_tag(self, host, tag):
        tags_page_url = 'https://{host}/label/{tag}/'.format({
            'host': host,
            'tag': tag,
        })
        page = self.get_page(tags_page_url)

    def add_tag_to_page(self, page_id, tag):
        self.session.post('https://{0}/add_label'.format(self.hostname))
