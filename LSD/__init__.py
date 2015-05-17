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
import LSD.drawing

__version__ = '1.0'
__author__ = 'Daniel Schreij'

class SDL2Environment(object):

	def __init__(self, window, resolution, renderer, texture_factory, surface_factory):
		self.window = window
		self.resolution = resolution
		self.renderer = renderer
		self.texture_factory = texture_factory
		self.surface_factory = surface_factory
		self.active_framebuffers = []

		# Get the rest of the info by quering SDL2 itself
		# Only for screen 1 for now
		self.pysdl2_version = sdl2.__version__
		self.sdl2_version = "{}.{}.{}".format(sdl2.version.SDL_MAJOR_VERSION, sdl2.version.SDL_MINOR_VERSION, sdl2.version.SDL_PATCHLEVEL)

		self.cpu_count = sdl2.SDL_GetCPUCount()
		self.display_count = sdl2.SDL_GetNumVideoDisplays()

		self.displays = []
		for dispnum in range(self.display_count):
			dispinfo = sdl2.SDL_DisplayMode()
			res = sdl2.SDL_GetCurrentDisplayMode(dispnum, dispinfo)
			if res == 0:
				self.displays.append(dispinfo)
				
		self.display_drivers = [sdl2.video.SDL_GetVideoDriver(i) for i in range(sdl2.video.SDL_GetNumVideoDrivers())]
		self.display_driver = sdl2.SDL_GetCurrentVideoDriver()

	def __str__(self):
		infostring = """
SDL2 environment information

General:
	LSD version {}
	PySDL2 version: {}
	SDL2 version: {}
	CPU count: {}

Displays:
	Available display drivers: {}
	Currrent display driver: {}
	Number of displays detected: {}
		""".format(
			__version__,
			self.pysdl2_version,
			self.sdl2_version,
			self.cpu_count,
			self.display_drivers,
			self.display_driver,
			self.display_count
		)

		for dispnum, display in enumerate(self.displays):
			infostring += """
	Display {}:
		Resolution: ({},{})
		Refresh rate: {} fps
			""".format(dispnum, display.w, display.h, display.refresh_rate)
		return infostring

	def info(self):
		info = { 
			"LSD version":__version__,
			"PySDL2 version":self.pysdl2_version,
			"SDL2 version":self.sdl2_version,
			"CPU count":self.cpu_count,
			"Current display driver":self.display_driver,
			"Display count":self.display_count,
			"Window dimensions":self.resolution,
			"Available display drivers":self.display_drivers,
		}
		
		for dispnum, display in enumerate(self.displays):
			cur_disp_info = {}			
			cur_disp_info["Resolution"] = (display.w, display.h)
			cur_disp_info["Refresh rate"] = display.refresh_rate
			info["Display {}".format(dispnum)] = cur_disp_info
			
		
		return info

	def get_available_display_drivers(self):
		drivers = []
		for vd in range(sdl2.SDL_GetNumVideoDrivers()):
			drivers.append(sdl2.SDL_GetVideoDriver(vd))
		return drivers


def create_window(resolution,title="SDL2 Display Window", fullscreen=False):
	global current_sdl2_environment
	if type(resolution) != tuple and len(resolution) != 2:
		raise TypeError("Please make sure the resolution variable is a tuple with (width,height)")
	(width,height) = resolution
	sdl2.ext.init()

	flags = None
	if fullscreen:
		flags = flags|sdl2.SDL_WINDOW_FULLSCREEN
	
	window = sdl2.ext.Window(title, size=(width, height), flags=flags)
	window.show()

	# Create a render system that renders to the window surface
	renderer = sdl2.ext.Renderer(window)
	renderer.clear(0)
	renderer.present()
	# Create sprite factory to create textures with later
	texture_factory = sdl2.ext.SpriteFactory(renderer=renderer)
	# Create sprite factory to create surfaces with later
	surface_factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)

	sdl2env = SDL2Environment(window,resolution,renderer, texture_factory, surface_factory)
	current_sdl2_environment= sdl2env
	window.refresh()
	return sdl2env

def destroy_window():
	global current_sdl2_environment
	current_sdl2_environment = None
	del(current_sdl2_environment)
	sdl2.ext.quit()

current_sdl2_environment = None
