from sicken.exceptions import UserProfileNotFoundException, UserProfileAlreadyExistsException

def clean_up_profile(profile):
	del profile['_id']
	del profile['profile_uuid']
	del profile['profile_platform']
	del profile['profile_user_name']
	return profile


class Profiles:
	def get_profile_by_profile_uuid(self, profile_uuid):
		query={
			'profile_uuid': profile_uuid
			}

		doc=self._user_profiles_collection.find_one(query)
		return doc

	def get_profile_by_user_name(self, profile_user_name):
		query={
			'profile_user_name': profile_user_name,
			}

		doc=self._user_profiles_collection.find_one(query)
		return doc

	def get_all_classifications_of_user_profile_by_profile_uuid(self, profile_uuid):
		if not self.get_profile_by_profile_uuid(profile_uuid):
			raise UserProfileNotFoundException

		profile=self.get_profile_by_profile_uuid(profile_uuid=profile_uuid)
		classifications=clean_up_profile(profile)


		return classifications




	def add_user_profile(self, profile_uuid, profile_user_name, classifications):
		if self.get_profile_by_user_name(profile_user_name):
			raise UserProfileAlreadyExistsException

		document={
			"profile_uuid": str(profile_uuid),
			"profile_user_name": profile_username,
			"profile_platform": profile_platform
		}

		for classification in classifications:
			document[classifications[classification]['classification_uuid']]=classifications['classification']

		self._user_profiles_collection.insert_one(message)