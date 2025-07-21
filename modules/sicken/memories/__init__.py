from uuid import uuid4
from random import randint
class Memories:
	def __init__(self, root):

		self._root=root

		self._config=root._config
		self._log=root._log

		self._db=root._db


	
	def _get_user_memories(self, profile_user_name, profile_platform):
		profile=self._db.get_profile_by_user_name(
			profile_user_name=profile_user_name,
			profile_platform=profile_platform
			)
		if profile:
			memories=self._db.get_all_memories_with_user_by_profile_uuid(
				profile_uuid=profile['profile_uuid'])

			generated_memories={}
			for memory in memories:
				#print(memory, memories[memory])
				classification_definition=self._db.get_classification_definition_by_classification_uuid(
					classification_uuid=memories[memory]['classification_uuid'])

				classification_group=self._db.get_classification_group_by_classification_group_uuid(
					classification_group_uuid=classification_definition['classification_group_uuid'])
				cl={
					"memory_value": memories[memory]['memory_value'],			
					"classification_name": classification_definition['classification_name'],
					"classification_description": classification_definition['classification_description'],
					"classification_group": classification_group['classification_group_name'],
					"sickens_comment": memories[memory]['sickens_comment']

				}
				generated_memories[memories[memory]['memory_uuid']]=cl
			return generated_memories
		return {}

	def _get_random_memories(self, profile_user_name, profile_platform, amount=50):
		memories=self._get_user_memories(profile_user_name, profile_platform)
		memories_indexes=list(memories.keys())
		idents=[]
		ids=[]
		for x in range(amount):
			while True:
				i=randint(0,len(memories_indexes)-1)
				if i not in ids:
					ids.append(i)
					idents.append(memories_indexes[i])
					break

		random_memories={}
		for x in idents:
			random_memories[x]=memories[x]

		return random_memories

	def _add_memory(self, profile_user_name, profile_platform, classification_uuid, memory_value, sickens_comment):
		if not self._db.profile_exists(profile_user_name=profile_user_name,profile_platform=profile_platform):
			profile_uuid=str(uuid4())
			self._db.add_user_profile(
				profile_uuid=profile_uuid,
				profile_platform=profile_platform,
				profile_user_name=profile_user_name)

		profile=self._db.get_profile_by_user_name(
			profile_user_name=profile_user_name,
			profile_platform=profile_platform
			)
		memory_uuid=str(uuid4())

		classification_group=self._db.get_classification_group_by_classification_uuid(
			classification_uuid=classification_uuid)

		self._db.add_memory(
			memory_uuid=memory_uuid,
			profile_uuid=profile['profile_uuid'],
			profile_user_name=profile_user_name,
			profile_platform=profile_platform,
			classification_uuid=classification_uuid,
			classification_group_uuid=classification_group['classification_group_uuid'],
			memory_value=memory_value,
			sickens_comment=sickens_comment
			)

