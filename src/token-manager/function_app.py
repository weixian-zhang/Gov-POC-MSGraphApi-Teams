import azure.functions as func
import logging
from azure.identity import UsernamePasswordCredential
import os
from loguru import logger
import json
import requests

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

scope = 'https://graph.microsoft.com/.default'
graph_tenantid = os.getenv("graph_tenantid")
graph_clientid = os.getenv("graph_clientid")
graph_username = os.getenv("graph_username")
graph_password = os.getenv("graph_password")

@app.route(route="teams/channel/send")
@app.function_name("TeamsChannelSend")
def get_graph_teams_token(req: func.HttpRequest) -> func.HttpResponse:
    
    try:
        
        if "X-FORWARDED-FOR" in req.headers:
            source_ip = req.headers["X-FORWARDED-FOR"].split(':')[0]
            logger.info(f'client {source_ip} requesting AAD access token for MS Graph API for Teams')
        else:
            logger.info(f'client requesting AAD access token for MS Graph API for Teams')
        
        body = json.loads(req.get_body())
        
        if 'message' not in body:
            return func.HttpResponse('No message found') 
        
        token = get_bearer_token()
        
        message = body['message']
        
        if 'mapping' in body:
            mapping = body['mapping']
            for teamId, channelId in mapping:
                teamsUrl = f'https://graph.microsoft.com/v1.0/teams/{teamId}/channels/{channelId}/messages'
                http_call(teamsUrl, token, message)
        
        logger.info(f'token successfully aquired')
        
        return func.HttpResponse(token.token)
    
    except Exception as e:
        logger.error(f'error: {e}')
        return func.HttpResponse(f"internal server error {str(e)}")

def get_bearer_token() -> str:
    cred = UsernamePasswordCredential(
        client_id=graph_clientid, 
        username=graph_username, 
        password=graph_password, 
        tenant_id=graph_tenantid)
    
    token = cred.get_token(scope)  
    
    return token
    
def http_call(url, token, message):
    data = message
    headers = {"Authorization": f"Bearer {token}"}
    logger.info(requests.post(url, data=data, headers=headers).json())
        
    # if name:
    #     return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
    # else:
    #     return func.HttpResponse(
    #          "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
    #          status_code=200
    #     )