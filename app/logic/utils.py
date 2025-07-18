from typing import Iterable

from prometheus_client.samples import Sample


def assert_samples_consistent(samples: Iterable[Sample]):
    """
    断言所有 Sample 的 name 和 timestamp 都一致，否则抛出 ValueError。
    """
    first_name = ""
    for idx, s in enumerate(samples):
        if idx == 0:
            first_name = s.name
        else:
            if s.name != first_name:
                raise ValueError("All samples must have the same name.")
        yield s
