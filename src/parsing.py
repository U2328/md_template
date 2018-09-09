from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from itertools import takewhile
from typing import List, Optional, Callable, Generator, Any, NamedTuple, Union, NewType, Mapping
import re
import ast

from filtering import Filter

__all__ = ("Types", "tokenize", "parse")


Context = NewType("Context", Mapping[str, Any])
NodeFunc = NewType("NodeFunc", Callable[[Context,], Any])

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
        return (
            f"Node(type={self.type}, contents={repr(self.contents)}, " +
            f"children={self.children}, func={self.func})"
        )


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
    for tok in tokenize(s):
        # Skip the empty stuff
        if tok.contents == "" or tok.type == Types.NULL:
            continue
        # make sure the parent is set properly
        tok.parent = current_node

        # handle complex type assigment
        if tok.type == Types.ENV:
            data = tok.contents.strip().split(' ')
            operation = data[0]
            if (len(awaited_ends) == 0 or operation != awaited_ends[-1]) and operation in LEGAL_OPERATIONS:
                tok.type = Types(operation)
                if tok.type == Types.CONTEXT_INJECT:
                    tok.func = parse_contextmanager(data[1:])
                    awaited_ends.append("end" + operation)
                if tok.type == Types.ITERATE:
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
                    raise SyntaxError("Unkown operation")
                current_node.children.append(tok)
                current_node = tok
            elif operation == awaited_ends[-1]:
                last_content = current_node.children[-1].contents
                last_type = current_node.children[-1].type
                if last_type == Types.TEXT and last_content.endswith("\n"):
                    current_node.children[-1].contents = last_content[:-2]
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
            if current_node.parent != None and current_node.children == [] and tok.contents.replace(' ', '').endswith("\n"):
                tok.contents = tok.contents.replace(' ', '')[:-2]
            if tok.contents.replace(' ', '') != '':
                current_node.children.append(tok)
    return root


def parse_iteration(data: List[str]) -> NodeFunc:
    names_raw = list(takewhile(lambda x: x != "in", data))
    names_list = sum((
        name.split(",")
        if "," in name else
        [name]
        for name in names_raw
    ), [])
    names_str = ', '.join(x for x in names_list if x != "")
    iter_stat = ' '.join(data).replace(" ".join(names_raw), '')
    gen_expr = f"(({names_str},) for {names_str}{iter_stat})"

    def iteration(context: Context) -> Tuple[str, Any]:
        return names_list, eval(gen_expr, context)

    return iteration


def parse_contextmanager(data: List[str]) -> NodeFunc:
    var, _data_target = data[0].strip().split("=")
    data_target = Filter.compile_filters(_data_target)

    def context_injection(context: Context) -> Tuple[str, Any]:
        return var, data_target(context)

    return context_injection


def parse_condition(data: List[str]) -> NodeFunc:
    cond = ' '.join(data)
    def condition(context: Context) -> bool:
        return eval(cond, context)

    return condition
