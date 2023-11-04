from exceptions import ValidationError
from api.log_handle import Log_Handle
from api.form_validator import Form_Validator
from db import DB
from response import Response
from endpoints import Endpoints
from middlewares import Middlewares

from adisconfig import adisconfig
from log import Log

from flask import Response as Flask_Response

class API:
    project_name="sicken-api"
    def __init__(self):
        self.config=adisconfig('/opt/adistools/configs/sicken-api.yaml')

        self.log=Log(
            parent=self,
            rabbitmq_host=self.config.rabbitmq.host,
            rabbitmq_port=self.config.rabbitmq.port,
            rabbitmq_user=self.config.rabbitmq.user,
            rabbitmq_passwd=self.config.rabbitmq.password,
            debug=self.config.log.debug,
            )

        self.log.info('Starting initialization of sicken-api')
        
        self.db=DB(self)
        self.middlewares=Middlewares(self)
        self.log_handle=Log_Handle(self)
        self.endpoints=Endpoints(self)
        self.form_validator=Form_Validator(self)
            
        self.log.success('Initialisation of sicken-api succeed')

    def router(self, target, args, request):      
        """Router method - all valid traffic goes through this method"""
        if not self.check_if_target_exists(target):
            rsp=Response()
            rsp.status="Error"
            rsp.message="Not Found - Endpoint does not exist."
            return Flask_Response(rsp, mimetype="application/json", status=404)
                 

        try:
            self.form_validator.validate(target, args)

        except ValidationError as e:
            rsp=Response()
            rsp.status="Error"
            rsp.message="Bad Request - Validation Error"
            rsp.data=e.error
            return Flask_Response(rsp, mimetype="application/json", status=400)


        #check if the endpoint require login. If so check if the session_uuid were provided and check existance of the session in the DB
        if self._check_if_login_is_required(target):
            if not self.db.session_exists(args['session_uuid']):
                rsp=Response()
                rsp.status='Error'
                rsp.message='Unauthorized - This endpoint do require a valid session'
            
                return Flask_Response(rsp, mimetype="application/json", status=401)
        
        self.log_handle.request=request
        

        #call the endpoint
        try:
            self.log.info('Processing of request started')
            response=Flask_Response(
                getattr(self.endpoints,target)(**args),
                mimetype="application/json"
                )
            self.log.success('Processing of request finished')
            return response
        except Exception as e:
            self.log.error('Exception')
            raise
            rsp=Response()
            rsp.status='Error'
            rsp.status='Internal Server Error - During processing this request exception occured. Try agin later'

            return Flask_Response(rsp, mimetype='application/json', status=500)
    
    def check_if_target_exists(self, target):
        return hasattr(self.endpoints, target)

    def _check_if_login_is_required(self, target):
        if getattr(self.endpoints, target) in self.endpoints._endpoints_with_required_login:
            return True
        return False

    
    def error(self, error):
        """handler for error pages"""

        rsp=Response()
        rsp.status='Error'
        rsp.message=error.description 
        
        return Flask_Response(rsp, mimetype="application/json", status=error.code)