import argparse
import json
import dill as pickle

from src.parsing import parse, Types
from src.walking import walk


def _compile(args):
    ast = parse(args.file.read())
    print(ast.pp())
    out_path = args.file.name[::-1].split(".", maxsplit=1)[1][::-1] + ".mdtemp"
    with open(out_path, "wb") as f:
        pickle.dump(ast, f)


def _apply(args):
    data = json.load(args.data)
    ast = pickle.load(args.template)
    res = walk(ast, data)
    args.output.write(res)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="md_template")
    subparsers = parser.add_subparsers(help="Pick a sub command...")

    compile_parser = subparsers.add_parser("compile", aliases=["c"], help="compile a template")
    compile_parser.add_argument(
        "file", type=argparse.FileType(mode="r", encoding="utf-8"),
        help="template to compile"
    )
    compile_parser.set_defaults(func=_compile)

    apply_parser = subparsers.add_parser("apply", aliases=["a"], help="apply a template")
    apply_parser.add_argument(
        "data", type=argparse.FileType(mode="r", encoding="utf-8"),
        help="data to use as context"
    )
    apply_parser.add_argument(
        "template", type=argparse.FileType(mode="rb"),
        help="template to apply"
    )
    apply_parser.add_argument(
        "output", type=argparse.FileType(mode="w", encoding="utf-8"),
        help="output file"
    )
    apply_parser.set_defaults(func=_apply)

    args = parser.parse_args()
    args.func(args)
