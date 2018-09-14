from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from itertools import takewhile
from typing import (
    List,
    Optional,
    Callable,
    Generator,
    Any,
    NewType,
    Mapping,
    Tuple,
)

from filtering import Filter

__all__ = ("Types", "tokenize", "parse")


Context = NewType("Context", Mapping[str, Any])
NodeFunc = NewType("NodeFunc", Callable[[Context], Any])


class Types(Enum):
    # Simple types
    NULL = None
    TEXT = "text"
    STAT = "stat"

    # Temporary types
    ENV = ""
    BRAC_CLOSE = None

    # Complex types
    CONTEXT_INJECT = "with"
    ITERATE = "for"
    CONDITIONAL = "if"
    ALTERNATIVE = "else"
    ALTERNATE_CONDITIONAL = "elif"

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.name


LEGAL_OPERATIONS = [
    op.value
    for op in [
        Types.CONTEXT_INJECT,
        Types.ITERATE,
        Types.CONDITIONAL,
        Types.ALTERNATE_CONDITIONAL,
        Types.ALTERNATIVE,
    ]
]


@dataclass
class Node:
    type: Types = field(default=Types.NULL)
    contents: Optional[str] = None
    parent: Optional[Node] = None
    children: List[Node] = field(default_factory=list)
    func: Optional[NodeFunc] = None

    def __repr__(self):
        return self.pp(-1)

    def pp(self, level=0):
        _self = f"Node(type={self.type}, contents={repr(self.contents)}, func={self.func})"
        if level >= 0:
            _children = [child.pp(level + 1) for child in self.children]
            for child in _children:
                _self += "\n" + "\t" * level + "↪  " + child
        return _self


def tokenize(s: str) -> Generator[Node, None, None]:
    acc = ""
    open_bracket = Types.BRAC_CLOSE

    for c in s:
        acc += c
        if len(acc) > 1:
            check = acc[-2:]
            bracket = None

            # Check for statments, i.e. '... {{ ... }} ...'
            if check == r"{{" and open_bracket is Types.BRAC_CLOSE:
                bracket = Types.STAT
            if check == r"}}" and open_bracket is Types.STAT:
                bracket = Types.BRAC_CLOSE

            # Check for environment/scope statements, i.e. '... {% ... %} ...'
            if check == r"{%" and open_bracket is Types.BRAC_CLOSE:
                bracket = Types.ENV
            if check == r"%}" and open_bracket is Types.ENV:
                bracket = Types.BRAC_CLOSE

            # Check for change in bracket "state"
            if bracket is Types.BRAC_CLOSE:
                yield Node(open_bracket, acc[:-2])
                acc = ""
                open_bracket = bracket
            elif bracket is not None:
                yield Node(Types.TEXT, acc[:-2])
                acc = ""
                open_bracket = bracket

    yield Node(Types.TEXT, acc)


def parse(s: str) -> Node:
    root: Node = Node()
    current_node: Node = root
    awaited_ends: List[str] = []
    skip = False
    for tok in tokenize(s):
        # Skip the empty stuff
        if tok.contents == "" or tok.type == Types.NULL or skip is True:
            skip = False
            continue
        # make sure the parent is set properly
        tok.parent = current_node

        # handle complex type assigment
        if tok.type == Types.ENV:
            data = tok.contents.strip().split(" ")
            operation = data[0]
            if (
                len(awaited_ends) == 0 or operation != awaited_ends[-1]
            ) and operation in LEGAL_OPERATIONS:
                tok.type = Types(operation)
                if tok.type == Types.CONTEXT_INJECT:
                    tok.func = parse_contextmanager(data[1:])
                    awaited_ends.append("end" + operation)
                elif tok.type == Types.ITERATE:
                    tok.func = parse_iteration(data[1:])
                    awaited_ends.append("end" + operation)
                elif tok.type == Types.CONDITIONAL:
                    tok.func = parse_condition(data[1:])
                    awaited_ends.append("end" + operation)
                elif tok.type == Types.ALTERNATE_CONDITIONAL:
                    tok.func = parse_condition(data[1:])
                elif tok.type == Types.ALTERNATIVE:
                    ...
                else:
                    raise SyntaxError(f"Unkown operation '{operation}'")
                current_node.children.append(tok)
                current_node = tok
            elif operation == awaited_ends[-1]:
                current_node = current_node.parent
                del awaited_ends[-1]
            else:
                raise NotImplementedError
        # handle simple type assignment
        else:
            if tok.type == Types.STAT:
                try:
                    tok.func = Filter.compile_filters(tok.contents.strip())
                except Exception as e:
                    print(f"<!> {e}")
                    tok.type = Types.TEXT
                    tok.contents = r"{{" + tok.contents + r"}}"
            current_node.children.append(tok)
    return root


def parse_iteration(data: List[str]) -> NodeFunc:
    names_raw = list(takewhile(lambda x: x != "in", data))
    names_list = [
        x
        for x in sum(
            (
                name.split(",") if "," in name else [name]
                for name in names_raw
                if name != ""
            ),
            [],
        )
        if x != ""
    ]
    names_str = ", ".join(list(names_list))
    iter_stat = " ".join(data).replace(" ".join(names_raw), "")
    gen_expr = f"(({names_str},) for {names_str}{iter_stat})"

    def iteration(context: Context) -> Tuple[str, Any]:
        return names_list, eval(gen_expr, context)

    return iteration


def parse_contextmanager(data: List[str]) -> NodeFunc:
    _vars = []
    _data_targets = []
    for _data in data:
        var, _data_target = _data.split("=")
        _data_targets.append(Filter.compile_filters(_data_target))
        _vars.append(var)

    def context_injection(context: Context) -> Tuple[str, Any]:
        return _vars, [data_target(context) for data_target in _data_targets]

    return context_injection


def parse_condition(data: List[str]) -> NodeFunc:
    cond = " ".join(data)

    def condition(context: Context) -> bool:
        return eval(cond, context)

    return condition
