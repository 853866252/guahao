import werobot

robot = werobot.WeRoBot(token='ce1JcsAyhGdXx5IKdOa')

@robot.text
def hello_world():
    return 'Hello World!'

robot.config['HOST'] = '101.200.49.167'
robot.config['PORT'] = 80

robot.run()