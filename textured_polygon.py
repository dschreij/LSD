# -*- coding: utf-8 -*-
"""
Created on Sun May 10 17:36:36 2015

@author: daniel
"""

# Initialize SDL2 and window
import sdl2
import sdl2.ext
import sdl2.sdlgfx
import ctypes
sdl2.ext.init()
window = sdl2.ext.Window("Probleem", size=(800,600))
window.show()

# Create renderer and factories
renderer = sdl2.ext.Renderer(window)
renderer.clear(0)
renderer.present()
# Create sprite factory to create textures with later
texture_factory = sdl2.ext.SpriteFactory(renderer=renderer)
# Create sprite factory to create surfaces with later
surface_factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)

# Determine path to image to use as texture
RESOURCES = sdl2.ext.Resources(__file__, "LSD/resources")
image_path = RESOURCES.get_path("Memory.jpeg")

# set polygon coordinates
x = 100
row4 = 270
vx = [x, x+200, x+200, x]
vy = [row4-100, row4-100, row4+100, row4+100]

# Calculate the length of the vectors (which should be the same for x and y)
n = len(vx) 
# Make sure all coordinates are integers
vx = map(int,vx)
vy = map(int,vy)
# Cast the list to the appropriate ctypes vectors reabable by
# the sdlgfx polygon functions
vx = ctypes.cast((sdl2.Sint16*n)(*vx), ctypes.POINTER(sdl2.Sint16))
vy = ctypes.cast((sdl2.Sint16*n)(*vy), ctypes.POINTER(sdl2.Sint16))

# Load the image on an SoftwareSprite
# The underlying surface is available at SoftwareSprite.surface
texture = surface_factory.from_image(image_path)

## RENDER THE POLYGON WITH TEXTURE
sdl2.sdlgfx.texturedPolygon(renderer.renderer, vx, vy, n, texture.surface, 150, 50)

# Swap buffers
renderer.present()

# Handle window close events
processor = sdl2.ext.TestEventProcessor()
processor.run(window)

sdl2.ext.quit()