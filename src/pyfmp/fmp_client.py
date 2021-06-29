import requests
import cachetools
import ratelimit
import pandas as pd
from urllib.parse import urljoin
import os
import urllib3



class FMPClient:

    BASE_URL = 'https://financialmodelingprep.com/api/v3'# {{{
    PROFILE_URL = BASE_URL + '/profile/'
    SYMBOL_LIST_URL = BASE_URL + '/stock/list'
    ETF_LIST_URL = BASE_URL  + '/etf/list'
    TRADEABLE_SYMBOL_LIST_URL = BASE_URL + '/available-traded/list'
    V4_BASE_URL = 'https://financialmodelingprep.com/api/v4'
    # }}}

    def __init__(self, api_key=None, **kwargs):# {{{
        self.api_key = api_key
        self.kwargs = kwargs# }}}

    def connect(self):# {{{
        """Start the API session with the API keys"""

        headers = {'Content-Type': 'Application/json'}

        if ('FMP_API_KEY' in os.environ.keys()) and (self.api_key is None):
            self.api_key = os.environ['FMP_API_KEY']



        retries = urllib3.util.retry.Retry(total=5,
                backoff_factor=1,
                status_forcelist=[429, 500, 503, 502, 413, 504])

        ada = requests.adapters.HTTPAdapter(max_retries=retries)
        self.session = requests.Session(**self.kwargs)
        self.session.mount('https://', ada)
        self.session.headers.update(headers)

        if self.api_key is not None:
            self.session.params.update({'apikey': self.api_key})

        assert_status_hook = lambda response, *args, **kwargs: response.raise_for_status()
        self.session.hooks["response"] = [assert_status_hook]# }}}

    def disconnect(self):# {{{
        self.session.close()# }}}

    def _divide_chunks(self, l, n):# {{{
        # looping till length l
        for i in range(0, len(l), n): 
            yield l[i:i + n]# }}}

    @ratelimit.sleep_and_retry# {{{
    @ratelimit.limits(calls=10, period=1)
    def _request(self, *args, **kwargs):

        request = self.session.get(*args, **kwargs)

        request.raise_for_status()

        return request.json()# }}}

    def get_symbol_list(self):# {{{

        res1 = self._request(self.SYMBOL_LIST_URL)
        res2 = self._request(self.ETF_LIST_URL)
        res3 = self._request(self.TRADEABLE_SYMBOL_LIST_URL)

        df1 = pd.DataFrame(res1)
        df1['source'] = 'SYMBOL_LIST'
        df2 = pd.DataFrame(res2)
        df2['source'] = 'ETF_LIST'
        df3 = pd.DataFrame(res3)
        df3['source'] = 'TRADEABLE'

        dfs = pd.concat([df1, df2, df3])

        dfs = dfs.drop_duplicates(subset=['symbol'])

        return dfs# }}}

    def _request_chunks(self, url, iterable, size=1000):# {{{
        """will split up an iterable into a list and then perform the 
        relevant queries using self._request"""

        chunks = self._divide_chunks(iterable, size)

        results = []

        for chunk in chunks:

            li_chunk = ','.join(chunk)
            tmp = self._request(url + li_chunk)

            results.extend(tmp)

        return results# }}}

    def get_profile(self, stocks):# {{{

        if isinstance(stocks, str):
            stocks = [stocks]

        results = self._request_chunks(self.PROFILE_URL, stocks, size=500)

        return results# }}}


