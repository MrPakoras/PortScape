# PortScape
Turn portrait images into landscape wallpapers
> Before using the program, run installlibs.bat to install required modules

* Open PortScape
* Select a file
* Choose whether you want to colourise the background or not. If so:
	* Click _**Choose colour**_ and pick a colour value for the blacks
	* Click _**Choose colour**_ and pick a colour value for the whites
	* Select _Invert Values_ if you want to swap the blacks and whites
	
	> Colourise function converts image to greyscale and replaces black and white pixels with these colours
* Choose whether you cant to colour map the background or not. Choose a map that youd like using the dropdown menu.
	> Colour Map function uses matplotlib to map colours onto the image
* Choose whether you want to apply edits to the central image too or not
* Choose whether you want to darken the sides or not
* Choose whether you want a border on your image or not:
	* **Outer Border** - Adds a border around the outside of the image
	* **Separation Border** - Adds black lines to the sides of the central image to separate it from the background
* Choose blur options and then use the slider to select the amount:
	* **Gaussian Blur** - Applies a normal blur to the background of the image
	* **Pixellate** - Pixellate the background

* Click _**Preview**_ to see what your edits look like before finalising the image
* Click _**Create!**_ to save image :)
