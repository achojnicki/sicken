class sessions:
    def get_session_by_session_uuid(self, session_uuid:str):
        query={'session_uuid':session_uuid}

        session=self.sessions.find_one(query)
        return session

    def get_session_by_user_uuid(self, user_uuid:str):
        query={'user_uuid':user_uuid}

        session=self.sessions.find_one(query)
        return session

    def get_session_by_user_email(self, user_email:str):
        query={'user_email':user_email}

        session=self.sessions.find_one(query)
        return session

    def create_session(self, user_email, session_uuid:str, user_uuid:str):
        item={
            "session_uuid":str(session_uuid),
            "user_email":user_email,
            "user_uuid":user_uuid
        }

        self.sessions.insert_one(item)
        return item


    def remove_session(self, user_email:str,  session_uuid:str):
        query={
            'user_email':user_email,
            "session_uuid":session_uuid
            }
        try:
            self.sessions.delete_one(query)
            return True
        except:
            return False
        
        
    def session_exists(self, session_uuid:str, **kwargs):
        session=self.get_session_by_session_uuid(
            session_uuid=session_uuid
            )
        return True if session else False
    