import os
import torch
import pandas as pd
from skimage import io, transform
import numpy as np
import matplotlib.pyplot as plt
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, utils
import torchvision.models as models

# ref https://pytorch.org/tutorials/beginner/data_loading_tutorial.html

# Ignore warnings
import warnings
warnings.filterwarnings("ignore")

plt.ion()   # interactive mode

img_name = r''
img = io.imread(img_name)
plt.imshow(img)
plt.pause(5)
plt.show()

from win32api import GetSystemMetrics
print("Width =", GetSystemMetrics(0))
print("Height =", GetSystemMetrics(1))
