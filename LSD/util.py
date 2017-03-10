import sdl2
import sdl2.ext
from .env import SDL2Environment

def convert_opacity(value):
	""" Convert float values to opacity range between 0 and 255. """
	if type(value) == float and 0.0 <= value <= 1.0:
		# This is maybe a bit iffy, because it does not allow opacity values
		# in the 0 to 255 range between 0 and 1 (it maybe undesiredly converts
		# it to value*255).
		# TODO: Think about a solution for this
		return int(value*255)
	elif type(value) in [int, float]:
		if 0 <= value <= 255:
			return int(value)
		else:
			raise ValueError("Invalid opacity value")
	else:
		raise TypeError("Incorrect type or value passed for opacity.")

def determine_optimal_colorkey(drawing_color, dev_offset=5):
	""" Determines the optimal color to use for the transparent color key.
	
	It bases the decision on the supplied foreground and background color. The used
	algorithm is very simple and may be up for improvement. The function simply
	checks if the foreground color is not identical to the Framebuffer's
	background color (which me be the case if one wants to draw Kanizsa figures)
	If it is not, it uses the FrameBuffers background color as the transparent
	color key. If the colors are identical, it slightly manipulates the background
	color to a different value (offsetting the color by `dev_offset`)

	Parameters
	----------
	drawing_color: sdl2.ext.Color
		The foreground color in which the shape will be drawn
	dev_offset: int, optional
		The value with which to vary the background color if it is identical
		to the foreground color. The resulting color will be

		    background_color +/- dev_offset

		where dev_offset will be substracted if background_color is white and
		otherwise it will be added.

	Returns
	-------
	sdl2.ext.Color: the optimal colorkey value
	"""

	if not 1 <= dev_offset <= 25:
		raise ValueError("dev_offset should be a value between 1 and 25")

	# Create offset_color
	offset_color = sdl2.ext.Color(dev_offset, dev_offset, dev_offset, 0)
	# Create white_color
	white = sdl2.ext.Color(255,255,255,255)

	color_key = drawing_color + offset_color
	if color_key != white:
		return color_key
	else:
		return drawing_color - offset_color

def check_sdl2env(sdl2env):
	if type(sdl2env) != SDL2Environment:
		raise TypeError("Required sdl2env parameter is not a SDL2Environment object")
	else:
		return sdl2env

def check_int_value(value, min_value=None, varname="variable"):
	# Check if value is an int or float
	if type(value) not in [int, float]:
		raise TypeError("{} needs to be int or float".format(varname))
	if min_value and value < min_value:
		raise ValueError("{} cannot be smaller than {}".format(varname, min_value))
	return int(value)

def get_sdl_flip_value(flip):
	if flip is None:
		return sdl2.SDL_FLIP_NONE
	elif flip == "hor":
		return sdl2.SDL_FLIP_HORIZONTAL
	elif flip == "ver":
		return sdl2.SDL_FLIP_VERTICAL
	else:
		raise ValueError("Unrecognized value for flip")	

		
