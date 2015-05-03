# -*- coding: utf-8 -*-
"""
Created on Sat May  2 12:47:20 2015

@author: Daniel Schreij

[Insert Licence info here]

"""
# Python 3 compatibility
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

# SDL2 libraries
import sdl2.ext
from sdl2 import sdlgfx
from sdl2 import sdlimage

# misc
import LSD
from functools import wraps

class FrameBuffer(object):
	
	def __init__(self, environment):
		if type(environment) != LSD.SDL2Environment:
			raise TypeError("ERROR: context argument should be of type LSD.SDL2Environment")
		self.environment = environment	
		self.surface = environment.factory.create_sprite(size=environment.resolution, access=sdl2.SDL_TEXTUREACCESS_TARGET)
		self.renderer = environment.renderer
		self.sdl_renderer = self.renderer.renderer
		
		self.clear()		
	
	# Decorator
	def to_texture(drawing_function):
		
		@wraps(drawing_function)
		def wrapped(inst, *args, **kwargs):	
			tex_set = sdl2.SDL_SetRenderTarget(inst.sdl_renderer, inst.surface.texture)
			if tex_set != 0:
				raise Exception("Could not set FrameBuffers texture as rendering target")
			result = drawing_function(inst, *args, **kwargs)
			tex_unset = sdl2.SDL_SetRenderTarget(inst.sdl_renderer, None)
			if tex_unset != 0:
				raise Exception("Could not release FrameBuffers texture as rendering target")
			return result
		return wrapped


	@to_texture	
	def clear(self, color=0):
		color = sdl2.ext.convert_to_color(color)
		self.renderer.clear(color)	
	
	@to_texture
	def draw_circle(self, x, y, r, color, fill=True, aa=False):
		color = sdl2.ext.convert_to_color(color)
		if fill:		
			sdlgfx.filledCircleColor(self.sdl_renderer, x, y, r, color)
		elif aa:
			sdlgfx.aacircleColor(self.sdl_renderer, x, y, r, color)
		else:
			sdlgfx.circleColor(self.sdl_renderer, x, y, r, color)
	
	@to_texture	
	def draw_rect(self, x, y, w, h, color, border_radius=0, fill=True):
		color = sdl2.ext.convert_to_color(color)
		
		if fill:						
			if border_radius:
				sdl2.sdlgfx.roundedBoxColor(self.sdl_renderer, x, y, x+w, y+h, border_radius, color)
			else:
				sdl2.sdlgfx.boxColor(self.sdl_renderer, x, y, x+w, y+h, color)
		else:
			if border_radius:
				sdl2.sdlgfx.roundedRectangleColor(self.sdl_renderer, x, y, x+w, y+h, border_radius, color)
			else:
				sdl2.sdlgfx.rectangleColor(self.sdl_renderer, x, y, x+w, y+h, color)

				
	def show(self):
		self.renderer.copy(self.surface)
		self.renderer.present()
		self.environment.window.refresh()
		
	def __del__(self):
		del([self.renderer, self.surface, self.sdl_renderer])

		