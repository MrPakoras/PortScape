version = 'v6.2' # Editing centre image seperately to side images


import os, time, re, mimetypes, math, threading, tkinter, functools
from tkinter import *
from tkinter import filedialog, colorchooser, ttk
import PIL
from PIL import Image as i
from PIL import ImageFilter, ImageOps, ImageDraw, ImageTk, ImageEnhance
import matplotlib
from matplotlib import pyplot as plt
import numpy as np

print('>> Running...')

master = Tk()
#master.iconbitmap('tbcarrowicon.ico')
master.title(f'PortScape {version} GUI')
master.geometry('1280x475')
# master.resizable(False, False)
master.configure(background='#1d1c2c')
master.columnconfigure(0, weight=2)
icon = PhotoImage(file='./extras/favicon.png')
master.iconphoto(False, icon)
#bkg = PhotoImage(file='bkg.png')
#setb = Label(master, image=bkg)
#setb.place(x=0, y=0, relwidth=1, relheight=1)

## Browse for file function
filename = '/'
def browse():
	global filename
	filename = filedialog.askopenfilename(initialdir = filename, title = "Select a File")

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
	global img
	startbutton.config(state='disabled')
	previewbutton.config(state='disabled')
	browsebutton.config(state='disabled')
	mvar = 'Creating wallpaper. Please wait...'
	messvar.set(mvar)

	### CODE ###
	print('>> Opening image...')
	try:
		img = i.open(filename)
	except PIL.UnidentifiedImageError:
		mvar = 'Error. Cannot identify image file. Please choose another image.'
		messvar.set(mvar)
		browse()

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

	if cmswvar.get() == 0:
		cmcentreopt = pltvar.get()
		cmsidesopt = pltvar2.get()
	if cmswvar.get() == 1: # If switched
		cmcentreopt = pltvar2.get()
		cmsidesopt = pltvar.get()

	if cmcentreopt == 'None':
		pass
	else:
		cmcommand(cmcentreopt)
		centreimg = cmimg # colour mapped centre image to be pasted on top later

	if cmsidesopt == 'None':
		pass
	else:
		cmcommand(cmsidesopt) # Colour map sides
		img = cmimg


	## Invert colours
	if icvar.get() == 1: 
		print('>> Inverting image...')
		img = img.convert('RGB')
		# print(img.mode)
		img = ImageOps.invert(img)


	## Blur Options
	blurval = int(blurslider.get()) # Slider value

	
	if bluropt.get() == 0: # Gaussian blur
		if blurval == 0: # Filter options
			pass
		else:
			print('>> Applying Gaussian Blur...')
			# blur = hei/()*8
			img = img.filter(ImageFilter.GaussianBlur(radius=(blurval*0.1))) # Gaussian blur

	if bluropt.get() == 1: # Pixellate
		# pixw = (2*img.size[0]//(blurval+1))//(2**((img.size[0]//1000)-1))
		# pixh = (2*img.size[1]//(blurval+1))//(2**((img.size[1]//1000)-1))

		pixw = 2*img.size[0]//(blurval+1)
		pixh = 2*img.size[1]//(blurval+1)

		imgpix = img.resize((pixw, pixh), resample=i.BILINEAR)
		img = imgpix.resize(img.size, i.NEAREST)

	if bluropt.get() == 2: # Darken
		# https://stackoverflow.com/questions/43618910/pil-drawing-a-semi-transparent-square-overlay-on-image
		# img = i.eval(img, lambda x: x*((blurval/50)+0))

		# https://pythonexamples.org/python-pillow-adjust-image-brightness/
		enhancer = ImageEnhance.Brightness(img)
		img = enhancer.enhance(blurval/50)


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

	if cmcentreopt == 'None': # If centre colour map == 'None'
		bkg.paste(origimg, box=(math.ceil((wid/2)-(img.size[0]/2)), 0)) # Paste original image in the center of new image
	else:
		bkg.paste(centreimg, box=(math.ceil((wid/2)-(img.size[0]/2)), 0)) # Paste edited image in the center of new image
	

	## Borders

	# Add outer border
	# bordlayer = i.new('RGBA', (bkg.size[0], bkg.size[1]), (255,255,255,255)) # New layer for border to be added to which can then be edited and pasted on bkg

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
		if sepbddvar.get() == 'Normal':
			rectbord = ImageDraw.Draw(bkg)
			blc = (bkg.size[0]/2) - (origimg.size[0]/2) # Border left coordinate
			brc = (bkg.size[0]/2) + (origimg.size[0]/2) # Border left coordinate
			rectbord.line((blc, 0, blc, img.size[1]), width=20, fill='black') # Paste rectangle on either edge of central image
			rectbord.line((brc, 0, brc, img.size[1]), width=20, fill='black')
	else:
		pass

	# bkg.paste(bordlayer, (0, 0))
	# bordlayer.save('./bord.png')


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

	mvar = 'Done.'
	messvar.set(mvar)


## Create Button function
def create():
	start()

	print('>> Exporting image...')

	dt = time.strftime('%Y-%m-%d_%H-%M-%S')
	path = f'./walls/{dt}.png'

	bkg.save(path)
	# bkg.show()

	mvar = f'Done. File saved as {path}\n'
	print(f'>> {mvar}')
	messvar.set(mvar)

def cmcommand(option):
	global img, cmimg
	print(f'>> Applying {option} colour map...')
	pltcm = matplotlib.cm.get_cmap(option) # color map
	cmimg = img.convert('L')
	cmimg = np.array(cmimg)
	cmimg = pltcm(cmimg)
	cmimg = np.uint8(cmimg*255)
	cmimg = i.fromarray(cmimg)
	return cmimg

def blurcommand(n): # Command to set the scale values
	global bsstart, bsend, bluropt
	bsstart, bsend = IntVar(blurframe), IntVar(blurframe)

	if bluropt.get() == 2:
		bssvar, bsevar = '-100', '100'
		bsstart.set(bssvar)
		bsend.set(bsevar)

	else:
		bssvar, bsevar = '0', '100'
		bsstart.set(bssvar)
		bsend.set(bsevar)

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


## colourise, colour map, invert colours check buttons.
checkframe = Frame(leftsubframe, width=448, bg='#1d1c2c')
# checkframe.pack_propagate(0)
checkframe.grid(row=3, column=0)

def cmoption(): # When CM button is clicked
	if cmvar.get() == 1:
		cmb.config(state='normal')
		cmw.config(state='normal')		
		cmbcolour.configure(background=cmbvar.get())
		cmwcolour.configure(background=cmwvar.get())
		invbutton.config(state='normal') # Invert values button

	if cmvar.get() == 1:# or plbvar.get() == 1:
		atcb.config(state='normal') # Apply to Centre button
		bothb.config(state='normal') # Both button

	else:
		cmb.config(state='disabled')
		cmw.config(state='disabled')		
		cmbcolour.configure(background='#1d1c2c')
		cmwcolour.configure(background='#1d1c2c')
		invbutton.config(state='disabled')

		atcb.config(state='disabled')
		bothb.config(state='disabled')


cmvar = IntVar()
cmvar.set(0)
cmbutton = Checkbutton(checkframe, text='Colourise', variable=cmvar, command=cmoption, bg='#1d1c2c', fg='#8d73ff', activebackground='#1d1c2c' , activeforeground='#8d73ff')
cmbutton.grid(row=0, column=1)
cmbutton.config(state='normal')


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
#here
# cmblab = Label(cmframe, text='Blacks:', bg='#1d1c2c', fg='#d7ceff') # CM Black label

# cmbvar = StringVar()
# cmbvar.set('#000000')
# cmb = Button(cmframe, text='Choose colour', command=cmbset, width=11, bg='#1d1c2c', fg='#8d73ff', activebackground='#1d1c2c' , activeforeground='#8d73ff')

# cmbcolour = Button(cmframe, bg='#1d1c2c', width=2) # Button to display selected colour, couldnt be bothered to use tkinter canvas

# cmwlab = Label(cmframe, text='Whites:', bg='#1d1c2c', fg='#d7ceff') # CM White label

# cmwvar = StringVar()
# cmwvar.set('#FFFFFF')
# cmw = Button(cmframe, text='Choose colour', command=cmwset, width=11, bg='#1d1c2c', fg='#8d73ff', activebackground='#1d1c2c' , activeforeground='#8d73ff')

# cmwcolour = Button(cmframe, bg='#1d1c2c', width=2)

# invvar = IntVar()
# invvar.set(0)
# invbutton = Checkbutton(cmframe, text='Invert Values', variable=invvar, bg='#1d1c2c', fg='#8d73ff', activebackground='#1d1c2c' , activeforeground='#8d73ff') # Invert white and black

# cmb.config(state='disabled')
# cmw.config(state='disabled')
# invbutton.config(state='disabled')
# cmbcolour.config(state='disabled')
# cmwcolour.config(state='disabled')

# cmblab.grid(row=0, column=0)
# cmbcolour.grid(row=0, column=1)
# cmb.grid(row=0, column=2)
# cmwlab.grid(row=0, column=3)
# cmwcolour.grid(row=0, column=4)
# cmw.grid(row=0, column=5)
# invbutton.grid(row=0, column=6)
# cmframe.columnconfigure(5, pad=20)
#to here

colguiopts = ['Blacks:','Whites:','Mids:'] # Options for colourise function
colvals = ['#000000','#FFFFFF',None] # Colourise values
colshowlist = [] # List of colshow widgets
coln = len(colguiopts)-1

def colset(n): # argument from colour chooser button
	print(colshow.grid_info())
	col = colorchooser.askcolor() # Opens colour picker
	if col[1] != None:
		colvals[n] = col[1] # Sets colval array to hex value
		colshowlist[n].configure(background=colvals[n])
	else:
		pass

def colourisegui(n,name):
	global coln
	colvar = StringVar() # Colourise variable
	collab = Label(cmframe, text=name, bg='#1d1c2c', fg='#d7ceff')
	global colshow
	colshow = Button(cmframe, bg='#1d1c2c', width=2) # Shows what colour is chosen
	colshowlist.append(colshow) # Adds colshow widget to list to be configured individually later
	colchoose = Button(cmframe, text='Choose colour', command=functools.partial(colset, n), width=11, bg='#1d1c2c', fg='#8d73ff', activebackground='#1d1c2c' , activeforeground='#8d73ff') # Choose colour button
	# https://stackoverflow.com/questions/32037769/how-do-i-link-python-tkinter-widgets-created-in-a-for-loop

	collab.grid(row=0, column=3*n)
	colshow.grid(row=0, column=3*n+1)
	colshow.config(state='disabled')
	colchoose.grid(row=0, column=3*n+2)

	
	coln -= 1

[colourisegui(coln,colguiopts[coln]) for loop in range(coln+1)]
colshowlist.reverse() # Reverses colshowlist since widgets were added in reverse order




## Matplotlib Colour Map dropdown
pltframe = Frame(leftsubframe, width=600, bg='#5a49a4', padx=5, pady=5)
pltframe.pack_propagate(0)
pltframe.grid(row=5, column=0)

pltddstyle = ttk.Style() # Style options for dropdown
pltddstyle.configure('TCombobox', background='#1d1c2c', foreground='#000')

pltddvals = ('None','Accent','Accent_r','afmhot','afmhot_r','autumn','autumn_r','binary','binary_r','Blues','Blues_r','bone','bone_r','BrBG','BrBG_r','brg','brg_r','BuGn','BuGn_r','BuPu','BuPu_r','bwr','bwr_r','cividis','cividis_r','CMRmap','CMRmap_r','cool','coolwarm','coolwarm_r','cool_r','copper','copper_r','cubehelix','cubehelix_r','Dark2','Dark2_r','flag','flag_r','gist_earth','gist_earth_r','gist_gray','gist_gray_r','gist_heat','gist_heat_r','gist_ncar','gist_ncar_r','gist_rainbow','gist_rainbow_r','gist_stern','gist_stern_r','gist_yarg','gist_yarg_r','GnBu','GnBu_r','gnuplot','gnuplot2','gnuplot2_r','gnuplot_r','gray','gray_r','Greens','Greens_r','Greys','Greys_r','hot','hot_r','hsv','hsv_r','inferno','inferno_r','jet','jet_r','magma','magma_r','nipy_spectral','nipy_spectral_r','ocean','ocean_r','Oranges','Oranges_r','OrRd','OrRd_r','Paired','Paired_r','Pastel1','Pastel1_r','Pastel2','Pastel2_r','pink','pink_r','PiYG','PiYG_r','plasma','plasma_r','PRGn','PRGn_r','prism','prism_r','PuBu','PuBuGn','PuBuGn_r','PuBu_r','PuOr','PuOr_r','PuRd','PuRd_r','Purples','Purples_r','rainbow','rainbow_r','RdBu','RdBu_r','RdGy','RdGy_r','RdPu','RdPu_r','RdYlBu','RdYlBu_r','RdYlGn','RdYlGn_r','Reds','Reds_r','seismic','seismic_r','Set1','Set1_r','Set2','Set2_r','Set3','Set3_r','Spectral','Spectral_r','spring','spring_r','summer','summer_r','tab10','tab10_r','tab20','tab20b','tab20b_r','tab20c','tab20c_r','tab20_r','terrain','terrain_r','turbo','turbo_r','twilight','twilight_r','twilight_shifted','twilight_shifted_r','viridis','viridis_r','winter','winter_r','Wistia','Wistia_r','YlGn','YlGnBu','YlGnBu_r','YlGn_r','YlOrBr','YlOrBr_r','YlOrRd','YlOrRd_r')


# Centre Options
pltvar = StringVar() # matplotlib plot variable
plttext = Label(pltframe, text='Centre', bg='#5a49a4', fg='#d7ceff', activebackground='#5a49a4', activeforeground='#d7ceff') # Dropdown label
plttext.grid(row=0, column=0)

pltdd = ttk.Combobox(pltframe, width=15, textvariable=pltvar, style='TCombobox')
pltdd['values'] = pltddvals
pltdd.grid(row=0, column=1)
pltdd.state(['!disabled','readonly']) # Sets dropdown on non edit mode
pltdd.current(0) # Set dropdown default option

# Side Options
pltvar2 = StringVar() # matplotlib plot variable
plttext2 = Label(pltframe, text='Sides', bg='#5a49a4', fg='#d7ceff', activebackground='#5a49a4', activeforeground='#d7ceff') # Dropdown label
plttext2.grid(row=0, column=2)

pltdd2 = ttk.Combobox(pltframe, width=15, textvariable=pltvar2, style='TCombobox')
pltdd2['values'] = pltddvals
pltdd2.grid(row=0, column=3)
pltdd2.state(['!disabled','readonly']) # Sets dropdown on non edit mode
pltdd2.current(0) # Set dropdown default option


# Stops highlighting when clicked
def defocus(event):
	event.widget.master.focus_set()

pltdd.bind('<FocusIn>', defocus)
pltdd2.bind('<FocusIn>', defocus)

# Switch options button
cmswvar = IntVar()
cmswvar.set(0)
cmswbutton = Checkbutton(pltframe, text='Switch', variable=cmswvar, bg='#5a49a4', fg='#1d1c2c', activebackground='#5a49a4' , activeforeground='#1d1c2c')
cmswbutton.grid(row=0, column=4)



## Filer options radio button
frframe = Frame(leftsubframe, width=448, bg='#d7ceff', padx=5)
frframe.pack_propagate(0)
frframe.grid(row=6, column=0, pady=5)

fopt = IntVar()
fopt.set(0)

def radiob(t, n):
	r = Radiobutton(frframe, text=t, value=n, variable=fopt, bg='#d7ceff', fg='#5a49a4', activebackground='#d7ceff' , activeforeground='#5a49a4')
	r.grid(row=0, column=n)

	return r

noneb = radiob('None', 0) # None button
atcb = radiob('Apply to Centre', 1) # Apply to centre button
dsb = radiob('Darken Sides', 2) # Darken Sides button
bothb = radiob('Both', 3) # Both button

atcb.config(state='disabled')
bothb.config(state='disabled')


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

brbframe = Frame(blurframe, bg='#d7ceff', padx=5, pady=5) # Blur radio button frame
brbframe.grid(row=0)

bluropt = IntVar()
bluropt.set(0)

gbrb = Radiobutton(brbframe, text='Gaussian Blur', value=0, variable=bluropt, command=blurcommand(0), bg='#d7ceff', fg='#5a49a4', activebackground='#d7ceff' , activeforeground='#5a49a4') # Gaussian blur radio button
gbrb.grid(row=0, column=0)

pixrb = Radiobutton(brbframe, text='Pixellate', value=1, variable=bluropt, command=blurcommand(1), bg='#d7ceff', fg='#5a49a4', activebackground='#d7ceff' , activeforeground='#5a49a4') # Pixellate radio button
pixrb.grid(row=0, column=1)

darkrb = Radiobutton(brbframe, text='Darken', value=2, variable=bluropt, command=blurcommand(2), bg='#d7ceff', fg='#5a49a4', activebackground='#d7ceff' , activeforeground='#5a49a4') # Darken radio button
darkrb.grid(row=0, column=2)

# blurlabel = Label(blurframe, text='Blur Amount', bg='#d7ceff', fg='#5a49a4')
# blurlabel.grid(row=0, column=0)
global bsstart, bsend
# blurslider = Scale(blurframe, from_=bsstart.get(), to=bsend.get(), orient=HORIZONTAL, length=350, bg='#8d73ff', fg='#1d1c2c')
blurslider = ttk.Scale(blurframe, from_=bsstart.get(), to=bsend.get(), orient=HORIZONTAL, length=350)
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
pswidth = master.winfo_width()//1.6 # Preview section width
psheight = 9*pswidth//16

print(pswidth)

preview = Canvas(rightsubframe, width=pswidth, height=psheight, bg='#5a49a4')
preview.grid(row=0, column=0)
pimg = ImageTk.PhotoImage(file='./extras/pimg.png')
preview.create_image(0, 0, image=pimg, anchor='nw')


master.mainloop()