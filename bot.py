import modules
import os
import re
import os
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from flask import Flask, request


app = Flask(__name__)
GROUPS = {
    46649296: {"name": "Main Yale chat", "bot_id": "1520c98b3da635c8c6383951a6"},
}
commands = {
    "zalgo": modules.Zalgo(),
    "flip": modules.Flip(),
    "countdown": modules.Countdown(),
    "vet": modules.Vet(),
    "bulldog": modules.Bulldog(),
    "groups": modules.Groups(),
}

F_PATTERN = re.compile('can i get an? (.+) in the chat', flags=re.IGNORECASE | re.MULTILINE)
@app.route("/", methods=["POST"])
def webhook():
    """
    Receive callback to URL when message is sent in the group.
    """
    # Retrieve data on that single GroupMe message.
    message = request.get_json()
    group_id = int(message["group_id"])
    text = message["text"]
    print("Message received: %s" % message)
    matches = F_PATTERN.match(message["text"])
    if matches is not None and len(matches.groups()):
        reply(matches.groups()[0] + ' ❤', group_id)
    if message["sender_type"] != "bot":
        if text.startswith("!"):
            instructions = text[1:].split(" ", 1)
            command = instructions.pop(0).lower()
            query = instructions[0] if len(instructions) > 0 else None
            response = commands[command].response(query)
            if response is not None:
                reply(response, group_id)
        if "thank" in text.lower() and "yalebot" in text.lower():
            reply("You're welcome! :)", group_id)
        if "dad" in text.lower():
            new_text = text.strip().replace("dad", "dyd").replace("Dad", "Dyd").replace("DAD", "DYD")
            reply("Hey " + message["name"] + ", did you mean \"" + new_text + "\"?", group_id)
    if message["system"]:
        if not text.startswith("Poll '") and text.contains("the group") and not text.contains("changed name"):
            name = text.replace(" has rejoined the group", "").replace(" has joined the group", "")
            reply(commands["vet"].check_user(name), group_id)
    return "ok", 200

def reply(text, group_id):
    """
    Reply in chat.
    :param text: text of message to send.
    :param group_id: ID of group in which to send message.
    """
    url = "https://api.groupme.com/v3/bots/post"
    data = {
        "bot_id": GROUPS[group_id]["bot_id"],
        "text": text,
    }
    request = Request(url, urlencode(data).encode())
    response = urlopen(request).read().decode()
    print("Response after message send: %s" % response)

if __name__ == "__main__":
    print(commands["countdown"].response(""))
    print(commands["groups"].response(""))
