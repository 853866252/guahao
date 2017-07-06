import werobot

robot = werobot.WeRoBot(token='ce1Jcs')

@robot.text
def hello_world(message,session):

    return session


robot.config['HOST'] = '172.17.76.183'
robot.config['PORT'] = 80

robot.run()