# Turns portrait images into landscape wallpapers

from PIL import Image as i
from PIL import ImageFilter, ImageOps
import math, time

while True:
	try:
		path = input('>> Enter image path:   ')
		img = i.open(path)
		break
	except (AttributeError, FileNotFoundError, OSError) as e:
		print('>> Error.\n')

print('>> Opening image...')
wid, hei = math.ceil(img.size[1]*(16/9)), img.size[1] # Working out 16:9 width for original height

# print(f'>> Orig size:   {img.size}')
# print(f'>> New size:   {wid, hei}')

mode = 'RGB'
bkg = i.new(mode, (wid, hei)) # Background

def split(pos): # Splits image in 2 and puts top half on the left and bottom on the right
	imgcent = math.ceil(hei/2) # Image center
	blur = hei/200

	if pos == 't':
		print('>> Creating left background...')
		s = img.crop(box=(0,0,img.size[0],imgcent)) # Cropping image - 4 tuple: left,top,right,bottom
		sr = s.resize(tuple(z*2 for z in s.size)) # Scaling up by 2 because img was split in two
		sb = sr.filter(ImageFilter.GaussianBlur(radius=blur)) # Gaussian blur
		return sb
	elif pos == 'b':
		print('>> Creating right background...')
		s = img.crop(box=(0,imgcent,img.size[0],img.size[1]))
		sr = s.resize(tuple(z*2 for z in s.size))
		sb = sr.filter(ImageFilter.GaussianBlur(radius=blur))
		return sb

## Working out where top and bottom splits are to be pasted
print('>> Calculating dimensions...')
sw = math.ceil((wid-img.size[0])/2) # split width

tspos = (math.ceil((sw/2)-img.size[0]),0) # Top split position
bspos = (math.ceil((wid-sw/2) - img.size[0]),0) # Bottom split position

print('>> Creating background...')
bkg.paste(split('t'), box=tspos)
bkg.paste(split('b'), box=bspos)

bkg.paste(img, box=(math.ceil((wid/2)-(img.size[0]/2)), 0)) # Paste original image in the center of new image
#bkg = ImageOps.expand(bkg,border=wid//100,fill='black')

print('>> Exporting image...')
dt = time.strftime('%d-%m-%y_%H-%M-%S')
bkg.save(f'wallpaper-{dt}.png')
bkg.show()