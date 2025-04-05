from response import Response
from exceptions import UserDoNotExist, PasswordDoNotMatch

class login:
    def login(self, user_email:str, user_password:str):
        try:
            rsp=Response()
            session=self._middlewares.auth.login(
                user_email=user_email,
                user_password=user_password
            )
        
            rsp.status='Success'
            rsp.message='Login Successful'
            rsp.data['session_uuid']=session['session_uuid']
        
        except UserDoNotExist:
            rsp.status='Failed'
            rsp.message='User do not exist'
        
        except PasswordDoNotMatch:
            rsp.status="Failed"
            rsp.message="Wrong password"
        
        return rsp