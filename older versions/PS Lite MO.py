# PortScape Magma Only Lite version
# Magma maps images in dir and saves them

import os, time, re, mimetypes, math, threading, tkinter
from tkinter import *
from tkinter import filedialog, colorchooser, ttk
import PIL
from PIL import Image as i
from PIL import ImageFilter, ImageOps, ImageDraw, ImageTk
import matplotlib
from matplotlib import pyplot as plt
import numpy as np

options = ['magma', 'magma_r']

def create(file, opt):
	try:
		img = i.open(file)
		pltcm = matplotlib.cm.get_cmap(options[opt]) # color map
		img = img.convert('L')
		img = np.array(img)
		img = pltcm(img)
		img = np.uint8(img*255)
		img = i.fromarray(img)

		dt = time.strftime('%Y-%m-%d_%H-%M-%S')
		global root, fext
		path = f'{root}PSLMOd/{fname.replace(fext,"")}-{options[opt]}.png'

		img.save(path)

	except PIL.UnidentifiedImageError:
		pass

newdir = './PSLMOd/'
try:
	os.mkdir(newdir)
except FileExistsError:
	pass

exclude = set(['PSLMOd'])

for root, dirs, files in os.walk('./', topdown=True):
	dirs[:] = [d for d in dirs if d not in exclude] # Edits dirs list to remove new dir for created images so that program doesnt walk that too
	for fname in files:
		file = f'{root}/{fname}'
		fext = os.path.splitext(file)[1]
		# print(f'{root}')
		try:
			if mimetypes.guess_type(file)[0].startswith('image'):
				print(f'>> Creating magma - {fname}...')
				create(file, 0)
				print(f'>> Creating magma_r - {fname}...')
				create(file, 1)
		except AttributeError:
			pass 
