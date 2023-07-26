import azure.functions as func
import logging
from azure.identity import UsernamePasswordCredential
import os
import logging
import json
import requests
from requests_toolbelt.utils import dump
import traceback
import yaml

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

scope = 'https://graph.microsoft.com/.default'
graph_tenantid = os.getenv("graph_tenantid")
graph_clientid = os.getenv("graph_clientid")
graph_username = os.getenv("graph_username")
graph_password = os.getenv("graph_password")

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="teams/channel/send", methods=["POST"])
@app.function_name("TeamsChannelSend")
def get_graph_teams_token(req: func.HttpRequest) -> func.HttpResponse:
    
    try:
        
        if "X-FORWARDED-FOR" in req.headers:
            source_ip = req.headers["X-FORWARDED-FOR"].split(':')[0]
            logging.info(f'client {source_ip} requesting AAD access token for MS Graph API for Teams')
        else:
            logging.info(f'client requesting AAD access token for MS Graph API for Teams')
        
        bodyStr = req.get_body().decode("utf-8") 
        
        logging.info(f'received request with body: {bodyStr}')
        
        if not is_message_valid(bodyStr):
            return func.HttpResponse('request does not contain valid message', status_code=400) 

        bodyDict = json.loads(bodyStr, strict=False)
        
        message = bodyDict['message']
        
        yamlStr = bodyDict['mapping']
        
        try:
            mapping = yaml.safe_load(yamlStr)
        except Exception as e:
            logging.info(f'error parsing yaml teams-channcel-id-mapping: {str(e)}')
            return func.HttpResponse(f"error parsing yaml teams-channcel-id-mapping: {str(e)}", status_code=400)
        
        token = get_bearer_token()
        
        mapping = mapping['mapping']
        for item in mapping:
            teamId = item['teamId']
            channelId = item['channelId']
            teamsUrl = f'https://graph.microsoft.com/v1.0/teams/{teamId}/channels/{channelId}/messages'
            http_call(teamsUrl, token, message)
            logging.info(f'message sent to channel {teamsUrl}')
            
        
        logging.info(f'message successfully sent to {len(mapping)} Teams channel(s)')
        
        return func.HttpResponse('', status_code=200)
    
    except Exception as e:
        stacktraces = get_stacktrace()
        logging.error(f'error: {str(e)}, stacktrace: {stacktraces}')
        return func.HttpResponse(f"internal server error {stacktraces}", status_code=500)


def is_message_valid(body: str):
    bodyJson = json.loads(body, strict=False)
    
    if bodyJson == '' or 'message' not in bodyJson or 'mapping' not in bodyJson:
        return False
    
    return True

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
    
def get_stacktrace() -> str:
    stacktraces = []
    for line in traceback.format_stack():
        stacktraces.append(line.strip())
        return ''.join(stacktraces)
