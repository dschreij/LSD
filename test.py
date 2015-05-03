# -*- coding: utf-8 -*-
"""
Created on Sun May  3 16:00:39 2015

@author: daniel
"""

#import LSD
#from LSD.drawing import FrameBuffer

import sdl2
import sdl2.ext
import sdl2.sdlgfx

from random import randint

sdl2.ext.init()

# Create a window with the specified resolution
resolution = (800,600)
window = sdl2.ext.Window("test", size=resolution)
window.show()

# Create a render system that renders to the window surface		
renderer = sdl2.ext.Renderer(window)
# Clear with black color
renderer.clear(0)
# Create sprite factory to create surfaces with later
factory = sdl2.ext.SpriteFactory(renderer=renderer)
surface = factory.create_sprite(size=resolution, access=sdl2.SDL_TEXTUREACCESS_TARGET)

print sdl2.SDL_SetRenderTarget(renderer.renderer, surface.texture)
renderer.clear(0)
sdl2.sdlgfx.thickLineColor(renderer.renderer, 10, 10, 40, 50, 3, 0xFFFFFFFF)
color = randint(0, 0xFFFFFFFF)
sdl2.sdlgfx.aalineColor(renderer.renderer, 100, 50, 400, 80, color)
sdl2.sdlgfx.lineColor(renderer.renderer, 100, 60, 400, 90, color)
print sdl2.SDL_SetRenderTarget(renderer.renderer, None)

renderer.copy(surface)
renderer.present()


processor = sdl2.ext.TestEventProcessor()
processor.run(window)

sdl2.ext.quit()