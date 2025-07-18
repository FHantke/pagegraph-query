from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import pagegraph.commands
import pagegraph.graph
from pagegraph.serialize import ReportBase
from pagegraph.graph.node import Node
from pagegraph.graph.node.script_local import ScriptLocalNode

if TYPE_CHECKING:
    from pathlib import Path

    from pagegraph.serialize import DOMNodeReport


@dataclass
class Result(ReportBase):
    elements: list[DOMNodeReport]


class Command(pagegraph.commands.Base):
    pg_id = None

    def __init__(self, input_path: Path,
                 pd_id: str,
                 debug: bool) -> None:
        self.pg_id = pd_id
        super().__init__(input_path, debug)

    def validate(self) -> bool:
        return super().validate()

    def execute(self) -> pagegraph.commands.Result:
        # Take a script node and return a report of the creator chain.

        pg = pagegraph.graph.from_path(self.input_path, self.debug)
        target_node = pg.node(self.pg_id)
        assert target_node.is_type(Node.Types.SCRIPT_LOCAL)

        creator_chain = []
        current_node = target_node
        current_creator = {
            "dom": None,
            "scripts": [],
            "urls": [],
            "execution_context": None,
        }

        while True:
            if current_node.is_type(Node.Types.SCRIPT_LOCAL):
                current_creator["scripts"].append(current_node.to_report())
                if current_node.script_type() == ScriptLocalNode.ScriptType.EXTERNAL:
                    current_creator["urls"].append(current_node.url())

            elif current_node.is_type(Node.Types.HTML):
                current_creator["dom"] = current_node.to_report()
                exec_context = current_node.execution_context()
                current_creator["execution_context"] = exec_context.to_report()
                creator_chain.append(current_creator)
                current_creator = {
                    "dom": None,
                    "scripts": [],
                    "urls": [],
                    "execution_context": None,
                }

            elif current_node.is_type(Node.Types.PARSER):
                current_creator["parser"] = current_node.to_report()
                creator_chain.append(current_creator)
                break
            else:
                raise ValueError(f"Unexpected node type in creator chain: {current_node.type()}")

            current_node = current_node.creator_node()


        report = {"creators": creator_chain}

        return pagegraph.commands.Result(pg, report)
