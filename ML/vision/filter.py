# image filter or convolution
import sys
import cv2 as cv
import numpy as np

filter_kernels = dict(
	lowpass=np.array([0.11]*9).reshape(3, 3),
	gaussian=np.array([
		[1,4,7,4,1],
		[4,16,26,16,4],
		[7,26,41,26,7],
		[4,16,26,16,4],
		[1,4,7,4,1]])/273.0,
	sharpeness=np.array([[0,-2,0],[-2,9,-2],[0,-2,0]]),
	edgedetection=np.array([[-1,-1,-1],[-1,8,-1],[-1,-1,-1]]),
	emboosing=np.array([
		[-2,-2,-2,-2,0],
		[-2,-2,-2,0,2],
		[-2,-2,0,2,2],
		[-2,0,2,2,2],
		[0,2,2,2,2],
		]),
	)

def main(path):
	image = cv.imread(path)
	print('input image shape', image.shape)
	cv.imshow('origin', image)
	results = []
	for name, kernel in filter_kernels.items():
		print('image filter', name)
		res = cv.filter2D(image, -1, kernel)
		results.append((name, res))
		cv.imshow(name, res)
	key = cv.waitKey(0)
	if key == ord('s'):
		for name, r in results:
			cv.imwrite(name + '.png', r)
	cv.destroyAllWindows()

if __name__ == '__main__':
	if len(sys.argv) > 1:
		main(sys.argv[1])
