import urllib.parse
import urllib.request
from copy import deepcopy
import http
from typing import cast, Callable
import json
from collections.abc import Iterator


def recreate_url(
    url: str, params: list[tuple[str, str]] | None = None, add_path: str | None = None
) -> str:
    url_data = urllib.parse.urlsplit(url)
    scheme = url_data.scheme
    netloc = url_data.netloc
    path = url_data.path
    query = url_data.query
    fragment = url_data.fragment

    if params:
        list_query_str = urllib.parse.parse_qsl(query)
        list_query_str += params

        query = urllib.parse.urlencode(list_query_str)

    if add_path:
        path_parts = path.split("/")
        path_parts += add_path.split("/")
        path = "/".join([part for part in path_parts if part])

    result = urllib.parse.urlunsplit((scheme, netloc, path, query, fragment))
    return result


class HttpResponse:
    def __init__(
        self, response: http.client.HTTPResponse, request: urllib.request.Request
    ):
        self.response = response
        self.request = request
        self._bytes: bytes | None = None

    @property
    def bytes(self) -> bytes | None:
        if self._bytes:
            return self._bytes
        else:
            self._bytes = self.response.read()

        return self.bytes

    def json(self) -> dict:
        if self.bytes is None:
            raise Exception("self.bytes is None")
        return json.loads(self.bytes.decode())


class HttpClient:
    def __init__(
        self,
        headers: dict[str, str] | None = None,
        params: list[tuple[str, str]] | None = None,
        base_uri: str | None = None,
    ):
        self.headers = headers
        self.params = params
        self.base_uri = base_uri
        self.base_url = (
            recreate_url(url=self.base_uri, params=self.params)
            if self.base_uri
            else self.base_uri
        )

    def get(
        self,
        url: str,
        params: list[tuple[str, str]] | None = None,
        headers: dict[str, str] | None = None,
        use_base_uri: bool = True,
    ) -> HttpResponse:
        """
        If the `base_uri` is set, then `url` is treated as url path to be added to
        the base_uri.
        """
        if use_base_uri and self.base_uri:
            self.base_url = cast(str, self.base_url)
            url = recreate_url(url=self.base_url, add_path=url, params=params)
        else:
            if self.params:
                # make the url with the base params first, then make the final url
                url = recreate_url(url, params=self.params)
            url = recreate_url(url=url, params=params)

        if self.headers and headers:
            base_headers = deepcopy(self.headers)
            base_headers.update(headers)
            headers = base_headers
        elif self.headers and not headers:
            headers = deepcopy(self.headers)

        req = urllib.request.Request(url, headers=headers if headers else {})
        response = urllib.request.urlopen(req)

        return HttpResponse(response, req)


class Pagination:
    """
    This class creates an generator over the HttpClient where, on each iteration,
    we update the params to the get call to point to the next page.

    With regards to stopping, this code depends on the stop_condition_func
    that is passed in. It accepts the response json payload as an argument and,
    when it returns True, we break out of the infinite loop.

    As a safety net, please set the parameter `upper_bound`. It will put an limit on
    how many time the loop will run.

    """

    def __init__(
        self,
        http_client: HttpClient,
        page_url_param: str,
        stop_condition_func: Callable[[dict], bool],
        starting_page: int = 1,
        upper_bound: int | None = None,
    ):
        self.http_client = http_client
        self.page_url_param = page_url_param
        self.stop_condition_func = stop_condition_func
        self.starting_page = starting_page
        self.upper_bound = upper_bound

    def iter(self, endpoint: str) -> Iterator[dict]:
        current_page = self.starting_page
        count = 1
        while True:
            params = [(self.page_url_param, str(current_page))]
            response = self.http_client.get(url=endpoint, params=params)
            data = response.json()

            yield data

            if self.stop_condition_func(data):
                break

            count += 1
            if self.upper_bound and count > self.upper_bound:
                break

            current_page += 1
