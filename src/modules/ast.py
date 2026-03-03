from dataclasses import dataclass
from typing import Callable, List, Optional, Any

from utils.utils import log


class ASTNode:
    pass


@dataclass
class Literal(ASTNode):
    value: Any

    def to_code(self) -> str:
        return repr(self.value)


@dataclass
class Identifier(ASTNode):
    name: str

    def to_code(self) -> str:
        return self.name


@dataclass
class BinOp(ASTNode):
    left: ASTNode
    op: str
    right: ASTNode

    def to_code(self) -> str:
        left = _to_code(self.left)
        right = _to_code(self.right)
        return f"({left} {self.op} {right})"


@dataclass
class UnaryOp(ASTNode):
    op: str
    expr: ASTNode

    def to_code(self) -> str:
        if self.op == "!":
            return f"(not {_to_code(self.expr)})"
        return f"({self.op}{_to_code(self.expr)})"


@dataclass
class FunctionCall(ASTNode):
    name: str
    args: List[ASTNode]

    def to_code(self) -> str:
        args = ", ".join(_to_code(a) for a in self.args)
        return f"{self.name}({args})"


@dataclass
class VarDecl(ASTNode):
    name: str
    var_type: str
    value: ASTNode

    def gen(self, logger: Callable, indent: int = 0) -> None:
        logger(
            f"{_indent(indent)}{self.name}: {self.var_type} = {_to_code(self.value)}"
        )


@dataclass
class Assignment(ASTNode):
    name: str
    value: ASTNode

    def gen(self, logger: Callable, indent: int = 0) -> None:
        logger(f"{_indent(indent)}{self.name} = {_to_code(self.value)}")


@dataclass
class PrintStmt(ASTNode):
    expr: ASTNode

    def gen(self, logger: Callable, indent: int = 0) -> None:
        logger(f"{_indent(indent)}print({_to_code(self.expr)})")


@dataclass
class ReturnStmt(ASTNode):
    expr: ASTNode

    def gen(self, logger: Callable, indent: int = 0) -> None:
        logger(f"{_indent(indent)}return {_to_code(self.expr)}")


@dataclass
class Block(ASTNode):
    statements: List[ASTNode]

    def gen(self, logger: Callable, indent: int = 0) -> None:
        for stmt in self.statements:
            try:
                stmt.gen(logger, indent)
            except TypeError:
                stmt.gen(logger)


@dataclass
class IfStmt(ASTNode):
    condition: ASTNode
    true_block: "Block"
    false_block: Optional["Block"] = None

    def gen(self, logger: Callable, indent: int = 0) -> None:
        logger(f"{_indent(indent)}if {_to_code(self.condition)}:")
        if self.true_block is not None:
            self.true_block.gen(logger, indent + 1)
        else:
            logger(f"{_indent(indent+1)}pass")
        if self.false_block is not None:
            logger(f"{_indent(indent)}else:")
            self.false_block.gen(logger, indent + 1)


@dataclass
class WhileStmt(ASTNode):
    condition: ASTNode
    body: "Block"

    def gen(self, logger: Callable, indent: int = 0) -> None:
        logger(f"{_indent(indent)}while {_to_code(self.condition)}:")
        if self.body is not None:
            self.body.gen(logger, indent + 1)
        else:
            logger(f"{_indent(indent+1)}pass")


# Nós de funçao e programa
@dataclass
class FormalParam(ASTNode):
    name: str
    param_type: str


@dataclass
class FunctionDecl(ASTNode):
    name: str
    params: List[FormalParam]
    return_type: str
    body: "Block"

    def gen(self, logger: Callable, indent: int = 0) -> None:
        params = ", ".join(f"{p.name}: {p.param_type}" for p in self.params)
        ret = f" -> {self.return_type}" if getattr(self, "return_type", None) else ""
        logger(f"{_indent(indent)}def {self.name}({params}){ret}:")
        if self.body and getattr(self.body, "statements", None):
            self.body.gen(logger, indent + 1)
        else:
            logger(f"{_indent(indent+1)}pass")


@dataclass
class Program(ASTNode):
    statements: List[ASTNode]

    def gen(self, logger: Callable = log) -> None:
        for stmt in self.statements:
            # statements receive (logger, indent)
            stmt.gen(logger)


# --- Code generation helpers attached to AST nodes ---


def _indent(level: int) -> str:
    return "    " * (level or 0)


def _to_code(node: Optional[ASTNode]) -> str:
    if node is None:
        return "None"
    # expressions implement `to_code` where appropriate
    if hasattr(node, "to_code"):
        return node.to_code()  # pyright: ignore[reportAttributeAccessIssue]
    # fallback: try to stringify
    return str(node)
