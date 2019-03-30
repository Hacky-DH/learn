#!/usr/bin/env python
import time
import gevent
from gevent.threadpool import ThreadPool
import numpy as np

def qsort(array):
	"""quick sort"""
	if len(array) < 2:
		return array
	pivot = array[0]
	return qsort([x for x in array[1:] if x < pivot])+[pivot]+qsort([x for x in array[1:] if x >= pivot])

if __name__ == '__main__':
	pool = ThreadPool(3)
	start = time.time()
	data = np.arange(10000)
	np.random.shuffle(data)
	for _ in range(4):
	    pool.spawn(qsort, data)
	gevent.wait()
	delay = time.time() - start
	print('Running qsort seconds: %.3fs' % delay)