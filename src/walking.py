from __future__ import annotations
from parsing import Types, Node, Context

__all__ = ("walk",)


def walk(root: Node, context: Conext) -> str:
    output = ""
    last_conditional = None
    for node in root.children:
        if node.type == Types.TEXT:
            output += node.contents
        elif node.type == Types.STAT:
            output += node.func(context)
        elif node.type == Types.CONTEXT_INJECT:
            name, value = node.func(context)
            output += walk(node, dict(context.items(), **{name: value}))
        elif node.type == Types.ITERATE:
            names, iterable = node.func(context)
            for x in iterable:
                _context = dict(
                    context.items(),
                    **{names[i]: val for i, val in enumerate(x)}
                )
                output += walk(node, _context)
        elif node.type == Types.CONDITIONAL:
            last_conditional = node.func(context)
            if last_conditional:
                output += walk(node, context)
        elif node.type == Types.ALTERNATE_CONDITIONAL:
            res = node.func(context)
            if not last_conditional and res:
                output += walk(node, context)
            last_conditional = res
        elif node.type == Types.ALTERNATIVE:
            if not last_conditional:
                output += walk(node, context)
    return output
