from bs4 import BeautifulSoup
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
        return self.session.get(url)

    def get_pages_with_tag(self, tag):
        """
        TODO handle paginated results page
        """
        tags_page_url = 'https://{hostname}/label/{tag}'.format(
            hostname=self.hostname,
            tag=tag,
        )
        page = self.get_page(tags_page_url)
        links_list = {}

        if (page.status_code == 200 and
                page.headers['content-type'].startswith('text/html;')):
            bs = BeautifulSoup(page.text)
            rows = bs.select('div.labels table.tableview tr td')

            for row in rows:
                link = row.find('a')

                if link:
                    links_list[link['href']] = link.text

        return links_list

    def add_tag_to_page(self, page_id, tag):
        self.session.post('https://{0}/add_label'.format(self.hostname))
