import json
import os
from flask import Flask, render_template, request
from llama_cpp import Llama
import uuid
from azure.messaging.webpubsubservice import WebPubSubServiceClient
from azure.messaging.webpubsubclient import WebPubSubClient, WebPubSubClientCredential
from azure.messaging.webpubsubclient.models import (
    OnConnectedArgs,
    OnGroupDataMessageArgs,
    OnDisconnectedArgs,
)

app = Flask(__name__, static_url_path='', template_folder="web/templates", static_folder="web/static")
# connection_string = os.environ['WEBPUBSUB_CONNECTION_STRING']
connection_string = ""
service = WebPubSubServiceClient.from_connection_string(connection_string=connection_string, hub='hub')
llm = Llama(model_path="../../../module/llama-2-7b-chat.Q2_K.gguf")
serverGroup = "serverGroup"
clientGroup = "clientGroup"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/negotiate')
def negotiate():
    userId = request.args.get('userId')
    return service.get_client_access_token(user_id=userId, roles=['webpubsub.joinLeaveGroup', 'webpubsub.sendToGroup'])

def on_group_message(msg: OnGroupDataMessageArgs):
    print(f"Received message {msg.data}")
    data = msg.data
    
    if data["event"] == "broadcastMessage":
        args = data["args"]
        client.send_to_group(clientGroup, {"name": args[0], "id":"", "message": args[1]}, "json", no_echo=False, ack=False)
    elif data["event"] == "echo":
        args = data["args"]
        client.send_to_group(args[0], {"name": args[0], "id":"", "message": args[1]}, "json", no_echo=False, ack=False)
    elif data["event"] == "inference":
        username = data["args"][0]
        prompt = data["args"][1]
        id = str(uuid.uuid4())
        stream = llm(
            "User {0}: {1}".format(username, prompt),
            max_tokens=128,
            stop=["Q:", "\n"],
            stream=True,
        )
        for output in stream:
            value = output["choices"][0]["text"]
            client.send_to_group(clientGroup, {"name": "LLAMA", "id":id, "message": value}, "json", no_echo=False, ack=False )


def bindMessage(client: WebPubSubClient):
    client.on("group-message", on_group_message)
    

if __name__ == '__main__':
    client = WebPubSubClient(credential=WebPubSubClientCredential(
            client_access_url_provider=lambda: service.get_client_access_token(
                roles=["webpubsub.joinLeaveGroup", "webpubsub.sendToGroup"]
            )["url"]
        ))
    with client:
        client.join_group(serverGroup)
        bindMessage(client)
        app.run()
