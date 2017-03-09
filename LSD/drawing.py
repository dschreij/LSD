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

from . import inject_sdl_environment, SDL2Environment

# misc
from .util import *
from functools import wraps
import ctypes
import time

# def use_texture(drawing_function):
# 	""" Decorator function for drawing functions.wraps

# 	This decorator is used to create a texture for the drawing function to draw
# 	on and sets it as the renderers current target. After the drawing function is
# 	finished it sets back the renderer to its original
# 	"""
# 	@wraps(drawing_function)
# 	@inject_sdl_environment
# 	def wrapped(*args, **kwargs):
		# sdl2env = kwargs.get("sdl2env", None)
		# if type(sdl2env) != SDL2Environment:
		# 	raise TypeError("passed sdl2env parameter is not a SDL2Environment object")

		# target_texture = sdl2env.texture_factory.create_texture_sprite(
		# 	sdl2env.renderer,

		# )

# 		if sdl2.SDL_SetRenderTarget(sdl2env.sdl_renderer, inst.surface.texture) != 0:
# 			raise Exception("Could not set FrameBuffers texture as rendering"
# 				" target: {}".format(sdl2.SDL_GetError()))
# 		# Perform the drawing operation
# 		result = drawing_function(inst, *args, **kwargs)
# 		# Unset the texture as render target
# 		if sdl2.SDL_SetRenderTarget(sdl2env.sdl_renderer, None) != 0:
# 			raise Exception("Could not unset FrameBuffers texture as rendering"
# 				" target: {}".format(sdl2.SDL_GetError()))
# 		return result
# 	return wrapped

@inject_sdl_environment
def circle(x, y, r, color, opacity=1.0, fill=True, aa=False, penwidth=1, 
	rotation_center=None, rotation=0, flip=None, **kwargs):
	# Make sure all spatial parameters are ints
	x, y, r = int(x), int(y), int(r)
	# Check if sdl2env is passed (implicitly or explicitly)
	sdl2env = check_sdl2env(kwargs.get("sdl2env", None))
	sdlrenderer = sdl2env.renderer.sdlrenderer

	# convert color parameter to sdl2 understandable values
	color = sdl2.ext.convert_to_color(color)
	# convert possible opacity values to the right scale
	opacity = convert_opacity(opacity)

	# Check for invalid penwidth values, and make sure the value is an int
	if type(penwidth) in [int, float]:
		if penwidth < 1:
			raise ValueError("Penwidth cannot be smaller than 1")
		else:
			penwidth = int(penwidth)
	else:
		raise TypeError("Penwidth needs to be int or float")
	
	# Check for invalid r values, and make sure the value is an int
	if type(r) in [int, float]:
		if r < 1:
			raise ValueError("r cannot be smaller than 1")
		else:
			r = int(r)
	else:
		raise TypeError("r needs to be int or float")

	if flip is None:
		flip = sdl2.SDL_FLIP_NONE
	elif flip == "horizontal":
		flip = sdl2.SDL_FLIP_HORIZONTAL
	elif flip == "vertical":
		flip = sdl2.SDL_FLIP_VERTICAL	

	# Calculate the required dimensions for the target texture
	outer_r, inner_r = int(r+penwidth*.5), int(r-penwidth*.5)

	# Calculate the required dimensions of the extra texture we are
	# going to draw the circle on. Add 1 pixel to account for division
	# errors (i.e. dividing an odd number of pixels)
	c_width, c_height = outer_r*2+1, outer_r*2+1

	target_texture = sdl2env.texture_factory.create_sprite(
		size=(c_width, c_height),
		access=sdl2.SDL_TEXTUREACCESS_TARGET
	)

	# Set texture as render target (from now on sdlrenderer draws on this texture)
	if sdl2.SDL_SetRenderTarget(sdlrenderer, target_texture.texture) != 0:
		raise Exception("Could not set circle texture as rendering target: "
			"{}".format(sdl2.SDL_GetError()))

	# if only a filled circle needs to be drawn, it's easy
	if fill:
		sdlgfx.filledCircleRGBA(sdlrenderer, r, r, r, color.r, color.g, color.b, opacity)
	else:
		# If penwidth is 1, simply use sdl2gfx's own functions
		if penwidth == 1:
			if aa:
		 		sdlgfx.aacircleRGBA(sdlrenderer, r, r, r, color.r, color.g, color.b, opacity)
			else:
				sdlgfx.circleRGBA(sdlrenderer, r, r, r, color.r, color.g, color.b, opacity)
		else:
			# If the penwidth is larger than 1, things become a bit more complex.
			# To ensure that the interior of the circle is transparent, we will
			# have to work with multiple textures and blending.
			outer_r, inner_r = int(r+penwidth*.5), int(r-penwidth*.5)

			# Calculate the required dimensions of the extra texture we are
			# going to draw the circle on. Add 1 pixel to account for division
			# errors (i.e. dividing an odd number of pixels)
			c_width, c_height = outer_r*2+1, outer_r*2+1

			# Create the circle texture, and make sure it can be a rendering
			# target by setting the correct access flag.
			circle_sprite = self.environment.texture_factory.create_software_sprite(
				size=(c_width, c_height)
			)
			# Create a renderer to draw to the circle sprite
			sprite_renderer = sdl2.ext.Renderer(circle_sprite)

			# Determine the optimal color key to use for this operation
			colorkey_color = self.determine_optimal_colorkey(color, self.background_color)
			
			# Clear the sprite with the colorkey color
			sprite_renderer.clear(colorkey_color)

			# Draw the annulus:
			sdlgfx.filledCircleRGBA(sprite_renderer.sdlrenderer, outer_r, outer_r,
				outer_r, color.r, color.g, color.b, 255)
			# Antialias if desired
			if aa:
				for i in range(-1,1):
					for j in range(2):
						sdlgfx.aacircleRGBA(sprite_renderer.sdlrenderer, outer_r,
							outer_r, outer_r+i, color.r, color.g, color.b, 255)
					
			# Draw the hole
			sdlgfx.filledCircleRGBA(sprite_renderer.sdlrenderer, outer_r, outer_r,
				inner_r, colorkey_color.r, colorkey_color.g, colorkey_color.b, 255)
			# Antialias if desired
			if aa:
				for i in range(0,2):
					for j in range(2):
						sdlgfx.aacircleRGBA(sprite_renderer.sdlrenderer, outer_r,
							outer_r, inner_r+i, color.r, color.g, color.b, 255)

			# Optimize drawing of transparent pixels
			sdl2.SDL_SetSurfaceRLE(circle_sprite.surface, 1)

			# Convert the colorkey to a format understandable by the 
			# SDL_SetColorKey function
			colorkey = sdl2.SDL_MapRGB(circle_sprite.surface.format, 
				colorkey_color.r, colorkey_color.g, colorkey_color.b)

			# Set transparency color key
			sdl2.SDL_SetColorKey(circle_sprite.surface, sdl2.SDL_TRUE, colorkey)

			# Create a texture from the circle sprite
			circle_texture = self.environment.texture_factory.from_surface(
				circle_sprite.surface
			)
			
			# Perform the blitting operation
			renderer.copy( circle_texture, dstrect=(0, 0, c_width, c_height))

			# Cleanup
			del(circle_sprite)
			del(sprite_renderer)

	# Set the desired transparency value to the texture
	sdl2.SDL_SetTextureAlphaMod(target_texture.texture, opacity)
	sdl2.SDL_SetTextureBlendMode(target_texture.texture, sdl2.SDL_BLENDMODE_BLEND)

	# Free texture as render target
	if sdl2.SDL_SetRenderTarget(sdlrenderer, None) != 0:
		raise Exception("Could not free circle texture as rendering target: "
			"{}".format(sdl2.SDL_GetError()))

	target_texture.x = x
	target_texture.y = y
	target_texture.r = r
	target_texture.opacity = opacity
	target_texture.center = rotation_center
	target_texture.angle = rotation
	target_texture.flip = flip
	return target_texture
		

@inject_sdl_environment
def ellipse(x, y, rx, ry, color, opacity=1.0, fill=True, aa=False, 
	penwidth=1, rotation=0, center=True):
	# Make sure all spatial parameters are ints
	x, y, rx, ry, penwidth = map(int,(x ,y, rx, ry, penwidth))

	if penwidth < 1:
		raise ValueError("Penwidth cannot be smaller than 1")

	width, height = 2*(rx+penwidth)+1, 2*(ry+penwidth)+1

	if not center:
		x, y = int(x - width/2), int(y - height/2)

	color = sdl2.ext.COLOR(color)
	opacity = self.opacity(opacity)

	if penwidth > 1:
		start_rx = rx - int(penwidth/2)
		start_ry = ry - int(penwidth/2)
		if start_rx < 1 or start_ry < 1:
			raise ValueError("Penwidth to large for a ellipse with this radius")

	if fill:
		sdlgfx.filledEllipseRGBA(self.sdl_renderer, x, y, rx, ry, color.r, color.g, color.b, opacity)
		if aa:
			sdlgfx.ellipseRGBA(self.sdl_renderer, x, y, rx, ry, color.r, color.g, color.b, opacity)
			sdlgfx.aaellipseRGBA(self.sdl_renderer, x, y, rx, ry, color.r, color.g, color.b, opacity)

	elif penwidth == 1:
		if aa:
			sdlgfx.aaellipseRGBA(self.sdl_renderer, x, y, rx, ry, color.r, color.g, color.b, opacity)
		else:
			sdlgfx.ellipseRGBA(self.sdl_renderer, x, y, rx, ry, color.r, color.g, color.b, opacity)
	else:
		# Create the circle texture, and make sure it can be a rendering
		# target by setting the correct access flag.
		ellipse_sprite = self.environment.texture_factory.create_software_sprite(
			size=(width, height),
		)
		# Create a renderer to draw to the circle sprite
		sprite_renderer = sdl2.ext.Renderer(ellipse_sprite)

		# Determine the optimal color key to use for this operation
		colorkey_color = self.determine_optimal_colorkey(color, self.background_color)
		
		# Clear the sprite with the colorkey color
		sprite_renderer.clear(colorkey_color)

		# Annulus
		sdlgfx.filledEllipseRGBA(sprite_renderer.sdlrenderer, rx+penwidth, ry+penwidth, 
			rx+int(penwidth/2), ry+int(penwidth/2), color.r, color.g, color.b, 255)
		
		# Hole
		sdlgfx.filledEllipseRGBA(sprite_renderer.sdlrenderer, rx+penwidth, ry+penwidth, 
			rx-int(penwidth/2), ry-int(penwidth/2), colorkey_color.r, 
			colorkey_color.g, colorkey_color.b, 255)
		
		if aa:
			# Annulus
			for i in range(-1,1):
				for j in range(2):
					sdlgfx.aaellipseRGBA(sprite_renderer.sdlrenderer, rx+penwidth, 
						ry+penwidth, rx+int(penwidth/2)+i, ry+int(penwidth/2)+i, 
						color.r, color.g, color.b, opacity)
			
			# Hole
			for i in range(0,2):
				for j in range(2):
					sdlgfx.aaellipseRGBA(sprite_renderer.sdlrenderer, rx+penwidth, 
						ry+penwidth, rx-int(penwidth/2)+i, ry-int(penwidth/2)+i, 
						color.r, color.g, color.b, opacity)
		
		# Optimize drawing of transparent pixels
		sdl2.SDL_SetSurfaceRLE(ellipse_sprite.surface, 1)

		# Convert the colorkey to a format understandable by the 
		# SDL_SetColorKey function
		colorkey = sdl2.SDL_MapRGB(ellipse_sprite.surface.format, 
			colorkey_color.r, colorkey_color.g, colorkey_color.b)

		# Set transparency color key
		sdl2.SDL_SetColorKey(ellipse_sprite.surface, sdl2.SDL_TRUE, colorkey)

		# Create a texture from the circle sprite
		ellipse_tex = self.environment.texture_factory.from_surface(
			ellipse_sprite.surface
		)

		# Set the desired transparency value to the texture
		sdl2.SDL_SetTextureAlphaMod(ellipse_tex.texture, opacity)

		# Perform the blitting operation
		if center:
			x, y = int(x - width/2), int(y - height/2)
		self.renderer.copy( ellipse_tex, dstrect=(x, y, width, height), 
			angle=rotation )

		# Cleanup
		del(ellipse_sprite)
		del(sprite_renderer)

	return self

@inject_sdl_environment
def rect(x, y, w, h, color, opacity=1.0, fill=True, border_radius=0, penwidth=1):
	# Make sure all spatial parameters are ints
	x, y, w, h = map(int, (x, y, w, h))

	color = sdl2.ext.convert_to_color(color)

	if penwidth != 1:
		if penwidth < 1:
			raise ValueError("Penwidth cannot be smaller than 1")
		if penwidth > 1:
			penwidth = int(penwidth)
		start_x = x - int(penwidth/2)
		start_y = y - int(penwidth/2)
		start_w = w - int(penwidth)
		start_h = h - int(penwidth)

		if start_x < 1 or start_y < 1:
			raise ValueError("Penwidth to large for a rect with these dimensions")

		x_s = range(start_x,start_x+penwidth)
		y_s = range(start_y,start_y+penwidth)
		w_s = range(start_w+2*penwidth, start_w, -2)
		h_s = range(start_h+2*penwidth, start_h, -2)
		rects = zip(x_s,y_s,w_s,h_s)
	else:
		rects = [(x,y,w,h)]

	if fill:
		if border_radius > 0:
			sdl2.sdlgfx.roundedBoxRGBA(self.sdl_renderer, x, y, x+w, y+h, 
				border_radius, color.r, color.g, color.b, int(opacity*255))
		else:
			sdl2.sdlgfx.boxRGBA(self.sdl_renderer, x, y, x+w, y+h, color.r, 
				color.g, color.b, int(opacity*255))
	else:
		for x,y,w,h in rects:
			if border_radius > 0:
				sdl2.sdlgfx.roundedRectangleRGBA(self.sdl_renderer, x, y, 
					x+w, y+h, border_radius, color.r, color.g, color.b, int(opacity*255))
			else:
				sdl2.sdlgfx.rectangleRGBA(self.sdl_renderer, x, y, x+w, y+h, 
					color.r, color.g, color.b, int(opacity*255))
	return self

@inject_sdl_environment
def line(x1, y1, x2, y2, color, opacity=1.0, aa=False, width=1):
	# Make sure all spatial parameters are ints
	x1, y1, x2, y2 = map(int, (x1, y1, x2, y2))

	color = sdl2.ext.convert_to_color(color)
	if width < 1:
		raise ValueError("Line width cannot be smaller than 1px")

	if width > 1:
		return sdl2.sdlgfx.thickLineRGBA(self.sdl_renderer, x1, y1, x2, y2, 
			width, color.r, color.g, color.b, int(opacity*255))
	if not aa:
		return sdl2.sdlgfx.lineRGBA(self.sdl_renderer, x1, y1, x2, y2, 
			color.r, color.g, color.b, int(opacity*255))
	else:
		return sdl2.sdlgfx.aalineRGBA(self.sdl_renderer, x1, y1, x2, y2, 
			color.r, color.g, color.b, int(opacity*255))

@inject_sdl_environment
def text(x, y, text, color, opacity=1.0):
	# Make sure all spatial parameters are ints
	x,y = int(x), int(y)

	# Make sure the passed text is of type 'bytes'
	text = sdl2.ext.compat.byteify(text, 'utf8')
	print(text)

	color = sdl2.ext.convert_to_color(color)
	sdl2.sdlgfx.stringRGBA(self.sdl_renderer, x, y, text, color.r, color.g, color.b, self.opacity(opacity))
	return self

@inject_sdl_environment
def arc(x, y, r, start, end, color, opacity=1.0, penwidth=1):
	# Make sure all spatial parameters are ints
	x, y, r = map(int, (x, y, r))

	color = sdl2.ext.convert_to_color(color)
	if penwidth != 1:
		if penwidth < 1:
			raise ValueError("Penwidth cannot be smaller than 1")
		if penwidth > 1:
			penwidth = int(penwidth)
		start_r = r - int(penwidth/2)
		if start_r < 1:
			raise ValueError("Penwidth to large for a circle with this radius")
		r_s = range(start_r,start_r+penwidth)
	else:
		r_s = [r]

	if not r_s is None:
		for r in r_s:
			sdl2.sdlgfx.arcRGBA(self.sdl_renderer, x, y, r, start, end,  color.r, color.g, color.b, int(opacity*255))
	return self

@inject_sdl_environment
def pie(x, y, r, start, end, color, opacity=1.0, fill=True):
	# Make sure all spatial parameters are ints
	x, y, r = map(int, (x, y, r))

	color = sdl2.ext.convert_to_color(color)
	if fill:
		return sdl2.sdlgfx.filledPieRGBA(self.sdl_renderer, x, y, r, start, end, color.r, color.g, color.b, int(opacity*255))
	else:
		return sdl2.sdlgfx.pieRGBA(self.sdl_renderer, x, y, r, start, end, color.r, color.g, color.b, int(opacity*255))
	return self

@inject_sdl_environment
def trigon(x1, y1, x2, y2, x3, y3, color, opacity=1.0, fill=True, aa=False):
	# Make sure all spatial parameters are ints
	x1, y1, x2, y2, x3, y3 = map(int, (x1, y1, x2, y2, x3, y3))

	color = sdl2.ext.convert_to_color(color)
	if fill:
		return sdl2.sdlgfx.filledTrigonRGBA(self.sdl_renderer, x1, y1, x2, y2, x3, y3, color.r, color.g, color.b, int(opacity*255))
	elif aa:
		return sdl2.sdlgfx.aatrigonRGBA(self.sdl_renderer, x1, y1, x2, y2, x3, y3, color.r, color.g, color.b, int(opacity*255))
	else:
		return sdl2.sdlgfx.trigonRGBA(self.sdl_renderer, x1, y1, x2, y2, x3, y3, color.r, color.g, color.b, int(opacity*255))
	return self

@inject_sdl_environment
def polygon(vx, vy, color, opacity=1.0, fill=True, aa=False, texture=None):
	color = sdl2.ext.convert_to_color(color)
	if len(vx) != len(vy):
		raise ValueError('vx and vy do not have the same number of items')
	n = len(vx)

	# Make sure all coordinates are integers
	vx = map(int,vx)
	vy = map(int,vy)
	# Cast the list to the appropriate ctypes vectors readable by
	# the polygon functions
	vx = ctypes.cast((sdl2.Sint16*n)(*vx), ctypes.POINTER(sdl2.Sint16))
	vy = ctypes.cast((sdl2.Sint16*n)(*vy), ctypes.POINTER(sdl2.Sint16))

	if not texture is None:
		if type(texture) == tuple and len(texture) == 3:
			(img,offset_x,offset_y) = texture
		if type(texture) == str:
			img = texture
			offset_x = offset_y = 0
		sprite = self.environment.surface_factory.from_image(img)
		sdl2.sdlgfx.texturedPolygon(self.sdl_renderer, vx, vy, n, sprite.surface, offset_x, offset_y)
	elif fill:
		sdl2.sdlgfx.filledPolygonRGBA(self.sdl_renderer, vx, vy, n, color.r, color.g, color.b, int(opacity*255))
	elif aa:
		sdl2.sdlgfx.aapolygonRGBA(self.sdl_renderer, vx, vy, n, color.r, color.g, color.b, int(opacity*255))
	else:
		sdl2.sdlgfx.polygonRGBA(self.sdl_renderer, vx, vy, n, color.r, color.g, color.b, int(opacity*255))
	return self

@inject_sdl_environment
def bezier_curve(vx, vy, s, color, opacity=1.0):
	color = sdl2.ext.convert_to_color(color)
	if len(vx) != len(vy):
		raise ValueError('vx and vy do not have the same number of items')
	n = len(vx)

	# Make sure all coordinates are integers
	vx = map(int,vx)
	vy = map(int,vy)
	# Cast the list to the appropriate ctypes vectors readable by
	# the polygon functions
	vx = ctypes.cast((sdl2.Sint16*n)(*vx), ctypes.POINTER(sdl2.Sint16))
	vy = ctypes.cast((sdl2.Sint16*n)(*vy), ctypes.POINTER(sdl2.Sint16))

	sdl2.sdlgfx.bezierRGBA(self.sdl_renderer, vx, vy, n, s, color.r, color.g, color.b, int(opacity*255))
	return self

@inject_sdl_environment
def image(x, y, image_path):
	x,y = int(x), int(y)

	image = self.environment.texture_factory.from_image(image_path)
	image.position = (x,y)
	self.spriterenderer.render(image)
	return self
