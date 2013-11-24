from __future__ import print_function, unicode_literals

import argparse
import datetime
import os
import time

import requests

ACCESS_TOKEN = os.environ['USER_ACCESS_TOKEN']

parser = argparse.ArgumentParser()
parser.add_argument('dtstart')


def _filename_for_date(date):
    return 'data/{0}.json'.format(date.strftime("%Y%m%d"))


def _downloaded_for_date(date):
    return os.path.exists(_filename_for_date(date))


class Fetcher(object):

    def __init__(self, dtstart, api_root="https://api.moves-app.com/api/v1"):
        self.api_root = api_root
        self.dtstart = dtstart
        self._sess = requests.Session()
        self._sess.headers.update({
            'authorization': 'Bearer {0}'.format(ACCESS_TOKEN)})

    def run(self):
        # Don't download today's data, as it's probably not complete
        yday = datetime.datetime.utcnow() - datetime.timedelta(days=1)

        days = yday - self.dtstart

        if days.days >= 0:
            for i in range(days.days + 1):
                self.fetch(self.dtstart + datetime.timedelta(i))

    def fetch(self, date):
        url = "{root}/user/storyline/daily/{date}?trackPoints=true"
        if not _downloaded_for_date(date):
            # The API is currently limited to 60 requests a second
            time.sleep(1)
            resp = self._sess.get(url.format(root=self.api_root,
                                             date=date.strftime("%Y%m%d")))
            resp.raise_for_status()

            with open(_filename_for_date(date), 'wb') as fp:
                fp.write(resp.content)


def main():
    args = parser.parse_args()

    dtstart = datetime.datetime.strptime(args.dtstart, "%Y%m%d")
    fetcher = Fetcher(dtstart)

    fetcher.run()

if __name__ == '__main__':
    main()
