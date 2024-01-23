def run_in_process(func, *args):
    from multiprocessing import Process, Queue
    exception_queue = Queue()

    def my_func(queue, *args):
        try:
            func(*args)
        except Exception as e:
            queue.put(e)

    p = Process(target=my_func, args=(exception_queue, ) + args)
    p.start()
    p.join()
    if not exception_queue.empty():
        raise exception_queue.get()
