from __future__ import annotations

from base64 import b64encode
import hashlib
from typing import Optional, TYPE_CHECKING

from pagegraph.graph.node.abc.dom_element import DOMElementNode
from pagegraph.serialize import Reportable, DOMElementReport

if TYPE_CHECKING:
    from pagegraph.serialize import JSONAble


class TextNode(DOMElementNode, Reportable):

    def as_text_node(self) -> Optional[TextNode]:
        return self

    def to_report(self) -> DOMElementReport:
        attrs: dict[str, JSONAble] = {"text": self.text()}

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
                
        return DOMElementReport(self.pg_id(), self.tag_name(), attrs)

    def tag_name(self) -> str:
        return "[text]"

    def text(self) -> str:
        return self.data()[self.__class__.RawAttrs.TEXT.value]

    def hash(self) -> str:
        hasher = hashlib.new("sha256")
        hasher.update(self.text().encode("utf8"))
        return b64encode(hasher.digest()).decode("utf8")
