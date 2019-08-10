from __future__ import annotations
import re
from functools import partial
import math
import ast
from dateutil import parser as datetime_parser
from typing import Mapping, Callable, List, Tuple, Any, NoReturn, Type, ClassVar


__all__ = ("Filter",)


class Filter:
    _filters: ClassVar[Mapping[str, Callable]] = {}

    @classmethod
    def compile_filters(cls: Type[Filter], filter_string: str) -> Filter:
        parts = filter_string.split("|")
        target = parts[0]
        _filters = parts[1:] if len(target) > 1 else None
        filters = []
        if _filters is not None:
            for _filter in _filters:
                if _filter != "":
                    try:
                        _func, _args = _filter.split(":", maxsplit=1)
                        args = ast.literal_eval(f"[{_args}]")
                        func = cls._filters[_func]
                        filters.append((func, args))
                    except KeyError as e:
                        raise SyntaxError(f'unkown filter "{_func}"')
                    except AttributeError as e:
                        raise SyntaxError("illegal filter syntax")
                else:
                    raise SyntaxError("illegal filter syntax")
        return Filter(target, filters)

    @classmethod
    def register(cls: Type[Filter], func: Callable) -> Callable:
        cls._filters[func.__qualname__] = func
        return func

    def __init__(
        self: Filter, target: str, filters: List[Tuple[Callable, List[Any]]]
    ) -> NoReturn:
        self._target = target
        self._filters = filters

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"Filter(target={repr(self._target)}, " + f" funcs={self._filters})"

    def __call__(self: Filter, context: Mapping[str, Any]) -> str:
        value = context[self._target]
        for func, args in self._filters:
            value = func(value, *args)
        return value


# == Filters
class Link:
    @Filter.register
    def as_name(val, target):
        return f"[{val}]({target})"

    @Filter.register
    def as_target(val, name):
        return f"[{name}]({val})"


@Filter.register
def get_mul(val, target):
    return [
        d[target if isinstance(d, dict) else int(target)]
        for d in val if target in d
    ]


@Filter.register
def get(val, target):
    return val[target if isinstance(val, dict) else int(target)]


@Filter.register
def ul(vals):
    return "\n".join(f"* {val}" for val in vals)


@Filter.register
def ol(vals):
    return "\n".join(f"{i+1}. {val}" for i, val in enumerate(vals))


@Filter.register
def bold(val):
    return f"__{val}__"


@Filter.register
def italic(val):
    return f"*{val}*"


@Filter.register
def strikethrough(val):
    return f"~~{val}~~"


@Filter.register
def heading(val, level=1):
    return ("#" * int(level)) + f" {val}"


@Filter.register
def tabularize(vals, *headings):
    if len(vals) == 0:
        return "No values"

    def row(coll, fill=" "):
        return "|" + "|".join(fill + str(val) + fill for val in coll) + "|\n"

    def generate_headings(v):
        return set(key for item in v for key in item)

    if isinstance(vals, dict) and all(isinstance(val, dict) for val in vals.values()):
        vals = sorted(
            [dict(_=key, **val) for key, val in vals.items()],
            key=lambda x: x["_"]
        )
        headings = ["_"] + list(headings or (generate_headings(vals) - set(["_"])))
    elif len(headings) == 0:
        headings = generate_headings(vals)

    table = row(headings) + row(("-" * len(heading) for heading in headings), fill="-")
    for entry in vals:
        new_row = row(
            str(entry[heading]).strip().replace("\n", " ") if heading in entry else "-"
            for heading in headings
        )
        table += new_row
    return table


@Filter.register
def date(val, output_format="%x %X"):
    return datetime_parser.parse(val).strftime(output_format)


@Filter.register
def frmt(val, output_format):
    return f"{{:{output_format}}}".format(val)


@Filter.register
def adjust(val, adjustment, precision=0):
    if adjustment == "+":
        return math.ceil(float(val))
    elif adjustment == "-":
        return math.floor(float(val))
    elif adjustment == "~":
        return round(float(val), int(precision))
    else:
        raise SyntaxError(f'unkown adjustment "{adjustment}"')


escape_sequences: Mapping[str, str] = {"\\n": "\n"}


@Filter.register
def join(vals, delim, escape=None):
    if escape and delim in Filter.escape_sequences:
        delim = escape_sequences[delim]
    return delim.join(vals)
