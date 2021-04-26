from flask import Flask 
from flask_httpauth import HTTPDigestAuth
import sys  # For simplicity, we'll read config file from 1st CLI param sys.argv[1]
import json
import logging

import requests
import msal


#tent_id = "2dff09ac-2b3b-4182-9953-2b548e0d0b39"
#client_id = "52e70339-963b-4bf1-9f1b-25c34d4e6f47"
#cert_path = "server.pem"
config = json.load(open('params.json'))

def getSecret(config):
    app = msal.ConfidentialClientApplication(
    config["client_id"], authority=config["authority"],
    client_credential={"thumbprint": config["thumbprint"], "private_key": open(config['private_key_file']).read()},
    # token_cache=...  # Default cache is in memory only.
                       # You can learn how to use SerializableTokenCache from
                       # https://msal-python.readthedocs.io/en/latest/#msal.SerializableTokenCache
    )
    #graph api vault
    endpoint = config["vault_url"] + "secrets/" + config["secretName"] + "?api-version=2016-10-01"
    result = app.acquire_token_for_client(scopes=config["scope"])
    
    if "access_token" in result:
        print(result)
    # Calling graph using the access token
        graph_data = requests.get(  # Use token to call downstream service
            endpoint,
            headers={'Authorization': 'Bearer ' + result['access_token']},).json()
        print("Graph API call result: %s" % json.dumps(graph_data, indent=2))
        return graph_data['value']

app = Flask(__name__) 
app.config['SECRET_KEY'] = '123456' 
auth = HTTPDigestAuth()
secretKey = getSecret(config) 
print(secretKey) 
users = { "api": secretKey }

@auth.get_password 
def get_pw(username): 
    if username in users: 
        return users.get(username) 
    return None

@app.route('/') 
@auth.login_required 
def index(): 
    return "Hello, {}!".format(auth.username())

if __name__ == '__main__': 
    app.run()