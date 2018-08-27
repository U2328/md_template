import re
import math
from dateutil import parser as datetime_parser
from typing import Mapping, Callable, List, Tuple, Any, NoReturn, Type


__all__ = (
    "Filter",
)

_filter_re = re.compile(r"^(?P<func>[^()]+)(?:\((?P<args>.*)\))?$")
_arg_re = re.compile(r"(?P<arg>[^(),]+(?:\([^()]*\))?)")


class Filter:
    _filters: Mapping[str, Callable] = {}

    @classmethod
    def compile_filters(cls: Type[Filter], filter_strings: List[str]) -> Filter:
        filters = []
        if filter_strings:
            for filter_string in filter_strings:
                if filter_string != "":
                    try:
                        _func, args = cls._parse_filter(filter_string)
                        func = cls._filters[_func]
                        filters.append((func, args))
                    except KeyError as e:
                        raise SyntaxError(f"unkown filter \"{func}\"")
                    except AttributeError as e:
                        raise SyntaxError("illegal filter syntax")
                else:
                    raise SyntaxError("illegal filter syntax")
        return Filter(filters)

    @staticmethod
    def _parse_filter(filter_string: str) -> Tuple[str, List[str]]:
        match = _filter_re.fullmatch(filter_string)
        func = match.group("func")
        args = []
        if match.group("args"):
            for match in _arg_re.finditer(match.group("args")):
                args.append(match.group("args"))
        return func, args

    @classmethod
    def register(cls: Type[Filter], func: Callable) -> Callable:
        cls._filters[func.__qualname__] = func
        return func

    def __init__(self: Filter, target: str, *filters: List[Tuple[Callable, List[Any]]]) -> NoReturn:
        self._target = target
        self._filters = filters

    def __call__(self: Filter, context: Mapping[str, Any]) -> str:
        value = context[self._target]
        for func, args in self._filters:
            value = func(value, *args)
        return str(value)


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
        return ""

    def row(coll, fill=" "):
        return "|" + "|".join(fill + str(val) + fill for val in coll) + "|\n"

    def generate_headings(v):
        return set(key for item in v for key in item)

    if isinstance(vals, dict) and isinstance(list(vals.values())[0], dict):
        vals = sorted(
            [dict(_=key, **vals[key]) for key in vals],
            key=lambda x: x["_"]
        )
        headings = (
            ["_"] +
            list(
                headings or
                (generate_headings(vals) - set(["_"]))
            )
        )
    elif len(headings) == 0:
        headings = generate_headings(vals)
    table = (
        row(headings) +
        row(("-" * len(heading) for heading in headings), fill="-")
    )
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
        raise SyntaxError(f"unkown adjustment \"{adjustment}\"")


escape_sequences: Mapping[str, str] = {
    '\\n': '\n',
}


@Filter.register
def join(vals, delim, escape=None):
    if escape and delim in Filter.escape_sequences:
        delim = escape_sequences[delim]
    return delim.join(vals)
