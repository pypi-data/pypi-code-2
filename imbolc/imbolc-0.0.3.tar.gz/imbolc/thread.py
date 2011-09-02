# -*- coding: utf-8 -*-
'''
om_thread.py - многопоточный генератор
'''
import sys
import threading
import time
import Queue

thread = sys.modules[__name__]  # for auto-import
END = object()  # стоп-значение для потока


def main():
    '''
    Пример использования
    '''
    def tst(i):
        print '-> %i' % i
        time.sleep(0.1)
        return '<- %i' % i
    
    # получаем результаты по ходу вычислений
    for s in run(tst, xrange(100), 3):
        print s
        
    # если результаты не нужны
    list(run(tst, xrange(100), 3))
        

def run(callback, tasks, thread_limit, queue_limit=None, sleep=0.01):
    '''
    Многопоточный генератор, на вход:
        callback        - рабочая функция (или запускаемый объект)
        tasks           - задачи для callback, любой итерируемый тип
        thread_limit    - количество потоков
        queue_limit     - максимальный размер очереди заданий
        sleep           - время сна в цикле (для уменьшения загрузки процессора)
    '''
    
    queue = Queue.Queue(queue_limit)
    tasks = iter(tasks)
    pool = []
    ret_queue = Queue.Queue()
    queue_limit = queue_limit if queue_limit else thread_limit * 5
    
    while True:
        # возвращаем результат
        while not ret_queue.empty():
            yield ret_queue.get()
                
        # проверяем работоспособность потоков
        pool = filter(lambda x: x.isAlive(), pool)

        # добавляем недостающие потоки
        while len(pool) < thread_limit:
            th = Th(callback, queue, ret_queue)
            th.setDaemon(True)
            th.start()
            pool.append(th)
            
        # заполняем очередь заданий
        while queue.qsize() < queue_limit:
            try:
                task = tasks.next()
            except StopIteration:
                break
            queue.put(task)
        else:
            # задания ещё не кончились
            time.sleep(sleep)
            continue
        break
        
    # отключаем потоки
    for th in pool:
        queue.put(END)

    # ожидаем завершения потоков
    for th in pool:
        th.join()
    
    # отдаём остатки
    while not ret_queue.empty():
        yield ret_queue.get()


class Th(threading.Thread):
    '''
    Поток
    '''
    def __init__(self, callback, queue, ret_queue=None):
        self.callback = callback
        self.queue = queue
        self.ret_queue = ret_queue
        threading.Thread.__init__(self)
        
    def run(self):
        while True:
            args = self.queue.get()
            if args is END:
                break
            ret = self.callback(args)
            if self.ret_queue:
                self.ret_queue.put(ret)


if __name__ == "__main__":
    main()
