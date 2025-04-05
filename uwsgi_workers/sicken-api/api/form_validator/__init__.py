from exceptions import FormDefinitionSyntaxError, ValidationError, FormNotDefined
from yaml.scanner import ScannerError

from os import listdir
from pathlib import Path

import yaml

class Form_Validator:
	def __init__(self, root):
		self._root=root

		self.log=root.log
		self.config=root.config
	
		self._definitions={}

		self._load_args_definitions()

	def _search_for_args_definitons(self):
		d={}
		for a in listdir(self.config.directories.endpoints_directory):
			p=Path(self.config.directories.endpoints_directory, a, 'form.yaml')
			if p.is_file():
				d[a]=p
		return d

	def _load_args_definitions(self):
		definition_files=self._search_for_args_definitons()
		for a in definition_files:
			try:
				with open(definition_files[a],'r') as file:
					args=yaml.safe_load(file)
					self._definitions[a]=args

			except ScannerError:
				raise FormDefinitionSyntaxError

	def _get_required_fields(self, target):
		required=[]
		target_def=self._definitions[target]
		
		for a in target_def:
			if target_def[a]['required']:
				required.append(a)
		return required

	def _get_empty_not_allowed_fields(self, target):
		empty_not_allowed=[]
		target_def=self._definitions[target]
		
		for a in target_def:
			if not target_def[a]['allow_empty']:
				empty_not_allowed.append(a)
		return empty_not_allowed

	def validate(self, target, args):
		if target not in self._definitions:
			raise FormNotDefined
			
		required_fields=self._get_required_fields(target)
		empty_not_allowed_fields=self._get_empty_not_allowed_fields(target)
		
		missing_fields=required_fields.copy()
		empty_fields=[]

		
		for a in args:
			if a in required_fields:
				del missing_fields[missing_fields.index(a)]
				
		for a in args:
			if a in empty_not_allowed_fields and args[a]=="":
				empty_fields.append(a)

		error={}

		if missing_fields:
			error['missing_fields']=missing_fields
		if empty_fields:
			error['empty_fields']=empty_fields

		if error:
			e=ValidationError()
			e.error=error

			raise e










