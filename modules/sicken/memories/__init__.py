class Memories:
	def __init__(self, root):

		self._root=root

		self._config=root._config
		self._log=root._log

		self._db=root._db


	
	def _get_user_memories(self, profile_user_name):
		profile=self._db.get_profile_by_user_name(
			profile_user_name=profile_user_name,
			)

		memories=self._db.get_all_memories_with_user_by_profile_uuid(
			profile_uuid=profile['profile_uuid'])

		generated_memories={}
		for memory in memories:
			print(memory, memories[memory])
			classification_definition=self._db.get_classification_definition_by_classification_uuid(
				classification_uuid=memories[memory]['classification_uuid'])

			classification_group=self._db.get_classification_group_by_classification_group_uuid(
				classification_group_uuid=classification_definition['classification_group_uuid'])
			cl={
				"memory_uuid": memories[memory]['memory_uuid'],
				"classification_value": memories[memory]['memory_value'],			
				"classification_uuid": memories[memory]['classification_uuid'],
				"classification_name": classification_definition['classification_name'],
				"classification_description": classification_definition['classification_description'],
				"classification_group": classification_group['classification_group_name']
			}
			generated_memories[memories[memory]['memory_uuid']]=cl
		return generated_memories