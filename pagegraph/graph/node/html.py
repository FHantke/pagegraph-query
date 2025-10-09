from __future__ import annotations

from typing import Optional

from pagegraph.graph.node.abc.parent_dom_element import ParentDOMElementNode
from pagegraph.serialize import Reportable, DOMElementReport
from pagegraph.graph.node.parser import ParserNode


class HTMLNode(ParentDOMElementNode, Reportable):

    def as_html_node(self) -> Optional[HTMLNode]:
        return self

    def to_report(self) -> DOMElementReport:
        # creator_chain = [c.to_report() for c in self.creator_chain()]

        attrs = self.attributes()
        execution_context = self.execution_context()
        if execution_context:
            # print(execution_context.to_report())
            if not execution_context.is_top_level_domroot():
                parent_dom_root = execution_context.parent_domroot_node()
                frame_security_origin = parent_dom_root.security_origin()
                if frame_security_origin:
                    attrs["frame security origin"] = frame_security_origin

            frame_url = execution_context.url()
            if frame_url:
                attrs["frame url"] = frame_url

        return DOMElementReport(self.pg_id(), self.tag_name(),
                                attrs)
