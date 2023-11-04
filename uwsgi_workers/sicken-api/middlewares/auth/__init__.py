from exceptions import UserDoNotExist, PasswordDoNotMatch

from uuid import uuid4
from hashlib import sha256

class Auth:
    def __init__(self, root):
        self._root=root

        self.log=self._root.log
        self.db=self._root.db

        
    def login(self, user_email:str, user_password:str, **kwargs):
        user=self.db.get_user_by_user_email(user_email=user_email)
        if not user:
            raise UserDoNotExist
        
        session=self.db.get_session_by_user_email(user_email=user['user_email'])
        password_hash=sha256(user_password.encode('utf-8')).hexdigest()

        if password_hash==user['password_hash']:
            self.log.success(f'Password for {user["user_email"]} is correct')
            
            if not session:
                self.log.info(f'Existing session for user {user["user_email"]} weren\'t been found. Creating new one...')
                    
                session_uuid=uuid4()
                session=self.db.create_session(
                    user_email=user['user_email'],
                    session_uuid=session_uuid,
                    user_uuid=user['user_uuid']
                    )
                
                self.log.success(f'Session for {user["user_email"]} has been created successfully')
        
            return session

        else:
            self.log.warning(f'Password for user {user["user_email"]} is wrong.')
            raise PasswordDoNotMatch
    
    def logout(self, user_email:str, session_uuid:str, **kwargs):
        
        status=self.db.remove_session(
            user_email=user_email,
            session_uuid=session_uuid
            )
        if status:
            self.log.info(f'User {user_email} logged out successfully.')

        else:
            self.log.error(f'Attempt to log out user {user_email} failed.')
        return status
        