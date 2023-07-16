import azure.functions as func
import logging
from azure.identity import UsernamePasswordCredential
import os
import logging
import json
import requests
from requests_toolbelt.utils import dump

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

scope = 'https://graph.microsoft.com/.default'
graph_tenantid = os.getenv("graph_tenantid")
graph_clientid = os.getenv("graph_clientid")
graph_username = os.getenv("graph_username")
graph_password = os.getenv("graph_password")

@app.route(route="teams/channel/send", methods=["POST"])
@app.function_name("TeamsChannelSend")
def get_graph_teams_token(req: func.HttpRequest) -> func.HttpResponse:
    
    try:
        
        if "X-FORWARDED-FOR" in req.headers:
            source_ip = req.headers["X-FORWARDED-FOR"].split(':')[0]
            logging.info(f'client {source_ip} requesting AAD access token for MS Graph API for Teams')
        else:
            logging.info(f'client requesting AAD access token for MS Graph API for Teams')
        
        byteBody = req.get_body()
        
        if byteBody == b'':
            return func.HttpResponse('No message found', status_code=400) 
        
        body = json.loads(byteBody)
        
        if 'message' not in body:
            return func.HttpResponse('No message found') 
        
        token = get_bearer_token()
        
        message = body['message']
        
        if 'mapping' in body:
            mapping = body['mapping']
            for item in mapping:
                teamId = item['teamId']
                channelId = item['channelId']
                teamsUrl = f'https://graph.microsoft.com/v1.0/teams/{teamId}/channels/{channelId}/messages'
                http_call(teamsUrl, token, message)
        
        logging.info(f'token successfully aquired')
        
        return func.HttpResponse('', status_code=200)
    
    except Exception as e:
        logging.error(f'error: {e}')
        return func.HttpResponse(f"internal server error {str(e)}", status_code=500)

def get_bearer_token() -> str:
    cred = UsernamePasswordCredential(
        client_id=graph_clientid, 
        username=graph_username, 
        password=graph_password, 
        tenant_id=graph_tenantid)
    
    token = cred.get_token(scope)  
    
    return token.token
    
def http_call(url, token, message):
    data = message
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    body = {
        "body": {
            "content": message
        }
    }


    response = requests.post(url, data=json.dumps(body), headers=headers)
    data = dump.dump_all(response)
    logging.info(data.decode('utf-8'))
