import azure.functions as func
import logging
from azure.identity import UsernamePasswordCredential
import os
from loguru import logger

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

scope = 'https://graph.microsoft.com/.default'
graph_tenantid = os.getenv("graph_tenantid")
graph_clientid = os.getenv("graph_clientid")
graph_username = os.getenv("graph_username")
graph_password = os.getenv("graph_password")

@app.route(route="token/graph/teams")
@app.function_name("TokenManager")
def get_graph_teams_token(req: func.HttpRequest) -> func.HttpResponse:
    
    try:
        
        if "X-FORWARDED-FOR" in req.headers:
            source_ip = req.headers["X-FORWARDED-FOR"].split(':')[0]
            logger.info(f'client {source_ip} requesting AAD access token for MS Graph API for Teams')
        else:
            logger.info(f'client requesting AAD access token for MS Graph API for Teams')

        cred = UsernamePasswordCredential(client_id=graph_clientid, username=graph_username, password=graph_password, tenant_id=graph_tenantid)
        token = cred.get_token(scope)
        
        logger.info(f'token successfully aquired')
        
        return func.HttpResponse(token.token)
    
    except Exception as e:
        logger.error(f'error: {e}')
        return func.HttpResponse(f"internal server error {str(e)}")
            

    # if name:
    #     return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
    # else:
    #     return func.HttpResponse(
    #          "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
    #          status_code=200
    #     )