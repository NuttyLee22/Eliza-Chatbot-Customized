from flask import Flask, render_template, url_for, request
import random
import string
from dadjokes import Dadjoke
import re

app = Flask(  # Create a flask app
    __name__,
    template_folder='templates',  # Name of html file folder
    static_folder='static'  # Name of directory for static files
)

# Eliza word lists
terminal = "!.?"

sadwords = ["sad", "depressed", "lonely", "tired", "exhausted",
            "meaningless", "worthless", "horrible", "hate"]

happywords = ["happy", "good", "glad", "joy", "excite", "great", "amazing"]

deadconvo = ["yea", "yes", "cool", "ok", "okay", "k", "nice", "lol", "lmao"]

resp = {"* i am * because i am *": [lambda wc: "How is you being " + wc[2] + " related to being " + wc[1] + "?"], "* i feel * because *": [lambda wc: "How is " + wc[2] + " related to you feeling " + wc[1] + "?", lambda wc: "Has " + wc[2] + " reallly made you feel " + wc[1] + "?", lambda wc: "Has " + wc[2] + " always made you feel " + wc[1] + "?"], "* i love * because *": [lambda wc: "How is " + wc[2] + " related to you loving " + wc[1] + "?"], "* i want * because *": [lambda wc: "Why does " + wc[2] + " make you want " + wc[1] + "?"], "* i am * because *": [lambda wc: "What about " + wc[2] + " makes you " + wc[1] + "?"], "* i am *": [lambda wc: "Why are you " + wc[1] + "?", lambda wc: "How long have you been " + wc[1] + "?", lambda wc: "Do you think it is normal to be " + wc[1] + "?", lambda wc: "Hi " + wc[1] + ", I am Daddy;)"], "* i feel *": [lambda wc: "Why do you feel " + wc[1] + "?", lambda wc: "Do you enjoy feeling " + wc[1] + "?", lambda wc: "What does feeling " + wc[1] + " remind you of?", lambda wc: "Do you often feel " + wc[1] + "?"], "* you are *": [lambda wc: "Why am I " + wc[1] + "?", lambda wc: "oh am I now;)", lambda wc: "Do you wish I was " + wc[1] + "?", lambda wc: "Am I " + wc[1] + " in your fantasies?", lambda wc: "Are you pleased to believe that I am " + wc[1] + "?"], "* i want *": [lambda wc: "What does " + wc[1] + " mean to you?", lambda wc: "Do you really want to be able to " + wc[1] + "?", lambda wc: "What if you never get " + wc[1] + "?", lambda wc: "Do you really think you deserve " + wc[1] + "?"], "* i love *": [lambda wc: "Why do you love " + wc[1] + "?",
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            lambda wc: "How strongly do you love " + wc[1] + "?", lambda wc: "Have you always loved " + wc[1] + "?", lambda wc: "Does " + wc[1] + " make you tingle inside?", lambda wc: "Do you deserve " + wc[1] + "?"], "* i like *": [lambda wc: "What about " + wc[1] + " appeals to you?"], "* i believe *": [lambda wc: "Why do you believe " + wc[1] + "?", lambda wc: "What has made you believe " + wc[1] + "?", lambda wc: "When did you start believing " + wc[1] + "?"], "* i have *": [lambda wc: "How long have you had " + wc[1] + "?", lambda wc: "When did you get " + wc[1] + "?"], "* are you *": [lambda wc: "Do you believe I am " + wc[1] + "?", lambda wc: "What makes you think that I am " + wc[1] + "?", lambda wc: "Why do you ask if I am " + wc[1] + "?", lambda wc: "Do you want me to be " + wc[1] + "?"], "* i cant *": [lambda wc: "Why can't you?"], "* i can *": [lambda wc: "Can you really " + wc[1] + "?", lambda wc: "Prove it", lambda wc: "Are you sure you can " + wc[1] + "?"], "* why are *": [lambda wc: "Do you believe that everything needs an explanation?", lambda wc: "The explanation is rather complicated"], "* i do *": [lambda wc: "Why do you " + wc[1] + "?"], "because *": [lambda wc: "Why do you believe that?", lambda wc: "Have you always believed that?"], "* what is *": [lambda wc: "Some things are better left unanwsered", lambda wc: "What do you think " + wc[1] + " is?"], "* is *": [lambda wc: "How does " + wc[0] + " being " + wc[1] + " make you feel?", lambda wc: "Why do you think that " + wc[0] + " is " + wc[1] + "?"], "my day *": [lambda wc: "What has made your day " + wc[0] + "?"]}

# Eliza functions
def cleaning(msg):
    msg = msg.lower()
    msg = msg.replace("'", "")
    msg = msg.replace("’", "")

    # contractions
    msg = msg.replace(" u ", "you")
    msg = msg.replace("wanna", "want")
    msg = msg.replace("i dont know", "idk")
    msg = msg.replace("how are you", "hru")
    msg = msg.replace("im", "i am")
    msg = msg.replace("youre", "you are")
    msg = msg.replace("just", "")

    msg = msg.strip()

    return msg


def changePronouns(msg):
    msg = msg.split(" ")
    # change pronouns
    for i in range(len(msg)):
        if msg[i] == "you":
            msg[i] = "me"
        elif msg[i] == "me":
            msg[i] = "you"
        if msg[i] == "i":
            msg[i] = "you"
        elif msg[i] == "you":
            msg[i] == "me"
        if msg[i] == "my":
            msg[i] = "your"
        elif msg[i] == "your":
            msg[i] = "my"
        if msg[i] == "myself":
            msg[i] = "yourself"
        elif msg[i] == "yourself":
            msg[i] = "myself"
        if msg[i] == "mine":
            msg[i] = "yours"
        elif msg[i] == "yours":
            msg[i] = "mine"

    msg = " ".join(msg)
    return msg

def match_rule(rule, sentence):
    wildcardarr = []
    ruleCounter = 0
    rule = rule.split(" ")
    sentence = sentence.split(" ")
    wildcard = ""
    for i in range(len(sentence)):
        if rule[ruleCounter] == "*":
            # check if wildcard is done
            if ruleCounter < len(rule)-2:
                if sentence[i] == rule[ruleCounter+1]:
                    wildcardarr.append(wildcard.strip(" "))
                    wildcard = ""
                    ruleCounter += 2
                else:
                    # add word to wildcard if wildcard not done
                    wildcard += sentence[i] + " "
            else:
                wildcard = " ".join(sentence[i:])
                wildcardarr.append(wildcard)
                ruleCounter = len(rule)
                break
        elif sentence[i] == rule[ruleCounter]:
            ruleCounter += 1

    if ruleCounter > len(rule)-1:
        return wildcardarr
    else:
        return None

def ifallelsefails(msg, convo):
    msg = msg.translate(str.maketrans('', '', string.punctuation))
    if msg in deadconvo:
        return random.choice(["Wanna hear a joke?", "How has your day been", "Tell me about your childhood", "What can I do to make you feel good;)"])

    for words in sadwords:
        if not msg.find(words) == -1:
            return random.choice(["You sound very sad. I'm sure its not all that bad.", "Are you okay?", "I'm sorry to hear that", "How can I make it better;)"])

    for words in happywords:
        if not msg.find(words) == -1:
            return random.choice(["I'm glad to hear that.", "Hearing that brings me joy!", "Is there anyway I can amplify those emotions;)"])

    if msg:
        for word in msg.split(" "):
            if len(word) > 6 and random.randint(0, 10) > 6:
                return word + "?"

    resps = ["ohh?", "Interesting", "Tell me more", "Can you elaborate?", "What is it you really want to know?", "Why?", "backtrack",
            "Tell me more about your childhood", "What are you getting at?", "Coooool...Wanna hear a joke??"]
    respchoice = random.choice(resps)
    if respchoice == "backtrack":
        if len(convo) > 3:
            pastRespIndex = random.randint(0, len(convo)-1)
            while pastRespIndex % 2 == 0:
                pastRespIndex = random.randint(0, len(convo)-1)
                pastUserResp = convo[pastRespIndex].replace("You:", "")
            return "Okayyyy....'" + pastUserResp + "'...Tell me more"
        else:
            return "What do you want to tell me?"
    else:
        return respchoice

def respond(msg, convo, name):
    previousQuestion = cleaning(convo[len(convo)-1])
    previousQuestion = previousQuestion.translate(
        str.maketrans('', '', string.punctuation))
    msg = msg.replace(name, "")

    if len(convo) > 2:
        pastUsermsg = cleaning(convo[len(convo)-2])
        # remove first word which will be name because cannot garuntee previous name == current name
        pastUsermsg = " ".join(pastUsermsg.split(" ")[1:])
        if pastUsermsg == msg:
            if msg not in deadconvo:
                return "BRUH, why u repeating?"

    if msg.translate(str.maketrans('', '', string.punctuation)) == " ".join(previousQuestion.split(" ")[1:]):
        return "Do you think you gain something by repeating me?"

    if not msg.find("your name") == -1:
        return "my name is whatever you want it to be"

    if not previousQuestion.find("hru") == -1 and not msg.find("wbu") == -1 or not previousQuestion.find("hru") == -1 and not msg.find("wbu") == -1 or not previousQuestion.find("hru") == -1 and not msg.find("hbu") == -1:
        return "I am good, thanks for asking. Now tell me your favorite animal"

    # jokes
    if not previousQuestion.find("hear a joke") == -1 and msg.find("no") == -1:
        return Dadjoke().joke
    elif not previousQuestion.find("hear a joke") == -1:
        return "i don't care..." + Dadjoke().joke

    # pre-programmed responses
    if msg == "idk":
        return "I don't know either...I want you to explain that to me"

    if not msg.find("good morning") == -1:
        return "Good morning!"

    if not msg.find("good night") == -1:
        return "Good night!"

    if msg == "no":
        return "Why so negative?"

    if msg == "hi" or not msg.find("hello") or not msg.find("hey"):
        return random.choice(["HII MY LOVER", "hello my love<3", "HEY HRU?", "hello!", "hi there", "Hi! How are you?", "yahoooo, how is your day?"])

    if not msg.find("hru") == -1:
        return "I am good, but I want to focus on you! So tell me more about how you're feelin?"

    if not msg.find("send") == -1 and not msg.find("joke") == -1 or not msg.find("give me") == -1 and not msg.find("joke") == -1 or not msg.find("tell me") == -1 and not msg.find("joke") == -1:
        return Dadjoke().joke

    # eliza magic
    msgarr = re.split('[?.,]', msg)  # analyze message by sentence
    possibleresp = []
    for words in msgarr:
        for rules in resp:
            response = match_rule(rules, words)
            if not response == None:
                for i in range(len(response)):
                    resps = response[i].split(' ')
                    response[i] = " ".join(resps)
                    response[i] = response[i].translate(
                        str.maketrans('', '', string.punctuation))
                    response[i] = changePronouns(response[i])
                possibleresp.append(random.choice(resp[rules])(response))
                break
    if len(possibleresp) > 0:
        return random.choice(possibleresp)
    else:
        return ifallelsefails(msg, convo)

# Setting up webpage
@app.route('/')
def form():
    return render_template('base.html')

@app.route('/', methods=['POST', 'GET'])
def data():
    if request.method == 'POST':
        form_data = request.form
        userinput = ""
        name = ""
        Elizaname = ""
        # for key, value in form_data.items():
        # if key == 'msg':
        userinput = str(form_data['msg'])
        # if key == 'chatlog':
        convo = str(form_data['chatlog']).split("<li>")
        # if key == 'name':
        name = str(form_data['name']) + ": "
        # if key == 'Elizaname':
        Elizaname = str(form_data['Elizaname']) + ": "
        if not userinput == "":  # make sure that the Eliza does not accept null inputs
            # new resp icludes user (the msg before cleaning) + Eliza's response in one string to send to client
            newresp = name + userinput
            userinput = name + cleaning(userinput)
            response = respond(userinput, convo, name)
            newresp += "<li>" + Elizaname + response
            return newresp
        else:
            return "empty"
        return render_template('base.html')

if __name__ == "__main__":  # Makes sure this is the main process
    app.run(  # Starts the site
        host='0.0.0.0',  # Establishes the host, required for repl to detect the site
        # Randomly select the port the machine hosts on.
        port=random.randint(2000, 9000)
    )
