def tidy_up_memory(profile):
	del profile['_id']
	return profile


class Memories:
	def get_all_memories_with_user_by_profile_uuid(self, profile_uuid):
		query={
			'profile_uuid': profile_uuid
			}

		doc=self._memories_collection.find(query)
		memories={}
		for memory in doc:
			memories[memory['memory_uuid']]=tidy_up_memory(memory)
		return memories
