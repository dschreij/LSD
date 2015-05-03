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

class DisplayContext(object):
	
	def __init__(self, window, resolution, display_driver):
		self.window = window
		self.resolution = resolution
		self.display_driver = display_driver
		
	def print_contents(self):
		print("Resolution: {0}".format(self.resolution))
		print("Display driver: {0}".format(self.display_driver))
		

def create_window((width,height),title="LSD"):
	sdl2.ext.init()
	window = sdl2.ext.Window(title, size=(width, height))
	window.show()
	return DisplayContext(window,(width,height), sdl2.SDL_GetVideoDriver(0))