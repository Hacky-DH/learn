#!/bin/env python
# rename files from their mtime
import os
import sys
from datetime import datetime

DEFAULT_EXT=('.png','.jpg','.bmp')

def main(path, ext=DEFAULT_EXT):
	if not os.path.exists(path):
		print(path, 'not exists')
		return 1
	if os.path.isfile(path):
		rename(path)
	elif os.path.isdir(path):
		for p in os.listdir(path):
			if p.lower().endswith(ext):
				rename(p)
	else:
		print(path, 'not support')
		return 1
	return 0

def rename(path):
	mtime = os.path.getmtime(path)
	mtime = datetime.fromtimestamp(mtime)
	file_prefix = mtime.strftime('%Y%m%d_%H%M%S_')
	path_, file = os.path.split(path)
	if not file.startswith(file_prefix):
		new_path = os.path.join(path_, file_prefix + file)
		os.rename(path, new_path)
		print('rename to', new_path)

if __name__ == '__main__':
	if len(sys.argv) > 1:
		main(sys.argv[1])
