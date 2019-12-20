from pypot.creatures import PoppyTorso
from pypot.server.httpserver import HTTPRobotServer

poppy = PoppyTorso()
print('Poppy ready')
server = HTTPRobotServer(poppy, host='localhost', port=8080)
print('Starting server')
server.run(quiet=False, server='tornado')
