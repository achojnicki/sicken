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

	def get_all_clasification_groups(self):
		classification_gropus=self._classification_groups_collection.find()

		cg={}
		for classification_group in classification_gropus:
			cg[classification_group['classification_group_uuid']]=clean_up(classification_group)

		return cg

	def get_all_classification_definitions_of_classification_group(self, classification_group_uuid):
		query={
			"classification_group_uuid": classification_group_uuid
		}
		d=self._classification_definitions_collection.find(query)

		cgd={}

		for classification_definition in d:
			cgd[classification_definition['classification_uuid']]=clean_up(classification_definition)

		return cgd
		
	def get_all_definitions_of_classification_group(self, classification_group_uuid):
		if not self.get_classification_group_by_classification_group_uuid(classification_group_uuid):
			raise ClassificationGroupNotFoundException

		definitions=[]

		query={'classification_group_uuid': classification_group_uuid}
		cursor=self._classification_definitions_collection.find(query)

		for definition in cursor:
			classifications.append(clean_up(definition))

		return definitions

	def get_classification_definition_by_classification_uuid(self, classification_uuid):
		query={
			'classification_uuid': classification_uuid
			}

		return clean_up(self._classification_definitions_collection.find_one(query))

	def get_classification_group_by_classification_uuid(self, classification_uuid):
		query={
			'classification_uuid': classification_uuid
			}

		cg=self._classification_definitions_collection.find_one(query)

		return self.get_classification_group_by_classification_group_uuid(
			classification_group_uuid=cg['classification_group_uuid'])

	def get_classifications(self):
		d=self.get_all_clasification_groups()
				
		for x in dict(d):
			d[x]['classifications']=self.get_all_classification_definitions_of_classification_group(x)

		return d