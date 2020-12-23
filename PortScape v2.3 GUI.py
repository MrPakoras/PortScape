# v2.3 - Added invert colours option

import os, time, re, mimetypes, math, threading
from tkinter import *
from tkinter import filedialog, colorchooser
from PIL import Image as i
from PIL import ImageFilter, ImageOps, ImageDraw

print('>> Running...')

master = Tk()
#master.iconbitmap('tbcarrowicon.ico')
master.title('PortScape v12.2 GUI')
master.geometry('448x252')
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

		else:
			startbutton.config(state='disabled')
			mvar = 'Error. Please choose an image file.'
			messvar.set(mvar)

## Start program button
def start():
	startbutton.config(state='disabled')
	browsebutton.config(state='disabled')
	mvar = 'Creating wallpaper. Please wait...'
	messvar.set(mvar)

	### CODE ###
	print('>> Opening image...')
	img = i.open(filename)
	wid, hei = math.ceil(img.size[1]*(16/9)), img.size[1] # Working out 16:9 width for original height

	# print(f'>> Orig size:   {img.size}')
	# print(f'>> New size:   {wid, hei}')

	mode = 'RGBA'
	bkg = i.new(mode, (wid, hei)) # Background

	def split(pos): # Splits image in 2 and puts top half on the left and bottom on the right
		imgcent = math.ceil(hei/2) # Image center
		blur = hei/200
		global fopt

		if pos == 't':
			print('>> Creating left background...')
			s = img.crop(box=(0,0,img.size[0],imgcent)) # Cropping image - 4 tuple: left,top,right,bottom
		elif pos == 'b':
			print('>> Creating right background...')
			s = img.crop(box=(0,imgcent,img.size[0],img.size[1]))	

		sr = s.resize(tuple(z*2 for z in s.size)) # Scaling up by 2 because img was split in two

		if cmvar.get() == 1: # Colour map
			if invvar.get() == 1:
				cmblack = cmwvar.get()
				cmwhite = cmbvar.get()
			else:
				cmblack = cmbvar.get()
				cmwhite = cmwvar.get()
			sr = sr.convert('L') # Convert to greyscale
			sr = ImageOps.colorize(sr, black=cmblack, white=cmwhite) # colour map

		if icvar.get() == 1: # Invert colours
			sr = ImageOps.invert(sr)

		if fopt.get() == 0: # Filter options
			pass
		else:
			if fopt.get() != 2: # If radio button 3 not chosen
				sr = sr.filter(ImageFilter.GaussianBlur(radius=blur)) # Gaussian blur
			
			if fopt.get() != 1: # If radio button 2 not chosen
				# https://stackoverflow.com/questions/43618910/pil-drawing-a-semi-transparent-square-overlay-on-image
				sr = i.eval(sr, lambda x: x/2)

		return sr

	## Working out where top and bottom splits are to be pasted
	print('>> Calculating dimensions...')
	sw = math.ceil((wid-img.size[0])/2) # split width

	tspos = (math.ceil((sw/2)-img.size[0]),0) # Top split position
	bspos = (math.ceil((wid-sw/2) - img.size[0]),0) # Bottom split position

	print('>> Creating background...')
	bkg.paste(split('t'), box=tspos)
	bkg.paste(split('b'), box=bspos)

	bkg.paste(img, box=(math.ceil((wid/2)-(img.size[0]/2)), 0)) # Paste original image in the center of new image
	
	# Add border
	if bordvar.get() == 1:
		bkg = ImageOps.expand(bkg,border=wid//100,fill='black')
	elif bordvar.get() == 0:
		pass

	print('>> Exporting image...')
	dt = time.strftime('%d-%m-%y_%H-%M-%S')
	path = f'./walls/wallpaper-{dt}.png'
	bkg.save(path)
	bkg.show()

	# ~ Resetting GUI ~
	startbutton.config(state='normal')
	browsebutton.config(state='normal')
	bordbutton.config(state='normal')

	mvar = f'Done. File saved as ./walls/wallpaper-{dt}.png'
	print(f'>> {mvar}')
	messvar.set(mvar)




### GUI ###


## Text
infolab = Label(master, width=58, justify='left', anchor='center', text="Please select a file and click the 'Create!' button", bg='#1d1c2c', fg='#d7ceff')
master.rowconfigure(0, pad=20)
infolab.grid(row=0)

## Address bar and browse button
addrframe = Frame(master, width=448, bg='#1d1c2c')
addrframe.pack_propagate(0)
addrframe.grid(row=2, column=0)

addrvar = StringVar(addrframe)
avar = 'Please choose a file'
addrvar.set(avar)

addrlab = Label(addrframe, textvariable=addrvar, anchor='w', width=40, bg='#1d1c2c', fg='#d7ceff')
addrlab.grid(row=0, column=0, sticky='we')

browsebutton = Button(addrframe, text='Browse', command=browse, width=9, bg='#1d1c2c', fg='#8d73ff', activebackground='#1d1c2c' , activeforeground='#8d73ff')
browsebutton.config(state='normal')
browsebutton.grid(row=0, column=1, pady=4)



## border, colour map, invert colours check buttons.
checkframe = Frame(master, width=448, bg='#1d1c2c')
checkframe.pack_propagate(0)
checkframe.grid(row=3, column=0)

bordvar = IntVar()
bordvar.set(0)
bordbutton = Checkbutton(checkframe, text='Add border', variable=bordvar, bg='#1d1c2c', fg='#8d73ff', activebackground='#1d1c2c' , activeforeground='#8d73ff')
bordbutton.grid(row=0, column=0)

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
cmbutton = Checkbutton(checkframe, text='Colour Map', variable=cmvar, command=cmoption, bg='#1d1c2c', fg='#8d73ff', activebackground='#1d1c2c' , activeforeground='#8d73ff')
cmbutton.grid(row=0, column=1)
cmbutton.config(state='normal')

## Invert colours
icvar = IntVar()
icvar.set(0)

icbutton = Checkbutton(checkframe, text='Invert Colours', variable=icvar, bg='#1d1c2c', fg='#8d73ff', activebackground='#1d1c2c' , activeforeground='#8d73ff') # Invert white and black

icbutton.grid(row=0, column=2)


## Colour Map
cmframe = Frame(master, width=448, bg='#1d1c2c')
cmframe.pack_propagate(0)
cmframe.grid(row=4, column=0)
master.rowconfigure(4, pad=10)

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



## Filer options radio button
frframe = Frame(master, width=448, bg='#d7ceff')
frframe.pack_propagate(0)
frframe.grid(row=5, column=0)

fo = ['None','Gaussian Blur', 'Darken', 'Blur & Darken'] # Filter options
fopt = IntVar()
fopt.set(0)

for x in fo:
	n = fo.index(x)
	filterrad = Radiobutton(frframe, text=x, value=n, variable=fopt, bg='#d7ceff', fg='#5a49a4', activebackground='#d7ceff' , activeforeground='#5a49a4')
	filterrad.grid(row=4, column=n)



## Create
# Threading tutorial: https://www.youtube.com/watch?v=jnrCpA1xJPQ
startbutton = Button(master, text='Create!', command=lambda:threading.Thread(target=start).start(), width=20, height=2, bg='#1d1c2c', fg='#8d73ff', activebackground='#1d1c2c' , activeforeground='#8d73ff')
# master.rowconfigure(3, weight=1)
master.rowconfigure(6, pad=10)
startbutton.grid(row=6, column=0)
startbutton.config(state='disabled')



## Messages
messvar = StringVar(master)
mvar = ''
messvar.set(mvar)

messlabel = Label(master, textvariable=messvar, anchor='center', width=58, bg='#1d1c2c', fg='#d7ceff')
messlabel.grid(row=7, column=0)


master.mainloop()
