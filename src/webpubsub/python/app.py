import os
from flask import Flask, render_template, request
from llama_cpp import Llama
from azure.messaging.webpubsubservice import WebPubSubServiceClient

app = Flask(__name__, static_url_path='', template_folder="web/templates", static_folder="web/static")
# connection_string = os.environ['WEBPUBSUB_CONNECTION_STRING']
connection_string = ""
service = WebPubSubServiceClient.from_connection_string(connection_string=connection_string, hub='hub')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/negotiate')
def negotiate():
    userId = request.args.get('userId')
    return service.get_client_access_token(user_id=userId, roles=['webpubsub.joinLeaveGroup', 'webpubsub.sendToGroup'])

if __name__ == '__main__':
    llm = Llama(model_path="../../../module/llama-2-7b.Q2_K.gguf")
    output = llm("Q: Name the planets in the solar system? A: ", max_tokens=32, stop=["Q:", "\n"], echo=True)
    print(output)
    app.run(debug=True)
