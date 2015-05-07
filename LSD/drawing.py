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

# misc
import LSD
from functools import wraps
import ctypes

class FrameBuffer(object):

	def __init__(self, environment, background_color=0):
		if type(environment) != LSD.SDL2Environment:
			raise TypeError("ERROR: context argument should be of type LSD.SDL2Environment")
		self.environment = environment
		self.surface = environment.texture_factory.create_sprite(size=environment.resolution, access=sdl2.SDL_TEXTUREACCESS_TARGET)
		
		# pysdl2 render object (to interface with the renderer)
		self.renderer = environment.renderer
		# Low-level SDL renderer (needs to be passed to all sdlgfx functions)
		self.sdl_renderer = self.renderer.renderer
		# Renderer for images (sprites) as textures
		self.spriterenderer = environment.texture_factory.create_sprite_render_system()
		
		# Renderer for images (sprites) as surfaces (software mode)		
		self.background_color = background_color
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
	def clear(self, color=None):
		if color is None:
			color = self.background_color
		color = sdl2.ext.convert_to_color(color)
		self.renderer.clear(color)

	@to_texture
	def draw_circle(self, x, y, r, color, opacity=1.0, fill=True, aa=False):
		color = sdl2.ext.convert_to_color(color)
		if fill:
			return sdlgfx.filledCircleRGBA(self.sdl_renderer, x, y, r, color.r, color.g, color.b, int(opacity*255))
		elif aa:
			return sdlgfx.aacircleRGBA(self.sdl_renderer, x, y, r, color.r, color.g, color.b, int(opacity*255))
		else:
			return sdlgfx.circleRGBA(self.sdl_renderer, x, y, r, color.r, color.g, color.b, int(opacity*255))

	@to_texture
	def draw_ellipse(self, x, y, rx, ry, color, opacity=1.0, fill=True, aa=False):
		color = sdl2.ext.convert_to_color(color)

		if fill:
			return sdl2.sdlgfx.filledEllipseRGBA(self.sdl_renderer, x, y, rx, ry, color.r, color.g, color.b, int(opacity*255))
		elif aa:
			return sdl2.sdlgfx.aaellipseRGBA(self.sdl_renderer, x, y, rx, ry, color.r, color.g, color.b, int(opacity*255))
		else:
			return sdl2.sdlgfx.ellipseRGBA(self.sdl_renderer, x, y, rx, ry, color.r, color.g, color.b, int(opacity*255))

	@to_texture
	def draw_rect(self, x, y, w, h, color, opacity=1.0, fill=True, border_radius=0):
		color = sdl2.ext.convert_to_color(color)
		if fill:
			if border_radius > 0:
				return sdl2.sdlgfx.roundedBoxRGBA(self.sdl_renderer, x, y, x+w, y+h, border_radius, color.r, color.g, color.b, int(opacity*255))
			else:
				return sdl2.sdlgfx.boxRGBA(self.sdl_renderer, x, y, x+w, y+h, color.r, color.g, color.b, int(opacity*255))
		else:
			if border_radius > 0:
				return sdl2.sdlgfx.roundedRectangleRGBA(self.sdl_renderer, x, y, x+w, y+h, border_radius, color.r, color.g, color.b, int(opacity*255))
			else:
				return sdl2.sdlgfx.rectangleRGBA(self.sdl_renderer, x, y, x+w, y+h, color.r, color.g, color.b, int(opacity*255))

	@to_texture
	def draw_line(self, x1, y1, x2, y2, color, opacity=1.0, aa=False, width=1):
		color = sdl2.ext.convert_to_color(color)
		if width < 1:
			raise ValueError("Line width cannot be smaller than 1px")
		
		if width > 1:
			return sdl2.sdlgfx.thickLineRGBA(self.sdl_renderer, x1, y1, x2, y2, width, color.r, color.g, color.b, int(opacity*255))
		if not aa:
			return sdl2.sdlgfx.lineRGBA(self.sdl_renderer, x1, y1, x2, y2, color.r, color.g, color.b, int(opacity*255))
		else:
			return sdl2.sdlgfx.aalineRGBA(self.sdl_renderer, x1, y1, x2, y2, color.r, color.g, color.b, int(opacity*255))

	@to_texture
	def draw_text(self, x, y, text, color, opacity=1.0):
		color = sdl2.ext.convert_to_color(color)
		return sdl2.sdlgfx.stringRGBA(self.sdl_renderer, x, y, text, color.r, color.g, color.b, int(opacity*255))

	@to_texture
	def draw_arc(self, x, y, r, start, end, color, opacity=1.0):
		color = sdl2.ext.convert_to_color(color)
		return sdl2.sdlgfx.arcRGBA(self.sdl_renderer, x, y, r, start, end,  color.r, color.g, color.b, int(opacity*255))

	@to_texture
	def draw_pie(self, x, y, r, start, end, color, opacity=1.0, fill=True):
		color = sdl2.ext.convert_to_color(color)
		if fill:
			return sdl2.sdlgfx.filledPieRGBA(self.sdl_renderer, x, y, r, start, end, color.r, color.g, color.b, int(opacity*255))
		else:			
			return sdl2.sdlgfx.pieRGBA(self.sdl_renderer, x, y, r, start, end, color.r, color.g, color.b, int(opacity*255))

	@to_texture
	def draw_trigon(self, x1, y1, x2, y2, x3, y3, color, opacity=1.0, fill=True, aa=False):
		color = sdl2.ext.convert_to_color(color)
		if fill:
			return sdl2.sdlgfx.filledTrigonRGBA(self.sdl_renderer, x1, y1, x2, y2, x3, y3, color.r, color.g, color.b, int(opacity*255))
		elif aa:
			return sdl2.sdlgfx.aatrigonRGBA(self.sdl_renderer, x1, y1, x2, y2, x3, y3, color.r, color.g, color.b, int(opacity*255))
		else:
			return sdl2.sdlgfx.trigonRGBA(self.sdl_renderer, x1, y1, x2, y2, x3, y3, color.r, color.g, color.b, int(opacity*255))
	
	@to_texture
	def draw_polygon(self, vx, vy, color, opacity=1.0, fill=True, aa=False, texture=None):
		color = sdl2.ext.convert_to_color(color)
		if len(vx) != len(vy):
			raise ValueError('vx and vy do not have the same number of items')
		n = len(vx)
		
		# Make sure all coordinates are integers
		vx = map(int,vx)
		vy = map(int,vy)
		# Cast the list to the appropriate ctypes vectors reabable by
		# the polygon functions
		vx = ctypes.cast((sdl2.Sint16*n)(*vx), ctypes.POINTER(sdl2.Sint16))
		vy = ctypes.cast((sdl2.Sint16*n)(*vy), ctypes.POINTER(sdl2.Sint16))
		
		if texture:
			sprite = self.environment.surface_factory.from_image(texture)
			return sdl2.sdlgfx.texturedPolygon(self.sdl_renderer, vx, vy, n, sprite.surface, ctypes.c_int(0), ctypes.c_int(0))
		elif fill:
			return sdl2.sdlgfx.filledPolygonRGBA(self.sdl_renderer, vx, vy, n, color.r, color.g, color.b, int(opacity*255))
		elif aa:
			return sdl2.sdlgfx.aapolygonRGBA(self.sdl_renderer, vx, vy, n, color.r, color.g, color.b, int(opacity*255))
		else:
			return sdl2.sdlgfx.polygonRGBA(self.sdl_renderer, vx, vy, n, color.r, color.g, color.b, int(opacity*255))
			
	@to_texture
	def draw_bezier_curve(self, vx, vy, s, color, opacity=1.0):		
		color = sdl2.ext.convert_to_color(color)
		if len(vx) != len(vy):
			raise ValueError('vx and vy do not have the same number of items')
		n = len(vx)
		
		# Make sure all coordinates are integers
		vx = map(int,vx)
		vy = map(int,vy)
		# Cast the list to the appropriate ctypes vectors reabable by
		# the polygon functions
		vx = ctypes.cast((sdl2.Sint16*n)(*vx), ctypes.POINTER(sdl2.Sint16))
		vy = ctypes.cast((sdl2.Sint16*n)(*vy), ctypes.POINTER(sdl2.Sint16))
		
		return sdl2.sdlgfx.bezierRGBA(self.sdl_renderer, vx, vy, n, s, color.r, color.g, color.b, int(opacity*255))

	@to_texture
	def draw_image(self, x, y, image_path):
		image = self.environment.texture_factory.from_image(image_path)
		image.position = (x,y)
		return self.spriterenderer.render(image)

	def show(self):
		self.renderer.clear()
		self.renderer.copy(self.surface)
		return self.renderer.present()

	def __del__(self):
		del([self.renderer, self.surface, self.sdl_renderer, self.spriterenderer])

