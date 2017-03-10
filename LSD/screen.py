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
import sdl2
import sdl2.ext
from sdl2 import sdlgfx

# LSD package libraries
from .util import *

# misc
from functools import wraps
import time

class FrameBuffer(object):

	def __init__(self, sdl2env=None, background_color=0):
		self.environment = check_sdl2env(sdl2env)
		
		self.surface = self.environment.texture_factory.create_sprite(
			size=self.environment.resolution,
			access=sdl2.SDL_TEXTUREACCESS_TARGET
		)

		# pysdl2 render object (to interface with the renderer)
		self.renderer = self.environment.renderer
		# Low-level SDL renderer (needs to be passed to all sdlgfx functions)
		self.sdl_renderer = self.renderer.sdlrenderer

		# Renderer for images (sprites) as textures
		self.spriterenderer = self.environment.texture_factory.create_sprite_render_system()

		# Renderer for images (sprites) as surfaces (software mode)
		self.background_color = sdl2.ext.convert_to_color(background_color)
		self.clear()

		# Add this buffer to the list of active framebuffers in the environment
		self.environment.active_framebuffers.append(self)

	# Decorator
	def to_texture(function):
		@wraps(function)
		def wrapped(inst, *args, **kwargs):
			if sdl2.SDL_SetRenderTarget(inst.sdl_renderer, inst.surface.texture) != 0:
				raise Exception("Could not set FrameBuffers texture as rendering"
					" target: {}".format(sdl2.SDL_GetError()))
			# Perform the drawing operation
			result = function(inst, *args, **kwargs)
			# Unset the texture as render target
			if sdl2.SDL_SetRenderTarget(inst.sdl_renderer, None) != 0:
				raise Exception("Could not unset FrameBuffers texture as rendering"
					" target: {}".format(sdl2.SDL_GetError()))
			return result
		return wrapped

	@to_texture
	def clear(self, color=None):
		if color is None:
			color = self.background_color
		color = sdl2.ext.convert_to_color(color)
		self.renderer.clear(color)
		return self

	@to_texture
	def add(self, texture, **kwargs):
		# Fails if x or y = 0, which is a valid use case. FIX!
		x = kwargs.get('x', None)
		if type(x) != int:
			x = texture.x
			if type(x) != int:
				raise ValueError("x coordinate not specified")

		y = kwargs.get('y', None)
		if type(y) != int:
			y = texture.y
			if type(y) != int:
				raise ValueError("y coordinate not specified")
		
		# Set the desired transparency value to the texture
		alpha = kwargs.get('opacity', None)
		if alpha:
			sdl2.SDL_SetTextureAlphaMod(texture.texture, self.opacity(alpha))

		angle = kwargs.get('angle', None) 
		if type(angle) != int:
		 	angle = texture.angle or 0

		flip = kwargs.get('flip', None)
		if not flip:
			flip = texture.flip
		elif flip == "hor":
			flip = sdl2.SDL_FLIP_HORIZONTAL
		elif flip == "ver":
			flip = sdl2.SDL_FLIP_VERTICAL

		if flip is None:
			flip = sdl2.SDL_FLIP_NONE

		rotation_center = kwargs.get('rotation_center', None)
		if not type(rotation_center) in [tuple,list] or len(rotation_center) == 2:
			rotation_center = texture.center

		# Calculate the dest_rect and copy the texture
		dest_rect = (x, y, texture.size[0], texture.size[1])

		self.renderer.copy(texture, dstrect=dest_rect, angle=angle, flip=flip)
		return self

	def show(self):
		t1 = sdl2.SDL_GetTicks()

		# The destination rectangle on the surface
		# Only calculate if the drawing frame dimensions are different from the window size
		if self.environment.resolution == self.environment.window.size:
			dest_rect = None
		else:
			w_w, w_h = self.environment.window.size
			f_w, f_h = self.environment.resolution
			w, h = self.environment.resolution

			# Make sure the texture is centered on the screen
			x = int(w_w/2 - f_w/2)
			y = int(w_h/2 - f_h/2)
			dest_rect = (x, y, w, h)

		self.renderer.clear(0)
		self.renderer.copy(self.surface, dstrect=dest_rect)
		self.renderer.present()
		drawing_delay = sdl2.SDL_GetTicks() - t1
		return (time.time(), drawing_delay)

	def __del__(self):
		sdl2.SDL_DestroyTexture(self.surface.texture)
		del([self.renderer, self.surface, self.sdl_renderer, self.spriterenderer])
		# Remove this buffer from lists of active buffers in environment!

