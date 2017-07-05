import werobot

robot = werobot.WeRoBot(token='ce1JcsAyhGdXx5IKdOa')

@robot.text
def hello_world():
    return 'Hello World!'

#robot.config['HOST'] = '127.0.0.1'
#robot.config['PORT'] = 80

robot.run()