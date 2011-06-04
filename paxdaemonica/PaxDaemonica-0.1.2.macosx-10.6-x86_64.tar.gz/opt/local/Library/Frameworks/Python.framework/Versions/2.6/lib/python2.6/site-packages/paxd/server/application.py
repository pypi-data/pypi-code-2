# from paxd.process import print_exc
# from multiprocessing import Pipe, Process
# from Queue import Empty
# 
# def start_appman(name, command_queue, read_q, write_q):
#     AppManager(name, command_queue, read_q, write_q).start()
#     
# class AppManager(object):
#     def __init__(self, name, command_queue, read_q, write_q):
#         self.name = name
#         self.command_queue = command_queue
#         self.read_q = read_q
#         self.write_q = write_q
#     
#     def start(self):
#         while True:
#             with print_exc:
#                 obj = self.read_q.get()
#                 self.handle(obj)
#     
#     def handle(self, obj):
#         # Validate Command
#         if obj == 'APPLIST':
#             self.write_q.put({
#                 'applications' : []
#             })
#             return
#         return {'error' : 'unknown command'}
#         # 
#         # # Execute Command
#         # self.command_queue.put((name, 'APPLIST'))
#         # if controller_pipe.poll(0.8):
#         #     httpserver_pipe.send(controller_pipe.recv())
#         #     return
#         # httpserver_pipe.send('TIMEOUT')
#         # 
