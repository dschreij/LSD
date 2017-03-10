
from functools import wraps

def inject_sdl(func):
	@wraps(func)
	def wrapper(*args, **kwargs):
		print("In inject_sdl")
		print(args)
		print(kwargs)
		if "sdl2env" not in kwargs:
			kwargs['sdl2env'] = "Environment present"
		return func(*args, **kwargs)
	return wrapper


def texture(func):
	@wraps(func)
	@inject_sdl
	def wrapper(*args, **kwargs):
		print("In texture")
		print(args)
		print(kwargs)
		return func(*args, **kwargs)
	return wrapper

@texture
def draw_circle(x, y, r, **kwargs):
	""" Docstring of circle """
	print(kwargs)
	print("Drawing circle at {}, {} with radius {}".format(x, y, r))

draw_circle(10,10,5)
print(draw_circle.__doc__)

