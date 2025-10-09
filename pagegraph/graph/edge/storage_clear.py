from __future__ import annotations

from typing import Optional
from pagegraph.graph.edge import Edge

from pagegraph.graph.edge.abc.storage_call import StorageCallEdge


class StorageClearEdge(StorageCallEdge):
    summary_methods = {
        "is ad context": "is_ad",
    }

    def as_storage_clear_edge(self) -> Optional[StorageClearEdge]:
        return self
    
    def is_ad(self) -> bool:
        return self.data().get(Edge.RawAttrs.IS_AD.value, False)
