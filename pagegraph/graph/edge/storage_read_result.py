from __future__ import annotations

from typing import Optional

from pagegraph.graph.edge import Edge
from pagegraph.graph.edge.abc.frame_id_attributed import FrameIdAttributedEdge


class StorageReadResultEdge(FrameIdAttributedEdge):
    summary_methods = {
        "value": "value",
        "is ad context": "is_ad",
    }
    def as_storage_read_result_edge(self) -> Optional[StorageReadResultEdge]:
        return self

    def value(self) -> str:
        return self.data()[Edge.RawAttrs.VALUE.value]
    
    def is_ad(self) -> bool:
        return self.data().get(Edge.RawAttrs.IS_AD.value, False)
