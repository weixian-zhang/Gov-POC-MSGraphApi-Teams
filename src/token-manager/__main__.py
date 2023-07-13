from flask import Flask
from flask import request
from azure.identity import UsernamePasswordCredential
import os
from loguru import logger

scope = 'https://graph.microsoft.com/.default'
graph_tenantid = os.getenv("graph_tenantid")
graph_clientid = os.getenv("graph_clientid")
graph_username = os.getenv("graph_username")
graph_password = os.getenv("graph_password")

app = Flask(__name__)

@app.route('/token/graphteams')
def get_graphteams_token():
    
    try:
        
        cred = UsernamePasswordCredential(client_id=graph_tenantid, username=graph_username, password=graph_password, tenant_id=graph_tenantid)
        token = cred.get_token(scope)
        
        logger.info(f'token requested from {request.remote_addr}')
        return token.token
    
    except Exception as e:
        logger.error(e)
        return str(e)
    
    
if __name__ == '__main__' or __name__ == 'main':
    app.run(host='0.0.0.0', port=5000)
    


