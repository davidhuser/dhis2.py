import pytest
import responses

from dhis2 import exceptions, Api
from .common import BASEURL, API_URL


@pytest.fixture  # BASE FIXTURE
def api():
    return Api(BASEURL, "admin", "district")


@pytest.mark.parametrize(
    "payload,threshold,expected",
    [
        (
            {"dataElements": [1, 2, 3, 4, 5, 6, 7, 8]},
            3,
            [
                {"dataElements": [1, 2, 3]},
                {"dataElements": [4, 5, 6]},
                {"dataElements": [7, 8]},
            ],
        ),
        (
            {"dataElements": [1, 2, 3, 4, 5, 6, 7, 8]},
            9,
            [{"dataElements": [1, 2, 3, 4, 5, 6, 7, 8]}],
        ),
    ],
)
@responses.activate
def test_post_partitioned(api, payload, threshold, expected):
    endpoint = "metadata"
    url = "{}/{}".format(API_URL, endpoint)
    for p in expected:
        responses.add(responses.POST, url, json=p, status=200)

    for index, p in enumerate(
        api.post_partitioned(endpoint=endpoint, json=payload, thresh=threshold)
    ):
        assert p.status_code == 200

    assert len(responses.calls) == len(expected)


@pytest.mark.parametrize(
    "payload_invalid",
    [
        {"dataElements": [1, 2, 3, 4, 5, 6, 7, 8], "organisationUnits": []},
        {"dataElements": []},
        ["dataElements", {}],
        None,
        3,
        dict(),  # stopIteration check, should raise because empty
    ],
)
def test_post_partitioned_invalid(api, payload_invalid):
    with pytest.raises(exceptions.ClientException):
        for _ in api.post_partitioned(endpoint="metadata", json=payload_invalid):
            continue


@pytest.mark.parametrize("threshold", [0, 1, 1.5, None, [], [3]])
def test_post_partitioned_threshold_invalid(api, threshold):
    payload = {"dataElements": [1, 2, 3]}
    with pytest.raises(exceptions.ClientException):
        for _ in api.post_partitioned(
            endpoint="metadata", json=payload, thresh=threshold
        ):
            continue
