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

# misc
import LSD
from functools import wraps
import ctypes
import time

class FrameBuffer(object):

	def __init__(self, environment, background_color=0):
		if type(environment) != LSD.SDL2Environment:
			raise TypeError("ERROR: context argument should be of type LSD.SDL2Environment")
		self.environment = environment
		self.surface = environment.texture_factory.create_sprite(
			size=environment.resolution,
			access=sdl2.SDL_TEXTUREACCESS_TARGET
		)

		# pysdl2 render object (to interface with the renderer)
		self.renderer = environment.renderer
		# Low-level SDL renderer (needs to be passed to all sdlgfx functions)
		self.sdl_renderer = self.renderer.sdlrenderer

		# Renderer for images (sprites) as textures
		self.spriterenderer = environment.texture_factory.create_sprite_render_system()

		# Renderer for images (sprites) as surfaces (software mode)
		self.background_color = sdl2.ext.convert_to_color(background_color)
		self.clear()

		# Add this buffer to the list of active framebuffers in the environment
		environment.active_framebuffers.append(self)

	# Decorator
	def to_texture(drawing_function):
		@wraps(drawing_function)
		def wrapped(inst, *args, **kwargs):
			if sdl2.SDL_SetRenderTarget(inst.sdl_renderer, inst.surface.texture) != 0:
				raise Exception("Could not set FrameBuffers texture as rendering"
					" target: {}".format(sdl2.SDL_GetError()))
			# Perform the drawing operation
			result = drawing_function(inst, *args, **kwargs)
			# Unset the texture as render target
			if sdl2.SDL_SetRenderTarget(inst.sdl_renderer, None) != 0:
				raise Exception("Could not unset FrameBuffers texture as rendering"
					" target: {}".format(sdl2.SDL_GetError()))
			return result
		return wrapped

	def opacity(self, value):
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

	def determine_optimal_colorkey(self, drawing_color, dev_offset=5):
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

		# If foreground and background colors are not identical, simply return
		# the background color
		if drawing_color != self.background_color:
			return self.background_color

		if not 1 <= dev_offset <= 25:
			raise ValueError("dev_offset should be a value between 1 and 25")

		# Create offset_color
		offset_color = sdl2.ext.Color(dev_offset, dev_offset, dev_offset, 0)
		# Create white_color
		white = sdl2.ext.Color(255,255,255,255)

		color_key = self.background_color + offset_color
		if color_key != white:
			return color_key
		else:
			return self.background_color - offset_color

	@to_texture
	def clear(self, color=None):
		if color is None:
			color = self.background_color
		color = sdl2.ext.convert_to_color(color)
		self.renderer.clear(color)
		return self

	@to_texture
	def draw_circle(self, x, y, r, color, opacity=1.0, fill=True, aa=False, penwidth=1):
		# Make sure all spatial parameters are ints
		x, y, r = int(x), int(y), int(r)

		# convert color parameter to sdl2 understandable values
		color = sdl2.ext.convert_to_color(color)
		# convert possible opacity values to the right scale
		opacity = self.opacity(opacity)

		# Check for invalid penwidth values, and make sure the value is an int
		if penwidth != 1:
			if penwidth < 1:
				raise ValueError("Penwidth cannot be smaller than 1")
			if penwidth > 1:
				penwidth = int(penwidth)

		# if only a filled circle needs to be drawn, it's easy
		if fill:
			sdlgfx.filledCircleRGBA(self.sdl_renderer, x, y, r, color.r, color.g, color.b, opacity)
		else:
			# If penwidth is 1, simply use sdl2gfx's own functions
			if penwidth == 1:
				if aa:
			 		sdlgfx.aacircleRGBA(self.sdl_renderer, x, y, r, color.r, color.g, color.b, opacity)
				else:
					sdlgfx.circleRGBA(self.sdl_renderer, x, y, r, color.r, color.g, color.b, opacity)
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
					size=(c_width, c_height),
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

				# Set the desired transparency value to the texture
				sdl2.SDL_SetTextureAlphaMod(circle_texture.texture, opacity)

				# Perform the blitting operation
				self.renderer.copy( circle_texture, dstrect=(x-int(c_width/2),
					y-int(c_height/2), c_width, c_height) )

				# Cleanup
				del(circle_sprite)
				del(sprite_renderer)
			
		return self

	@to_texture
	def draw_ellipse(self, x, y, rx, ry, color, opacity=1.0, fill=True, aa=False, 
		penwidth=1, rotation=0, center=True):
		# Make sure all spatial parameters are ints
		x, y, rx, ry = int(x), int(y), int(rx), int(ry)

		width, height = 2*(rx+penwidth)+1, 2*(ry+penwidth)+1

		if not center:
			x, y = int(x - width/2), int(y - height/2)

		color = sdl2.ext.COLOR(color)
		opacity = self.opacity(opacity)

		if penwidth != 1:
			if penwidth < 1:
				raise ValueError("Penwidth cannot be smaller than 1")
			if penwidth > 1:
				penwidth = int(penwidth)
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

	@to_texture
	def draw_rect(self, x, y, w, h, color, opacity=1.0, fill=True, border_radius=0, penwidth=1):
		# Make sure all spatial parameters are ints
		x = int(x)
		y = int(y)
		w = int(w)
		h = int(h)

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


	@to_texture
	def draw_line(self, x1, y1, x2, y2, color, opacity=1.0, aa=False, width=1):
		# Make sure all spatial parameters are ints
		x1 = int(x1)
		y1 = int(y1)
		x2 = int(x2)
		y2 = int(y2)

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

	@to_texture
	def draw_text(self, x, y, text, color, opacity=1.0):
		# Make sure all spatial parameters are ints
		x,y = int(x), int(y)

		# Make sure the passed text is of type 'bytes'
		text = sdl2.ext.compat.byteify(text, 'utf8')
		print(text)

		color = sdl2.ext.convert_to_color(color)
		sdl2.sdlgfx.stringRGBA(self.sdl_renderer, x, y, text, color.r, color.g, color.b, self.opacity(opacity))
		return self

	@to_texture
	def draw_arc(self, x, y, r, start, end, color, opacity=1.0, penwidth=1):
		# Make sure all spatial parameters are ints
		x = int(x)
		y = int(y)
		r = int(r)

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

	@to_texture
	def draw_pie(self, x, y, r, start, end, color, opacity=1.0, fill=True):
		# Make sure all spatial parameters are ints
		x = int(x)
		y = int(y)
		r = int(r)

		color = sdl2.ext.convert_to_color(color)
		if fill:
			return sdl2.sdlgfx.filledPieRGBA(self.sdl_renderer, x, y, r, start, end, color.r, color.g, color.b, int(opacity*255))
		else:
			return sdl2.sdlgfx.pieRGBA(self.sdl_renderer, x, y, r, start, end, color.r, color.g, color.b, int(opacity*255))
		return self

	@to_texture
	def draw_trigon(self, x1, y1, x2, y2, x3, y3, color, opacity=1.0, fill=True, aa=False):
		# Make sure all spatial parameters are ints
		x1 = int(x1)
		y1 = int(y1)
		x2 = int(x2)
		y2 = int(y2)
		x3 = int(x3)
		y3 = int(y3)

		color = sdl2.ext.convert_to_color(color)
		if fill:
			return sdl2.sdlgfx.filledTrigonRGBA(self.sdl_renderer, x1, y1, x2, y2, x3, y3, color.r, color.g, color.b, int(opacity*255))
		elif aa:
			return sdl2.sdlgfx.aatrigonRGBA(self.sdl_renderer, x1, y1, x2, y2, x3, y3, color.r, color.g, color.b, int(opacity*255))
		else:
			return sdl2.sdlgfx.trigonRGBA(self.sdl_renderer, x1, y1, x2, y2, x3, y3, color.r, color.g, color.b, int(opacity*255))
		return self

	@to_texture
	def draw_polygon(self, vx, vy, color, opacity=1.0, fill=True, aa=False, texture=None):
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

	@to_texture
	def draw_bezier_curve(self, vx, vy, s, color, opacity=1.0):
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

	@to_texture
	def draw_image(self, x, y, image_path):
		x = int(x)
		y = int(y)

		image = self.environment.texture_factory.from_image(image_path)
		image.position = (x,y)
		self.spriterenderer.render(image)
		return self

	def show(self):
		t1 = sdl2.SDL_GetTicks()
		self.renderer.clear(0)
		self.renderer.copy(self.surface)
		self.renderer.present()
		drawing_delay = sdl2.SDL_GetTicks() - t1
		return (time.time(), drawing_delay)

	def __del__(self):
		sdl2.SDL_DestroyTexture(self.surface.texture)
		del([self.renderer, self.surface, self.sdl_renderer, self.spriterenderer])
		# Remove this buffer from lists of active buffers in environment!

