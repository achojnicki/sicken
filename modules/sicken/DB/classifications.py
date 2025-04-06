from sicken.exceptions import ClassificationGroupNotFoundException

def clean_up(data):
	del data['_id']
	return data


class Classifications:
	def get_classification_group_by_classification_group_uuid(self, classification_group_uuid):
		query={
			'classification_group_uuid': classification_group_uuid
			}

		return clean_up(self._classification_groups_collection.find_one(query))

	def get_all_definitions_of_classification_group(self, classification_group_uuid):
		if not self.get_classification_group_by_classification_group_uuid(classification_group_uuid):
			raise ClassificationGroupNotFoundException

		definitions=[]

		query={'classification_group_uuid': classification_group_uuid}
		cursor=self._classification_definitions_collection.find(query)

		for definition in cursor:
			classifications.append(definition)

		return definitions

	def get_classification_definition_by_classification_uuid(self, classification_uuid):
		query={
			'classification_uuid': classification_uuid
			}

		return clean_up(self._classification_definitions_collection.find_one(query))


