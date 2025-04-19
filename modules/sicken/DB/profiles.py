from sicken.exceptions import UserProfileNotFoundException, UserProfileAlreadyExistsException

def clean_up_profile(profile):
	del profile['_id']
	return profile


class Profiles:
	def get_all_profiles(self):
		p={}
		docs=self._user_profiles_collection.find()

		for profile in docs:
			p[profile['profile_uuid']]=clean_up_profile(profile)

		return p

	def get_profile_by_profile_uuid(self, profile_uuid):
		query={
			'profile_uuid': profile_uuid
			}

		doc=self._user_profiles_collection.find_one(query)
		return doc

	def get_profile_by_user_name(self, profile_user_name, profile_platform):
		query={
			'profile_user_name': profile_user_name,
			'profile_platform': profile_platform
			}

		doc=self._user_profiles_collection.find_one(query)
		return doc

	def get_all_classifications_of_user_profile_by_profile_uuid(self, profile_uuid):
		if not self.get_profile_by_profile_uuid(profile_uuid):
			raise UserProfileNotFoundException

		profile=self.get_profile_by_profile_uuid(profile_uuid=profile_uuid)
		classifications=clean_up_profile(profile)


		return classifications


	def profile_exists(self, profile_user_name, profile_platform):
		if self.get_profile_by_user_name(
			profile_user_name=profile_user_name,
			profile_platform=profile_platform):
			return True
		return False


	def add_user_profile(self, profile_uuid, profile_user_name, profile_platform):
		if self.get_profile_by_user_name(profile_user_name=profile_user_name, profile_platform=profile_platform):
			raise UserProfileAlreadyExistsException

		document={
			"profile_uuid": str(profile_uuid),
			"profile_user_name": profile_user_name,
			"profile_platform": profile_platform
		}
		self._user_profiles_collection.insert_one(document)