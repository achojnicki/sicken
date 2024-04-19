from sicken.commands.commands import all_commands

from re import findall, S

class CommandNotFound(Exception):
	pass

MASKS_REGEX=r"\[([a-zA-Z0-9\_\-]{1,})\]"
REGEX=r"([a-zA-Z0-9\_\-\ą\ę\ó\ć\ź\ż\Ą\Ę\Ó\Ć\Ź\Ż]{1,})"

class masker:
	def __init__(self, root):
		self._root=root

	def find_masks_in_pattern(self, pattern_command):
		masks=findall(MASKS_REGEX, pattern_command)
		return masks

	def find_masks(self, raw_command, pattern_command):
		results={}
		masks=self.find_masks_in_pattern(pattern_command)

		
		res=findall(
			self.masks_regex(raw_command, pattern_command, masks),
			raw_command
			)
		print(masks)
		print(res)
		if res:
			for item in res[0]:
				index=res[0].index(item) if type(res[0]) is tuple else 0
				results[masks[index]]=item
		return results



	def masks_regex(self, command, pattern_command, masks):
		regex=pattern_command
		for mask in masks:
			regex=regex.replace('['+mask+']', REGEX)
		return regex



class Commands:
	def __init__(self, root):
		self._root=root
		self._log=root._log
		self._masker=masker(root)
		self._commands=all_commands

		self.initialise_commands()


	def initialise_commands(self):
		for command in self._commands:
			self._commands[command]['object']=self._commands[command]['class'](self._root)


	def find_args(self, cmd , raw_command):
		for pattern_command in self._commands[cmd]['commands']:
			if '[' in pattern_command and ']' in pattern_command:
				masks=self._masker.find_masks(raw_command=raw_command, pattern_command=pattern_command)
				if masks:
					return masks
		return {}

	def find_command(self, cmd, raw_command, args):
		for pattern_command in self._commands[cmd]['commands']:
			if '[' in pattern_command and ']' in pattern_command:
				for arg in args:
					if args[arg]:
						return cmd
			else:
				if raw_command in pattern_command:
					return cmd


	def find(self, raw_command):
		for cmd in self._commands:
			args=self.find_args(cmd, raw_command)
			command=self.find_command(cmd, raw_command, args)

			if command:
				print(command, args)
				return {"command": command, "args": args}

	def execute_command(self, command):
		cmd=self.find(command)
		
		if not cmd:
			raise CommandNotFound

		value=self._commands[cmd['command']]['object'].command(**cmd['args'])
		return value

