def tidy_up_knowledge(profile):
	del profile['_id']
	return profile


class Knowledge:
	def get_knowledge(self):
		
		doc=self._knowledge_collection.find()
		knowledge={}
		for knowledge_item in doc:
			knowledge[knowledge_item['knowledge_uuid']]=tidy_up_knowledge(knowledge_item)
		return knowledge
	
	def get_knowledge_groups(self):	
		doc=self._knowledge_groups_collection.find()
		knowledge_groups={}
		for knowledge_group_item in doc:
			knowledge_groups[knowledge_group_item['knowledge_group_uuid']]=tidy_up_knowledge(knowledge_group_item)
		return knowledge_groups

	def get_knowledge_group_by_knowledge_group_uuid(self, knowledge_group_uuid):
		query={
			"knowledge_group_uuid": knowledge_group_uuid
		}
		doc=self._knowledge_groups_collection.find_one(query)

		return tidy_up_knowledge(doc)

