import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
from PIL import Image

cm_hot = mpl.cm.get_cmap('winter')
img_src = Image.open('img.png').convert('L')
# img_src.thumbnail((512,512))
im = np.array(img_src)
im = cm_hot(im)
im = np.uint8(im * 255)
im = Image.fromarray(im)
im.save('test_hot.png')