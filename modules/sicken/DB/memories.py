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

	def add_memory(self, memory_uuid, profile_uuid, profile_user_name, profile_platform, classification_uuid, classification_group_uuid, memory_value, sickens_comment):
		document={
			"memory_uuid": memory_uuid,
			"profile_uuid": profile_uuid,
			"profile_user_name": profile_user_name,
			"profile_platform": profile_platform,
			"classification_uuid": classification_uuid,
			"classification_group_uuid": classification_group_uuid,
			"memory_value": memory_value,
			"sickens_comment": sickens_comment
		}

		self._memories_collection.insert_one(document)