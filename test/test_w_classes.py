# -*- coding: utf-8 -*-
"""
Created on Sun May  3 21:55:19 2015

@author: daniel
"""
# Make sure LSD from parent folder is imported
import sys, os
sys.path.insert(0,os.path.join(os.path.dirname(__file__), '..'))

import LSD
import sdl2.ext
from LSD.drawing import FrameBuffer
from random import randint

c = LSD.create_window((800,600))

print(c)

fb = FrameBuffer(c)
fb2 = FrameBuffer(c)
fb3 = FrameBuffer(c)
fb4 = FrameBuffer(c)
fb5 = FrameBuffer(c, background_color="#999999")
fb6 = FrameBuffer(c)

for i in range(0,250):
	fb.draw_circle(randint(0,750), randint(0,550), 40, color=randint(0, 0xFFFFFFFF),fill=False, aa=True)
	fb2.draw_rect(randint(0,750), randint(0,550), randint(10,100), randint(10,100), (255,0,0), opacity=randint(5,10)/10.0, fill=False)
	fb3.draw_rect(randint(0,750), randint(0,550), randint(10,100), randint(10,100), (0,255,0), opacity=randint(5,10)/10.0, border_radius=5, fill=True)
	fb4.draw_rect(randint(0,750), randint(0,550), randint(10,100), randint(10,100), (0,0,255), opacity=randint(5,10)/10.0, border_radius=5, fill=False)
	fb5.draw_rect(randint(0,750), randint(0,550), randint(10,100), randint(10,100), "#09ceff", opacity=randint(5,10)/10.0, fill=True)
	fb6.draw_circle(randint(0,750), randint(0,550), 40, color=(0,0,255,255), opacity=randint(5,10)/10.0 )

fb.show()
c.window.refresh()
sdl2.SDL_Delay(2000)
events = sdl2.ext.get_events()
fb2.show()
sdl2.SDL_Delay(2000)
events = sdl2.ext.get_events()
fb3.show()
sdl2.SDL_Delay(2000)
events = sdl2.ext.get_events()
fb4.show()
sdl2.SDL_Delay(2000)
events = sdl2.ext.get_events()
fb5.show()
sdl2.SDL_Delay(2000)
events = sdl2.ext.get_events()
fb6.show()
sdl2.SDL_Delay(2000)
events = sdl2.ext.get_events()
fb.show()
c.window.refresh()

processor = sdl2.ext.TestEventProcessor()
processor.run(c.window)

sdl2.ext.quit()