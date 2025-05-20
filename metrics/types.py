from typing import TypeAlias, Iterable

from prometheus_client.samples import Sample

Samples: TypeAlias = Iterable[Sample]

GroupedSamples: TypeAlias = dict[str, Samples]
Label: TypeAlias = dict[str, str]
SamplesOfSameName: TypeAlias = dict[str, Samples]
