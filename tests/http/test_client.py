import unittest
from unittest import mock
from unittest import TestCase
from typing import NamedTuple
import json

from python_stuff.http.client import (
    recreate_url,
    HttpClient,
    HttpResponse,
    Pagination,
)


class TestPagination(TestCase):
    def setUp(self):
        self.http_client = mock.Mock()
        self.endpoint = "endpoint"
        self.never_stops = lambda x: False

    def test_iter_upper_bound(self) -> None:
        upper_bound = 10
        pag = Pagination(
            self.http_client,
            "page",
            stop_condition_func=self.never_stops,
            upper_bound=upper_bound,
        )

        count = 0
        gen = pag.iter(self.endpoint)
        for data in gen:
            count += 1

        self.assertEqual(count, upper_bound)

    def test_stop_condition(self) -> None:
        expected_http_client_get_calls = [
            mock.call(url="endpoint", params=[("page", "1")]),
            mock.call(url="endpoint", params=[("page", "2")]),
            mock.call(url="endpoint", params=[("page", "3")]),
        ]

        return_values = [False, False, True]
        stop_condition = mock.Mock(side_effect=return_values)

        pag = Pagination(self.http_client, "page", stop_condition_func=stop_condition)

        count = 0
        gen = pag.iter(self.endpoint)
        for data in gen:
            count += 1

        self.assertListEqual(
            self.http_client.get.call_args_list, expected_http_client_get_calls
        )
        self.assertEqual(count, len(return_values))


class TestHttpResponse(TestCase):
    def setUp(self) -> None:
        self.expected_bytes = json.dumps({"fake_data": "found gold"}).encode()

        self.response = mock.Mock()
        self.response.read.return_value = self.expected_bytes

    def test_bytes(self) -> None:
        http_response = HttpResponse(self.response, mock.Mock())
        self.assertEqual(http_response.bytes, self.expected_bytes)

        # Ensuring that the `read` method was called once (bytes is cached)
        http_response.bytes
        self.response.read.assert_called_once()

    def test_json(self) -> None:
        http_response = HttpResponse(self.response, mock.Mock())
        self.assertDictEqual(
            http_response.json(), json.loads(self.expected_bytes.decode())
        )


class TestHttpClient(TestCase):
    def setUp(self):
        self.base_headers = {"test-header-1": "header_1", "test-header-2": "header_2"}
        self.base_params = [("param1", "one"), ("param2", "two")]
        self.base_uri = "http://unittest.org"
        self.extra_params = [("param3", "three"), ("param4", "four")]
        self.extra_headers = {"test-header-1": "new_value", "test-header-3": "header_3"}
        self.all_headers = {}
        self.all_headers.update(self.base_headers)
        self.all_headers.update(self.extra_headers)

    def test_get(self) -> None:
        class Case(NamedTuple):
            base_headers: dict[str, str] | None
            base_params: list[tuple[str, str]] | None
            base_uri: str | None
            url: str
            params: list[tuple[str, str]] | None
            headers: dict[str, str] | None
            use_base_uri: bool
            expected_full_url: str
            expected_headers: dict[str, str]

        cases = [
            Case(
                base_headers=None,
                base_params=None,
                base_uri=self.base_uri,
                url="example",
                params=self.extra_params,
                headers=None,
                use_base_uri=True,
                expected_full_url="http://unittest.org/example?param3=three&param4=four",
                expected_headers={},
            ),
            Case(
                base_headers=None,
                base_params=None,
                base_uri=self.base_uri,
                url="http://unittest.org/example",
                params=self.extra_params,
                headers=None,
                use_base_uri=False,
                expected_full_url="http://unittest.org/example?param3=three&param4=four",
                expected_headers={},
            ),
            Case(
                base_headers=self.base_headers,
                base_params=self.base_params,
                base_uri=self.base_uri,
                url="/example",
                params=self.extra_params,
                headers=None,
                use_base_uri=True,
                expected_full_url="http://unittest.org/example?param1=one&param2=two&param3=three&param4=four",
                expected_headers={
                    k.capitalize(): v for k, v in self.base_headers.items()
                },
            ),
            Case(
                base_headers=self.base_headers,
                base_params=self.base_params,
                base_uri=None,
                url="http://unittest.org/example",
                params=self.extra_params,
                headers=None,
                use_base_uri=True,
                expected_full_url="http://unittest.org/example?param1=one&param2=two&param3=three&param4=four",
                expected_headers={
                    k.capitalize(): v for k, v in self.base_headers.items()
                },
            ),
            Case(
                base_headers=self.base_headers,
                base_params=self.base_params,
                base_uri=None,
                url="http://unittest.org/example",
                params=self.extra_params,
                headers=self.extra_headers,
                use_base_uri=True,
                expected_full_url="http://unittest.org/example?param1=one&param2=two&param3=three&param4=four",
                expected_headers={
                    k.capitalize(): v for k, v in self.all_headers.items()
                },
            ),
        ]

        for case_num, case in enumerate(cases, start=1):
            with self.subTest(f"Case ({case_num})"):
                client = HttpClient(
                    headers=case.base_headers,
                    params=case.base_params,
                    base_uri=case.base_uri,
                )
                with mock.patch(
                    "python_stuff.http.client.urllib.request.urlopen"
                ) as mock_urlopen:
                    _ = client.get(
                        url=case.url,
                        params=case.params,
                        headers=case.headers,
                        use_base_uri=case.use_base_uri,
                    )
                    mock_urlopen
                    req = mock_urlopen.call_args[0][0]
                    self.assertEqual(req.get_full_url(), case.expected_full_url)
                    self.assertDictEqual(req.headers, case.expected_headers)


class TestCreateUrl(TestCase):
    def test_recreate_url(self) -> None:
        class Case(NamedTuple):
            url: str
            params: list[tuple[str, str]] | None
            add_path: str | None
            expected: str

        cases = [
            Case(
                "https://api.repo.nypl.org/api/v2/items/search?q=cats&publicDomainOnly=true",
                None,
                None,
                "https://api.repo.nypl.org/api/v2/items/search?q=cats&publicDomainOnly=true",
            ),
            Case(
                "https://api.repo.nypl.org/api/v2/items/search",
                [("q", "cats"), ("publicDomainOnly", "true")],
                None,
                "https://api.repo.nypl.org/api/v2/items/search?q=cats&publicDomainOnly=true",
            ),
            Case(
                "https://api.repo.nypl.org/api/v2/items/search?q=cats",
                [("publicDomainOnly", "true")],
                None,
                "https://api.repo.nypl.org/api/v2/items/search?q=cats&publicDomainOnly=true",
            ),
            Case(
                "https://api.repo.nypl.org/api/v2",
                [("q", "cats"), ("publicDomainOnly", "true")],
                "/items/search",
                "https://api.repo.nypl.org/api/v2/items/search?q=cats&publicDomainOnly=true",
            ),
            Case(
                "https://api.repo.nypl.org/api/v2/",
                [("q", "cats"), ("publicDomainOnly", "true")],
                "/items/search",
                "https://api.repo.nypl.org/api/v2/items/search?q=cats&publicDomainOnly=true",
            ),
            Case(
                "https://api.repo.nypl.org/api/v2",
                [("q", "cats"), ("publicDomainOnly", "true")],
                "items/search",
                "https://api.repo.nypl.org/api/v2/items/search?q=cats&publicDomainOnly=true",
            ),
        ]

        for case_num, case in enumerate(cases, start=1):
            with self.subTest(f"Case({case_num})"):
                result = recreate_url(case.url, case.params, case.add_path)
                self.assertEqual(result, case.expected)


if __name__ == "__main__":
    unittest.main()
