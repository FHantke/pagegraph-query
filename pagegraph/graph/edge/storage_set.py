from __future__ import annotations

from typing import Optional

from pagegraph.graph.edge import Edge
from pagegraph.graph.edge.abc.storage_call import StorageCallEdge


class StorageSetEdge(StorageCallEdge):
    summary_methods = {
        "key": "key",
        "value": "value",
        "is ad context": "is_ad",
    }

    def as_storage_set_dge(self) -> Optional[StorageSetEdge]:
        return self

    def key(self) -> str:
        return self.data()[Edge.RawAttrs.KEY.value]

    def value(self) -> str:
        return self.data()[Edge.RawAttrs.VALUE.value]
    
    def is_ad(self) -> bool:
        return self.data().get(Edge.RawAttrs.IS_AD.value, False)
