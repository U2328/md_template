# {{name}}
*export by {{user.displayName}} on {{modified|date}}*

## General
Race: {{race}}
Class: {{level}}
Age: {{age}}
Alignment: {{alignment}}
Size: {{size}}
Languages: {{languages}}

Immunities: {{immunities}}
Resistances: {{resistances}}

Total XP: {{xp.total}}
XP to next Level: {{xp.toNextLevel}}

| Ability       | value             |
| ------------- | ----------------- |
| Strength      | {{abilities.str}} |
| Dexterity     | {{abilities.dex}} |
| Charisma      | {{abilities.cha}} |
| Consititution | {{abilities.con}} |
| Intelligence  | {{abilities.int}} |
| Wisdom        | {{abilities.wis}} |

## Saves
{{saves|tabularize(total)}}

## Skills
{{skills|tabularize(name,classSkill,total,ranks,racial,trait,misc)}}

## Combat Shizzle
### HP
| total HP     | wounds        | non lethal       |
| ------------ | ------------- | ---------------- |
| {{hp.total}} | {{hp.wounds}} | {{hp.nonLethal}} |

### Numbers
| AC           | CMD           | CMB           |
| ------------ | ------------- | ------------- |
| {{ac.total}} | {{cmd.total}} | {{cmb.total}} |

### Ranged Attacks
{{ranged|tabularize(weapon,damage,attackBonus,critical,type,ammunition)}}

### Meelee Attacks
{{melee|tabularize(weapon,damage,attackBonus,critical,type)}}

## Special Shizzle
### Feats
{{feats|tabularize(name,type,notes)}}

### Special Abilities
{{specialAbilities|tabularize(type,name,notes)}}

### Traits
{{traits|tabularize(name,type,notes)}}

## Gear
### Money
| pp           | gp           | sp           | cp           | gems           | other           |
| ------------ | ------------ | ------------ | ------------ | -------------- | --------------- |
| {{money.pp}} | {{money.gp}} | {{money.sp}} | {{money.cp}} | {{money.gems}} | {{money.other}} |

### Stuff
{{gear|tabularize(name,type,location,quantity,weight,notes)}}

## Spells
{{spells|for_each(get(slotted),tabularize(level,name,school,subschool,prepared,cast))|join(\n,True)}}

## Notes
{{notes}}