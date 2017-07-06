import werobot

robot = werobot.WeRoBot(token='ce1Jcs')

@robot.text
def hello_world(message):
    return message.content()


#@robot.text
#def first(message, session):
#    if 'first' in session:
#        return '你之前给我发过消息'
#    session['first'] = True
#    return '你之前没给我发过消息'

robot.config['HOST'] = '172.17.76.183'
robot.config['PORT'] = 80

robot.run()