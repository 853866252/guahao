import werobot

robot = werobot.WeRoBot(token='ce1Jcs')

@robot.text
def hello_world(message):
    return message.content


robot.config['HOST'] = '172.17.76.183'
robot.config['PORT'] = 80

robot.run() 