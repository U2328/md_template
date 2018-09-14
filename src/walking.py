from __future__ import annotations
from src.parsing import Types, Node, Context

__all__ = ("walk",)


def walk(root: Node, context: Context) -> str:
    output = ""
    last_conditional = None
    for node in root.children:
        _type = node.type.value
        if _type == Types.TEXT.value:
            output += node.contents
        elif _type == Types.STAT.value:
            output += str(node.func(context))
        elif _type == Types.CONTEXT_INJECT.value:
            names, values = node.func(context)
            _context = dict(
                context.items(),
                **{
                    name: value
                    for name, value in zip(names, values)
                }
            )
            output += walk(node, _context)
        elif _type is Types.ITERATE.value:
            names, iterable = node.func(context)
            for vals in iterable:
                _context = dict(
                    context.items(),
                    **{
                        names[i]: val
                        for i, val in enumerate(vals)
                    }
                )
                output += walk(node, _context)
        elif _type == Types.CONDITIONAL.value:
            last_conditional = node.func(context)
            if last_conditional:
                output += walk(node, context)
        elif _type == Types.ALTERNATE_CONDITIONAL.value:
            res = node.func(context)
            if not last_conditional and res:
                output += walk(node, context)
            last_conditional = res
        elif _type == Types.ALTERNATIVE.value:
            if not last_conditional:
                output += walk(node, context)
    return output
