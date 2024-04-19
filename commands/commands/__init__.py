from sicken.commands.commands.godzina import godzina
from sicken.commands.commands.dzien import dzien
from sicken.commands.commands.swiatlo import swiatlo
from sicken.constants import Sicken

from yaml import safe_load

cmds={
	'godzina':godzina,
	"dzien": dzien,
	'swiatlo': swiatlo
	}

all_commands={}

for cmd in cmds:
	with open(Sicken.sicken_path / "commands" / "commands" / cmd / "manifest.yaml") as manifest_file:
		manifest=safe_load(manifest_file)
		
	all_commands[cmd]={
		"name": cmd,
		"description": manifest['description'],
		"commands": manifest['commands'],
		"class": cmds[cmd],
		"object": None
	}

