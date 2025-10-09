from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import pagegraph.commands
import pagegraph.graph
from pagegraph.graph.edge import Edge
from pagegraph.serialize import ReportBase

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Optional, Union

    from pagegraph.graph.node.dom_root import DOMRootNode
    from pagegraph.serialize import EdgeReport
    from pagegraph.types import PageGraphId


@dataclass
class Result(ReportBase):
    edge: EdgeReport

class Command(pagegraph.commands.Base):
    frame_nid: Optional[PageGraphId]
    edge_types: list[str] = None

    def __init__(self, input_path: Path, 
                 frame_nid: Optional[PageGraphId],
                 edge_types: Optional[list[str]],
                 debug: bool) -> None:
        self.frame_nid = frame_nid
        self.edge_types = edge_types
        super().__init__(input_path, debug)

    def validate(self) -> None:
        if self.frame_nid:
            pagegraph.commands.validate_node_id(self.frame_nid)
        return super().validate()

    def execute(self) -> pagegraph.commands.Result:
        pg = pagegraph.graph.from_path(self.input_path, self.debug)
        reports: list[Result] = []

        edge_types = [Edge.Types(e) for e in self.edge_types] if self.edge_types else Edge.Types
        # print(f"Using edge types: {edge_types}")
        edges = pg.edges_of_types(edge_types=edge_types)
        edges.sort(key=lambda edge: edge.pg_id())

        domroot_node: Optional[DOMRootNode] = None
        if self.frame_nid:
            domroot_node = pg.node(self.frame_nid).as_domroot_node()
            if not domroot_node:
                raise ValueError("The PageGraph id provided is not " +
                    f"a DOMRootNode, nid={self.frame_nid}")
            
        for edge in edges:
            if domroot_node:
                if edge.frame_id() != domroot_node.frame_id():
                    continue
            edge_report = edge.to_edge_report(depth=0)
            reports.append(Result(edge_report))

        return pagegraph.commands.Result(pg, reports)
