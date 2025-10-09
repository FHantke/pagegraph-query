from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import pagegraph.commands
import pagegraph.graph
from pagegraph.serialize import ReportBase

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Optional, Union

    from pagegraph.graph.node.dom_root import DOMRootNode
    from pagegraph.serialize import EdgeReport
    from pagegraph.types import PageGraphId


@dataclass
class Result(ReportBase):
    storage_call: EdgeReport

class Command(pagegraph.commands.Base):
    frame_nid: Optional[PageGraphId]

    def __init__(self, input_path: Path, 
                 frame_nid: Optional[PageGraphId],
                 debug: bool) -> None:
        self.frame_nid = frame_nid
        super().__init__(input_path, debug)

    def validate(self) -> None:
        if self.frame_nid:
            pagegraph.commands.validate_node_id(self.frame_nid)
        return super().validate()

    def execute(self) -> pagegraph.commands.Result:
        pg = pagegraph.graph.from_path(self.input_path, self.debug)
        reports: list[Result] = []


        storage_edges = list()
        storage_edges += pg.storage_read_edges()
        storage_edges += pg.storage_read_result_edges()
        storage_edges += pg.storage_set_edges()
        storage_edges += pg.storage_delete_edges()
        storage_edges += pg.storage_clear_edges()
        storage_edges.sort(key=lambda edge: edge.pg_id())

        domroot_node: Optional[DOMRootNode] = None
        if self.frame_nid:
            domroot_node = pg.node(self.frame_nid).as_domroot_node()
            if not domroot_node:
                raise ValueError("The PageGraph id provided is not " +
                    f"a DOMRootNode, nid={self.frame_nid}")
            
        for edge in storage_edges:
            if domroot_node:
                if edge.frame_id() != domroot_node.frame_id():
                    continue
            edge_report = edge.to_edge_report(depth=0)
            reports.append(Result(edge_report))
            """
            if edge.type in []
            key = edge.key()
            value = edge.value()
            incoming_node = edge.incoming_node()
            outgoing_node = edge.outgoing_node()

            storage_type = outgoing_node.type_name()

            # TODO Move the dicts to report calls in the edge class
            bucket = {
                "type": storage_type
            }

            call = {
                "method": edge.type_name(),
                "key": key,
                "value": value,
            }


            script_report = incoming_node.to_report()

            reports.append(Result(bucket, call, script_report))
            print(f"Checking edge {edge.pg_id()}")
            print(f"  Key: {key}, Value: {value}")
            print(f"  Incoming Node: {incoming_node.pg_id()}, "
                  f"Outgoing Node: {outgoing_node.pg_id()} ({storage_type})")
        
            """

            """
            if self.frame_nid and edge.frame_id() != domroot_node.frame_id():
                continue
            if self.cross_frame and not edge.is_cross_frame():
                continue
            script_node = edge.incoming_node()
            if self.pg_id and script_node.pg_id() != self.pg_id:
                continue
            call_report = edge.to_report()
            script_report = script_node.to_report()
            reports.append(Result(script_report, call_report))
            """
        """
        # print(reports)
        import json
        for report in reports:
            print(report.bucket)
            print(json.dumps(report.bucket))
            print(report.call)
            print(json.dumps(report.call))
        """
        return pagegraph.commands.Result(pg, reports)
    
        js_structure_nodes = pg.js_structure_nodes()
        for js_node in js_structure_nodes:
            if self.method and self.method not in js_node.name():
                continue

            for call_result in js_node.call_results():
                if (self.frame_nid and
                        call_result.call_context().pg_id() != self.frame_nid):
                    continue
                if (self.cross_frame and
                        not call_result.is_cross_frame_call()):
                    continue
                script_node = call_result.call.incoming_node()
                if self.pg_id and script_node.pg_id() != self.pg_id:
                    continue
                call_report = call_result.to_report()
                script_report = script_node.to_report()
                reports.append(Result(script_report, call_report))
        return pagegraph.commands.Result(pg, reports)
