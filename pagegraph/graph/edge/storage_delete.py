from __future__ import annotations

from typing import Optional
from pagegraph.graph.edge import Edge

from pagegraph.graph.edge.abc.storage_call import StorageCallEdge


class StorageDeleteEdge(StorageCallEdge):
    summary_methods = {
        "key": "key",
        "is ad context": "is_ad",
    }
    def as_storage_delete_edge(self) -> Optional[StorageDeleteEdge]:
        return self

    def key(self) -> str:
        return self.data()[self.RawAttrs.KEY.value]
    
    def is_ad(self) -> bool:
        return self.data().get(Edge.RawAttrs.IS_AD.value, False)
