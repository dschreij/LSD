# -*- coding: utf-8 -*-
"""
Created on Sun May  3 13:15:46 2015

@author: daniel
"""
# Python 3 compatibility
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

# SDL2 libraries
import sdl2.ext
from .screen import FrameBuffer
from .env import SDL2Environment
import os
import sys

from functools import wraps

__version__ = '1.0'
__author__ = 'Daniel Schreij'

# The variable to hold the sdl2environment object
current_sdl2_environment = None

def create_window(resolution, title="SDL2 Display Window", fullscreen=False):
	global current_sdl2_environment
	if type(resolution) != tuple and len(resolution) != 2:
		raise TypeError("Please make sure the resolution variable is a tuple with (width,height)")
	(width, height) = resolution
	
	try:
		sdl2.ext.init()
	except sdl2.ext.SDLError:
		# On windows, there is the strange error that sdl looks for "directx" as videodriver
		# although this is often internally specified as "windows". If this occurs, give sdl2 a 
		# nudge in the right direction by picking the first detected available video driver.
		if os.name == "nt":
			sys.stdout.write("Invalid video driver specified. Trying '{0}'..."
				"".format(sdl2.video.SDL_GetVideoDriver(0)))
			os.environ["SDL_VIDEODRIVER"] = sdl2.video.SDL_GetVideoDriver(0)
			sdl2.ext.init()
			print("Success!")

	windowflags = 0
	if fullscreen:
		windowflags = windowflags|sdl2.SDL_WINDOW_FULLSCREEN

		dispinfo = sdl2.SDL_DisplayMode()
		if sdl2.SDL_GetCurrentDisplayMode(0, dispinfo) != 0:
			raise Exception("Could not get display resolution: {}"
				"".format(sdl2.SDL_GetError()))
		window_size = dispinfo.w, dispinfo.h
	else:
		window_size = resolution

	window = sdl2.ext.Window(title, size=window_size, flags=windowflags)
	window.show()

	# Create a render system that renders to the window surface
	rendererflags = sdl2.SDL_RENDERER_ACCELERATED | \
		sdl2.SDL_RENDERER_PRESENTVSYNC | sdl2.SDL_RENDERER_TARGETTEXTURE
	renderer = sdl2.ext.Renderer(window, flags=rendererflags)
	renderer.clear(0)
	renderer.present()
	# Create sprite factory to create textures with later
	texture_factory = sdl2.ext.SpriteFactory(renderer=renderer)
	# Create sprite factory to create surfaces with later
	surface_factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)

	# Create an environment object that contains all necessary objects, functions
	# and other information to work with the window interface.
	sdl2env = SDL2Environment(window, resolution, renderer, texture_factory, 
		surface_factory, __version__)
	current_sdl2_environment= sdl2env
	window.refresh()
	return sdl2env

def destroy_window(sdl2env=None):
	global current_sdl2_environment
	current_sdl2_environment = None
	del(current_sdl2_environment)
	sdl2.ext.quit()

# Decorator
def inject_sdl_environment(func):
	@wraps(func)
	def wrapped(*args, **kwargs):
		global current_sdl2_environment
		if "sdl2env" not in kwargs:
			kwargs['sdl2env'] = current_sdl2_environment
		return func(*args, **kwargs)
	return wrapped

@inject_sdl_environment
def create_framebuffer(*args, **kwargs):
	sdl2env = kwargs.get('sdl2env', None)
	if type(sdl2env) == SDL2Environment:
		if len(args):
			return FrameBuffer(*args, **kwargs)
		else:
			return FrameBuffer(**kwargs)
	else:
		raise EnvironmentError("SDL2 is not initialized yet! Create a window first")




