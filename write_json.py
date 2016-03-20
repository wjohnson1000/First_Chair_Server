import json
import os

client_info = {
  "web": {
    "client_id": os.environ.get("client_id"),
    "Project_id": os.environ.get("Project_id"),
    "auth_uri": os.environ.get("auth_uri"),
    "token_uri": os.environ.get("token_uri"),
    "auth_provider_x509_cert_url": os.environ.get("auth_provider_x509_cert_url"),
    "client_secret": os.environ.get("client_secret"),
    "redirect_uris":[os.environ.get("redirect_uris")]
  }
}

with open('secrets_from_env.json', 'w') as f:
  json.dump(client_info, f)
