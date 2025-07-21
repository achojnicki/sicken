from uuid import uuid4

class Knowledge:
	def __init__(self, root):

		self._root=root

		self._config=root._config
		self._log=root._log

		self._db=root._db


	
	def _get_knowledge(self):
		knowledge=self._db.get_knowledge()
		
		generated_knowledge={}
		for knowledge_item in knowledge:
			knowledge_group=self._db.get_knowledge_group_by_knowledge_group_uuid(
				knowledge_group_uuid=knowledge[knowledge_item]['knowledge_group_uuid'])
			cl={
				"knowledge_value": knowledge[knowledge_item]['knowledge_value'],
				"knowledge_name": knowledge[knowledge_item]['knowledge_name'],
				"knowledge_description": knowledge[knowledge_item]['knowledge_description'],
				"knowledge_group_name": knowledge_group['knowledge_group_name'],
				"knowledge_group_description": knowledge_group['knowledge_group_name']
			}
			generated_knowledge[knowledge[knowledge_item]['knowledge_uuid']]=cl
		return generated_knowledge
