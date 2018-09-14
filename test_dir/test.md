## Spells
{% for levelA, levelB in zip(spells, spells) %}{% if "slotted" in levelA %}{% with level=levelA|get:"slotted" test=levelB %}
{{level|tabularize:"level","name","school","subschool","prepared","cast"}}
{{test|tabularize:"level","name"}}
{% endwith %}{% endif %}{% endfor %}