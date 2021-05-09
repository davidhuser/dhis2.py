from itertools import chain
from typing import Union, List, Generator, Callable


class PagerException(Exception):
    """Paging exceptions."""


class Pager:
    """Base pager class."""

    def __init__(
        self,
        *,
        get: Callable,
        endpoint: str,
        params: Union[dict, List[tuple]] = None,
        page_size: Union[int, str] = 50,
        merge: bool = False,
    ):
        try:
            if not isinstance(page_size, (str, int)) or int(page_size) < 1:
                raise ValueError
        except ValueError:
            raise PagerException("page_size must be > 1")

        params = {} if not params else params
        if "paging" in params:
            raise PagerException(
                "Can't set paging manually in `params` when using `get_paged`"
            )
        params["pageSize"] = page_size  # type: ignore
        params["page"] = 1  # type: ignore
        params["totalPages"] = True  # type: ignore

        self._get = get
        self._endpoint = endpoint
        self._params = params
        self._merge = merge

    def page_generator(self) -> Generator[dict, dict, None]:
        """This method should return a generator that allows page iteration."""

        raise NotImplementedError("Each Pager class should implement page_generator()")

    def merge(self):
        """This method should loop over the pages yielded by page_generator() and merge the results"""

        raise NotImplementedError("Each Pager class should implement merge()")

    def page(self) -> Union[Generator[dict, dict, None], dict]:
        """Returns the paginated results taking the merge option into account"""

        if not self._merge:
            return self.page_generator()
        else:
            return self.merge()


class CollectionPager(Pager):
    """Pager class for regular DHIS2 collections (data elements, indicators, etc...)"""

    def page_generator(self) -> Generator[dict, dict, None]:
        page = self._get(
            endpoint=self._endpoint, file_type="json", params=self._params
        ).json()
        page_count = page["pager"]["pageCount"]

        yield page

        while page["pager"]["page"] < page_count:
            self._params["page"] += 1  # type: ignore
            page = self._get(
                endpoint=self._endpoint, file_type="json", params=self._params
            ).json()
            yield page

    def merge(self):
        collection = self._endpoint.split("/")[
            0
        ]  # only use e.g. events when submitting events/query as endpoint
        data = []
        for p in self.page_generator():
            data.append(p[collection])
        return {collection: list(chain.from_iterable(data))}


class AnalyticsPager(Pager):
    """Pager class for the analytics endpoint (data elements, indicators, etc...)"""

    def page_generator(self) -> Generator[dict, dict, None]:
        page = self._get(
            endpoint=self._endpoint, file_type="json", params=self._params
        ).json()
        page_count = page["metaData"]["pager"]["pageCount"]

        yield page

        while page["metaData"]["pager"]["page"] < page_count:
            self._params["page"] += 1  # type: ignore
            page = self._get(
                endpoint=self._endpoint, file_type="json", params=self._params
            ).json()
            yield page

    def merge(self):
        data = []
        for p in self.page_generator():
            data.append(p["rows"])

        return {"rows": list(chain.from_iterable(data))}
