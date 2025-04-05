class users:
    def get_user_by_user_email(self, user_email):
        query={'user_email':user_email}

        return self.users.find_one(query)

    def get_user_by_user_uuid(self, user_uuid):
        query={'user_uuid':user_uuid}

        return self.users.find_one(query)