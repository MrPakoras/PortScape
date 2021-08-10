# v4.6 - Adding more border functions


import os, time, re, mimetypes, math, threading, tkinter
from tkinter import *
from tkinter import filedialog, colorchooser, ttk
from PIL import Image as i
from PIL import ImageFilter, ImageOps, ImageDraw, ImageTk
import matplotlib
from matplotlib import pyplot as plt
import numpy as np

print('>> Running...')

master = Tk()
#master.iconbitmap('tbcarrowicon.ico')
master.title('PortScape v4.6 GUI')
master.geometry('1280x475')
master.resizable(False, False)
master.configure(background='#1d1c2c')
master.columnconfigure(0, weight=2)
#bkg = PhotoImage(file='bkg.png')
#setb = Label(master, image=bkg)
#setb.place(x=0, y=0, relwidth=1, relheight=1)

## Browse for file function
def browse():
	global filename
	filename = filedialog.askopenfilename(initialdir = "/", title = "Select a File")

	if len(filename) != 0:
		if len(filename) >= 45:
			avar = filename[:45]+'...'
		else:
			avar = filename
		addrvar.set(avar)

		if mimetypes.guess_type(filename)[0].startswith('image'):
			mvar = ':)'
			messvar.set(mvar)
			startbutton.config(state='normal')
			previewbutton.config(state='normal')

		else:
			startbutton.config(state='disabled')
			mvar = 'Error. Please choose an image file.'
			messvar.set(mvar)

## Preview button program
def start():
	startbutton.config(state='disabled')
	previewbutton.config(state='disabled')
	browsebutton.config(state='disabled')
	mvar = 'Creating wallpaper. Please wait...'
	messvar.set(mvar)

	### CODE ###
	print('>> Opening image...')
	img = i.open(filename)
	origimg = img # Original image to be used later
	wid, hei = math.ceil(img.size[1]*(16/9)), img.size[1] # Working out 16:9 width for original height

	# print(f'>> Orig size:   {img.size}')
	# print(f'>> New size:   {wid, hei}')

	mode = 'RGBA'
	global bkg
	bkg = i.new(mode, (wid, hei)) # Background

	if cmvar.get() == 1: # Colour map
		if invvar.get() == 1:
			cmblack = cmwvar.get()
			cmwhite = cmbvar.get()
		else:
			cmblack = cmbvar.get()
			cmwhite = cmwvar.get()
		img = img.convert('L') # Convert to greyscale
		img = ImageOps.colorize(img, black=cmblack, white=cmwhite) # colour map

	## Matplotlib colour map

	if plbvar.get() == 0:
		pass
	else:
		print(f'>> Applying {pltvar.get()} colour map...')
		pltcm = matplotlib.cm.get_cmap(pltvar.get()) # color map
		img = img.convert('L')
		img = np.array(img)
		img = pltcm(img)
		img = np.uint8(img*255)
		img = i.fromarray(img)

	## Invert colours

	if icvar.get() == 1: 
		print('>> Inverting image...')
		img = img.convert('RGB')
		# print(img.mode)
		img = ImageOps.invert(img)


	## Gaussian Blur

	blurval = int(blurslider.get()) # Slider value

	if blurval == 0: # Filter options
		pass
	else:
		print('>> Applying Gaussian Blur...')
		# blur = hei/()*8
		img = img.filter(ImageFilter.GaussianBlur(radius=(blurval*0.1))) # Gaussian blur
	
	## Darken

	if fopt.get() == 2 or fopt.get() == 3: # If radio button 2 not chosen
		# https://stackoverflow.com/questions/43618910/pil-drawing-a-semi-transparent-square-overlay-on-image
		ndimg = img # Non darkened image to paste on top
		img = i.eval(img, lambda x: x/1.5)

	## Split image

	def split(pos): # Splits image in 2 and puts top half on the left and bottom on the right
		imgcent = math.ceil(hei/2) # Image center
		
		global fopt

		if pos == 't':
			print('>> Creating left background...')
			s = img.crop(box=(0,0,img.size[0],imgcent)) # Cropping image - 4 tuple: left,top,right,bottom
		elif pos == 'b':
			print('>> Creating right background...')
			s = img.crop(box=(0,imgcent,img.size[0],img.size[1]))	

		sr = s.resize(tuple(z*2 for z in s.size)) # Scaling up by 2 because img was split in two

		return sr

	## Working out where top and bottom splits are to be pasted
	print('>> Calculating dimensions...')
	sw = math.ceil((wid-img.size[0])/2) # split width

	tspos = (math.ceil((sw/2)-img.size[0]),0) # Top split position
	bspos = (math.ceil((wid-sw/2) - img.size[0]),0) # Bottom split position

	print('>> Creating background...')
	bkg.paste(split('t'), box=tspos)
	bkg.paste(split('b'), box=bspos)

	if fopt.get() == 1 or fopt.get() == 3: # If radiobutton 2 or 4 are chosen
		bkg.paste(ndimg, box=(math.ceil((wid/2)-(img.size[0]/2)), 0)) # Paste edited image in the center of new image
	else:
		bkg.paste(origimg, box=(math.ceil((wid/2)-(img.size[0]/2)), 0)) # Paste original image in the center of new image
	

	## Borders

	# Add outer border
	if obvar.get() == 1:
		# bkg = ImageOps.expand(bkg,border=wid//100,fill='black')
		obdraw = ImageDraw.Draw(bkg)
		bordthick = 40 # Thickness of border
		obdraw.line((0, 0, bkg.size[0], 0), width=bordthick, fill='black') # Top line
		obdraw.line((0, bkg.size[1], bkg.size[0], bkg.size[1]), width=bordthick, fill='black') # Bottom line
		obdraw.line((0, 0, 0, bkg.size[1]), width=bordthick, fill='black') # Left line
		obdraw.line((bkg.size[0], 0, bkg.size[0], bkg.size[1]), width=bordthick, fill='black') # Right line
	elif obvar.get() == 0:
		pass

	# Seperation borders
	if sepbvar.get() == 1:
		print(sepbddvar.get())
		if sepbddvar.get() == 'Normal':
			rectbord = ImageDraw.Draw(bkg)
			blc = (bkg.size[0]/2) - (origimg.size[0]/2) # Border left coordinate
			brc = (bkg.size[0]/2) + (origimg.size[0]/2) # Border left coordinate
			rectbord.line((blc, 0, blc, img.size[1]), width=20, fill='black') # Paste rectangle on either edge of central image
			rectbord.line((brc, 0, brc, img.size[1]), width=20, fill='black')
	else:
		pass

	prevbkg = bkg.resize((800,450)) # Resizing preview image to fit on canvas
	previmg = ImageTk.PhotoImage(image=prevbkg) # Creating a PhotoImage of image object to load on canvas
	preview.create_image(0,0, image=previmg, anchor='nw') # Loading photoimage on canvas
	preview.image = previmg # https://web.archive.org/web/20201111190625id_/http://effbot.org/pyfaq/why-do-my-tkinter-images-not-appear.htm
	# preview.itemconfig(setprev)
	# tkinter.Tk()
	# master.mainloop()

	# ~ Resetting GUI ~
	startbutton.config(state='normal')
	previewbutton.config(state='normal')
	browsebutton.config(state='normal')


## Create Button function
def create():
	start()

	print('>> Exporting image...')

	dt = time.strftime('%Y-%m-%d_%H-%M-%S')
	path = f'./walls/{dt}.png'

	bkg.save(path)
	bkg.show()

	mvar = f'Done. File saved as {path}\n'
	print(f'>> {mvar}')
	messvar.set(mvar)



### GUI ###

### Subframes
leftsubframe = Frame(master, bg='#1d1c2c')
leftsubframe.grid(row=0, column=0)

rightsubframe = Frame(master, bg='#5a49a4', width=800, height=450)
rightsubframe.grid(row=0, column=1)
master.rowconfigure(0, pad=20)
master.columnconfigure(1, pad=20)

### Left subframe

## Text
infolab = Label(leftsubframe, width=58, justify='left', anchor='center', text="PortScape - A Tool to Turn Portrait Images into Landcape Wallpapers", bg='#1d1c2c', fg='#d7ceff')
leftsubframe.rowconfigure(0, pad=20)
infolab.grid(row=0)

## Address bar and browse button
addrframe = Frame(leftsubframe, width=448, bg='#1d1c2c')
addrframe.pack_propagate(0)
addrframe.grid(row=2, column=0)

addrvar = StringVar(addrframe)
avar = 'Please choose a file...'
addrvar.set(avar)

addrlab = Label(addrframe, textvariable=addrvar, anchor='w', width=40, bg='#1d1c2c', fg='#d7ceff')
addrlab.grid(row=0, column=0, sticky='we')

browsebutton = Button(addrframe, text='Browse', command=browse, width=9, bg='#1d1c2c', fg='#8d73ff', activebackground='#1d1c2c' , activeforeground='#8d73ff')
browsebutton.config(state='normal')
browsebutton.grid(row=0, column=1, pady=4)


## border, colour map, invert colours check buttons.
checkframe = Frame(leftsubframe, width=448, bg='#1d1c2c')
# checkframe.pack_propagate(0)
checkframe.grid(row=3, column=0)

def cmoption(): # When CM button is clicked
	if cmvar.get() == 1:
		cmb.config(state='normal')
		cmw.config(state='normal')
		invbutton.config(state='normal')
		cmbcolour.configure(background=cmbvar.get())
		cmwcolour.configure(background=cmwvar.get())
	else:
		cmb.config(state='disabled')
		cmw.config(state='disabled')
		invbutton.config(state='disabled')
		cmbcolour.configure(background='#1d1c2c')
		cmwcolour.configure(background='#1d1c2c')

cmvar = IntVar()
cmvar.set(0)
cmbutton = Checkbutton(checkframe, text='Colourise', variable=cmvar, command=cmoption, bg='#1d1c2c', fg='#8d73ff', activebackground='#1d1c2c' , activeforeground='#8d73ff')
cmbutton.grid(row=0, column=1)
cmbutton.config(state='normal')

# MPL Colour Map button
def ploption():
	if plbvar.get() == 1:
		pltdd.state(['!disabled','readonly']) # Sets dropdown to non edit mode
		pltdd.current(72) # Set dropdown default option
	else:
		pltdd.state(['disabled','readonly']) # Disable dropdown

plbvar = IntVar()
plbvar.set(0)

plbutton = Checkbutton(checkframe, text='Colour Map', variable=plbvar, command=ploption, bg='#1d1c2c', fg='#8d73ff', activebackground='#1d1c2c' , activeforeground='#8d73ff') # plot button

plbutton.grid(row=0, column=2)

# Invert colours button
icvar = IntVar()
icvar.set(0)

icbutton = Checkbutton(checkframe, text='Invert Colours', variable=icvar, bg='#1d1c2c', fg='#8d73ff', activebackground='#1d1c2c' , activeforeground='#8d73ff') # Invert white and black

icbutton.grid(row=0, column=3)


## Colouriser
cmframe = Frame(leftsubframe, width=448, bg='#1d1c2c')
cmframe.pack_propagate(0)
cmframe.grid(row=4, column=0)
leftsubframe.rowconfigure(4, pad=10)

# def clr(event):
#   event.widget.delete(0, 'end')
#   return None

def cmbset():
	col = colorchooser.askcolor() # Opens colour picker
	if col[1] != None:
		cmbvar.set(col[1]) # Sets var to hex value
		cmbcolour.configure(background=cmbvar.get())
	else:
		pass

def cmwset():
	col = colorchooser.askcolor()
	if col[1] != None:
		cmwvar.set(col[1])
		cmwcolour.configure(background=cmwvar.get())
	else:
		pass

cmblab = Label(cmframe, text='Blacks:', bg='#1d1c2c', fg='#d7ceff') # CM Black label

cmbvar = StringVar()
cmbvar.set('#000000')
cmb = Button(cmframe, text='Choose colour', command=cmbset, width=11, bg='#1d1c2c', fg='#8d73ff', activebackground='#1d1c2c' , activeforeground='#8d73ff')

cmbcolour = Button(cmframe, bg='#1d1c2c', width=2) # Button to display selected colour, couldnt be bothered to use tkinter canvas

cmwlab = Label(cmframe, text='Whites:', bg='#1d1c2c', fg='#d7ceff') # CM Black label

cmwvar = StringVar()
cmwvar.set('#FFFFFF')
cmw = Button(cmframe, text='Choose colour', command=cmwset, width=11, bg='#1d1c2c', fg='#8d73ff', activebackground='#1d1c2c' , activeforeground='#8d73ff')

cmwcolour = Button(cmframe, bg='#1d1c2c', width=2)

invvar = IntVar()
invvar.set(0)
invbutton = Checkbutton(cmframe, text='Invert Values', variable=invvar, bg='#1d1c2c', fg='#8d73ff', activebackground='#1d1c2c' , activeforeground='#8d73ff') # Invert white and black

cmb.config(state='disabled')
cmw.config(state='disabled')
invbutton.config(state='disabled')
cmbcolour.config(state='disabled')
cmwcolour.config(state='disabled')

cmblab.grid(row=0, column=0)
cmbcolour.grid(row=0, column=1)
cmb.grid(row=0, column=2)
cmwlab.grid(row=0, column=3)
cmwcolour.grid(row=0, column=4)
cmw.grid(row=0, column=5)
invbutton.grid(row=0, column=6)
# cmframe.columnconfigure(5, pad=20)


## Matplotlib Colour Map dropdown
pltframe = Frame(leftsubframe, width=600, bg='#5a49a4', padx=50, pady=5)
pltframe.pack_propagate(0)
pltframe.grid(row=5, column=0)

pltvar = StringVar() # matplotlib plot variable
plttext = Label(pltframe, text='Colour Map', bg='#5a49a4', fg='#d7ceff', activebackground='#5a49a4', activeforeground='#d7ceff', padx=20) # Dropdown label
plttext.grid(row=0, column=0)

pltddstyle = ttk.Style() # Style options for dropdown
pltddstyle.configure('TCombobox', background='#1d1c2c', foreground='#000')

pltdd = ttk.Combobox(pltframe, width=15, textvariable=pltvar, style='TCombobox')
pltdd['values'] = ('Accent','Accent_r','afmhot','afmhot_r','autumn','autumn_r','binary','binary_r','Blues','Blues_r','bone','bone_r','BrBG','BrBG_r','brg','brg_r','BuGn','BuGn_r','BuPu','BuPu_r','bwr','bwr_r','cividis','cividis_r','CMRmap','CMRmap_r','cool','coolwarm','coolwarm_r','cool_r','copper','copper_r','cubehelix','cubehelix_r','Dark2','Dark2_r','flag','flag_r','gist_earth','gist_earth_r','gist_gray','gist_gray_r','gist_heat','gist_heat_r','gist_ncar','gist_ncar_r','gist_rainbow','gist_rainbow_r','gist_stern','gist_stern_r','gist_yarg','gist_yarg_r','GnBu','GnBu_r','gnuplot','gnuplot2','gnuplot2_r','gnuplot_r','gray','gray_r','Greens','Greens_r','Greys','Greys_r','hot','hot_r','hsv','hsv_r','inferno','inferno_r','jet','jet_r','magma','magma_r','nipy_spectral','nipy_spectral_r','ocean','ocean_r','Oranges','Oranges_r','OrRd','OrRd_r','Paired','Paired_r','Pastel1','Pastel1_r','Pastel2','Pastel2_r','pink','pink_r','PiYG','PiYG_r','plasma','plasma_r','PRGn','PRGn_r','prism','prism_r','PuBu','PuBuGn','PuBuGn_r','PuBu_r','PuOr','PuOr_r','PuRd','PuRd_r','Purples','Purples_r','rainbow','rainbow_r','RdBu','RdBu_r','RdGy','RdGy_r','RdPu','RdPu_r','RdYlBu','RdYlBu_r','RdYlGn','RdYlGn_r','Reds','Reds_r','seismic','seismic_r','Set1','Set1_r','Set2','Set2_r','Set3','Set3_r','Spectral','Spectral_r','spring','spring_r','summer','summer_r','tab10','tab10_r','tab20','tab20b','tab20b_r','tab20c','tab20c_r','tab20_r','terrain','terrain_r','turbo','turbo_r','twilight','twilight_r','twilight_shifted','twilight_shifted_r','viridis','viridis_r','winter','winter_r','Wistia','Wistia_r','YlGn','YlGnBu','YlGnBu_r','YlGn_r','YlOrBr','YlOrBr_r','YlOrRd','YlOrRd_r')
pltdd.grid(row=0, column=1)
pltdd.state(['disabled','readonly']) # Sets dropdown on non edit mode

# Stops highlighting when clicked
def defocus(event):
	event.widget.master.focus_set()

pltdd.bind('<FocusIn>', defocus) 



## Filer options radio button
frframe = Frame(leftsubframe, width=448, bg='#d7ceff', padx=5)
frframe.pack_propagate(0)
frframe.grid(row=6, column=0, pady=5)

fo = ['None','Apply to Centre', 'Darken Sides', 'Both'] # Filter options
fopt = IntVar()
fopt.set(0)

for x in fo:
	n = fo.index(x)
	filterrad = Radiobutton(frframe, text=x, value=n, variable=fopt, bg='#d7ceff', fg='#5a49a4', activebackground='#d7ceff' , activeforeground='#5a49a4')
	filterrad.grid(row=4, column=n)



## Border options
bordframe = Frame(leftsubframe, width=448,height=20, bg='#3b2b7d', padx=5)
bordframe.grid(row=7, column=0)

# Outer border
obvar = IntVar()
obvar.set(0)
obbutton = Checkbutton(bordframe, text='Outer Border', variable=obvar, bg='#3b2b7d', fg='#d7ceff', activebackground='#3b2b7d' , activeforeground='#d7ceff')
obbutton.grid(row=0, column=0)

# Separation border

def sepboption():
	if sepbvar.get() == 1:
		sepbdd.state(['!disabled','readonly']) # Sets dropdown to non edit mode
		sepbdd.current(0) # Set dropdown default option
	else:
		sepbdd.state(['disabled','readonly']) # Disable dropdown

sepbvar = IntVar()
sepbvar.set(0)
sepbbutton = Checkbutton(bordframe, text='Seperation Border', variable=sepbvar, command=sepboption, bg='#3b2b7d', fg='#d7ceff', activebackground='#3b2b7d' , activeforeground='#d7ceff')
sepbbutton.grid(row=0, column=1)

sepbddstyle = ttk.Style() # Style options for dropdown
sepbddstyle.configure('TCombobox', background='#3b2b7d', foreground='#000')

sepbddvar = StringVar()
sepbdd = ttk.Combobox(bordframe, width=15, textvariable=sepbddvar, style='TCombobox')
sepbdd['values'] = ('Normal', 'Pixelated') # Different types of borders
sepbdd.grid(row=0, column=2)
sepbdd.state(['disabled','readonly']) # Sets dropdown on non edit mode

# Stops highlighting when clicked
def defocus(event):
	event.widget.master.focus_set()

sepbdd.bind('<FocusIn>', defocus) 



## Blur slider
blurframe = Frame(leftsubframe, bg='#d7ceff', padx=5, pady=5)
blurframe.grid(row=8, pady=5)

blurlabel = Label(blurframe, text='Blur Amount', bg='#d7ceff', fg='#5a49a4')
blurlabel.grid(row=0, column=0)

blurslider = Scale(blurframe, from_=0, to=100, orient=HORIZONTAL, length=350, bg='#8d73ff', fg='#1d1c2c')
blurslider.grid(row=1, column=0)



## Preview and Create
# Threading tutorial: https://www.youtube.com/watch?v=jnrCpA1xJPQ
pcframe = Frame(leftsubframe, bg='#1d1c2c', padx=10, pady=20) # Preview and Create button frame
pcframe.columnconfigure(0, pad=10)
pcframe.columnconfigure(1, pad=10)
pcframe.grid(row=9)

previewbutton = Button(pcframe, text='Preview', command=lambda:threading.Thread(target=start).start(), width=20, height=2, bg='#1d1c2c', fg='#8d73ff', activebackground='#1d1c2c' , activeforeground='#8d73ff')
# leftsubframe.rowconfigure(3, weight=1)
# pcframe.rowconfigure(0, pad=10)
previewbutton.grid(row=0, column=0)

previewbutton.config(state='disabled')

startbutton = Button(pcframe, text='Create!', command=lambda:threading.Thread(target=create).start(), width=20, height=2, bg='#1d1c2c', fg='#8d73ff', activebackground='#1d1c2c' , activeforeground='#8d73ff')
# pcframe.rowconfigure(3, weight=1)
# pcframe.rowconfigure(0, pad=10)
startbutton.grid(row=0, column=1)
startbutton.config(state='disabled')


## Messages
messvar = StringVar(leftsubframe)
mvar = ''
messvar.set(mvar)

messlabel = Label(leftsubframe, textvariable=messvar, anchor='center', width=58, height=2, bg='#1d1c2c', fg='#d7ceff')
messlabel.grid(row=10, column=0)



### Right Subframe

preview = Canvas(rightsubframe, width=800, height=450, bg='#5a49a4')
preview.grid(row=0, column=0)
# pimg = PhotoImage(file='pimg.jpeg')
# preview.create_image(0, 0, image=pimg)


master.mainloop()
