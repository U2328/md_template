import json
import dill as pickle

from parsing import parse
from walking import walk


example = """## Spells
{% for levelA, levelB in zip(spells, spells) %}{% if "slotted" in levelA %}{% with level=levelA|get:"slotted" test=levelB %}
{{level|tabularize:"level","name","school","subschool","prepared","cast"}}
{{test|tabularize:"level","name"}}
{% endwith %}{% endif %}{% endfor %}"""

ast = parse(example)
print(ast.pp(), end="\n\n")

with open("src/data.json", "r") as f:
    data = json.load(f)

with open("ast.pickle", "wb") as f:
    f.write(pickle.dumps(ast))

with open("ast.pickle", "rb") as f:
    _ast = pickle.loads(f.read())

res = walk(_ast, data)
print(res)
