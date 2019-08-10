from __future__ import annotations
from typing import Optional

from src.parsing import Types, Node, Context

__all__ = ("walk",)


def walk(root: Node, context: Context, *, fail_default: Optional[str] = None) -> str:
    try:
        output = ""
        last_conditional = None
        for node in root.children:
            if node.type is Types.TEXT:
                output += node.contents
            elif node.type is Types.STAT:
                output += str(node.func(context))
            elif node.type is Types.CONTEXT_INJECT:
                names, values = node.func(context)
                _context = dict(
                    context.items(),
                    **{name: value for name, value in zip(names, values)}
                )
                output += walk(node, _context)
            elif node.type is Types.ITERATE:
                names, iterable = node.func(context)
                for vals in iterable:
                    _context = dict(
                        context.items(), **{names[i]: val for i, val in enumerate(vals)}
                    )
                    output += walk(node, _context)
            elif node.type is Types.CONDITIONAL:
                last_conditional = node.func(context)
                if last_conditional:
                    output += walk(node, context)
            elif node.type is Types.ALTERNATE_CONDITIONAL:
                res = node.func(context)
                if not last_conditional and res:
                    output += walk(node, context)
                last_conditional = res
            elif node.type is Types.ALTERNATIVE:
                if not last_conditional:
                    output += walk(node, context)
        return output
    except:
        if fail_default is None:
            raise
        else:
            return fail_default
