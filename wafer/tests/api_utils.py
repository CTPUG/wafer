"""Utilities for testing wafer APIs."""

from rest_framework.test import APIClient


class SortedResultsClient(APIClient):
    """ A client that sorts API results to make comparisons easier.
    """
    def __init__(self, *args, **kw):
        self._sort_key = kw.pop('sort_key')
        super(SortedResultsClient, self).__init__(*args, **kw)

    def _sorted_response(self, response):
        def get_key(item):
            return item[self._sort_key]
        if response.data and 'results' in response.data:
            response.data['results'].sort(key=get_key)
        return response

    def generic(self, *args, **kw):
        response = super(SortedResultsClient, self).generic(*args, **kw)
        return self._sorted_response(response)
