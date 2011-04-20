'''
Created on May 16, 2009

@author: felipe
'''

class Publisher:
    def __init__(self):
        self.subscribers = []
        
    def register(self, subscriber):
        self.subscribers.append(subscriber)
        
    def publish(self, message):
        for subscriber in self.subscribers:
            subscriber.receive(message)
    
    def close(self):
        for subscriber in self.subscribers:
            subscriber.close()
