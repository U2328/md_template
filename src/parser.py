from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Callable, Generator
from pprint import pprint
import re


class Types(Enum):
    NULL = 0
    TEXT = 1
    EXPR = 2
    STAT = 3
    BRAC_CLOSE = 4


@dataclass
class Node:
    type: Types = field(default=Types.NULL)
    contents: Optional[str] = None
    parent: Optional[Node] = None
    children: List[Node] = field(default_factory=list)
    func: Optional[Callable[[str], str]] = None

    def __repr__(self):
        return f"Node(type={self.type}, contents={repr(self.contents)}, children={self.children})"


def tokenize(s: str) -> Generator[Node, None, None]:
    acc = ""
    open_bracket = Types.BRAC_CLOSE

    for c in s:
        acc += c
        if len(acc) > 1:
            check = acc[-2:]
            bracket = None

            # Check for expressions, i.e. '... {{ ... }} ...'
            if check == r'{{' and open_bracket is Types.BRAC_CLOSE:
                bracket = Types.EXPR
            if check == r'}}' and open_bracket is Types.EXPR:
                bracket = Types.BRAC_CLOSE

            # Check for Statements, i.e. '... {% ... %} ...'
            if check == r'{%'and open_bracket is Types.BRAC_CLOSE:
                bracket = Types.STAT
            if check == r'%}' and open_bracket is Types.STAT:
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
    root = Node()
    current_node = root
    for tok in tokenize(s):
        if tok.type == Types.STAT:
            ...
        else:
            if tok.type == Types.EXPR:
                tok.func = compile_expression(tok.contens)
                if tok.func is None:
                    tok.type = Types.TEXT
                    tok.contents = r'{{' + tok.contents + r'}}'
            current_node.children.append(tok)


def compile_expression(s: str) -> Optional[Callable[[str], str]]:
    return None


if __name__ == "__main__":
    example = r"{{ test }}{%test%}test{{{%asdasd}}%}"

    for child in tokenize(example):
        print(child)

    print(parse(example))
