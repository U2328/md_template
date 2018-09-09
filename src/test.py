import json
import dill as pickle

from parsing import parse, Types
from walking import walk


example =\
"""## Spells
{% for level, in spells %}
{% if "slotted" in level %}
    {{level|get:"slotted"|tabularize:"level","name","school","subschool","prepared","cast"}}

{% endif %}
{% endfor %}"""

ast = parse(example)
# print(*ast.children, sep="\n\n")

with open("data.json", "r") as f:
    data = json.load(f)

_ast = pickle.dumps(ast)

res = walk(pickle.loads(_ast), data)
print(res)
