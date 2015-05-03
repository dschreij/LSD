# -*- coding: utf-8 -*-
"""
Created on Sun May  3 21:55:19 2015

@author: daniel
"""

import LSD
import sdl2.ext
from LSD.drawing import FrameBuffer
from random import randint

c = LSD.create_window((800,600))
fb = FrameBuffer(c)
fb2 = FrameBuffer(c)
fb3 = FrameBuffer(c)
fb4 = FrameBuffer(c)
fb5 = FrameBuffer(c)

for i in range(0,10):
	fb.draw_circle(randint(50,750), randint(50,550), 40, color=randint(0, 0xFFFFFFFF))
	fb2.draw_rect(randint(50,750), randint(50,550), randint(10,100), randint(10,100), (255,0,0,255), 0, 0)
	fb3.draw_rect(randint(50,750), randint(50,550), randint(10,100), randint(10,100), (255,255,0,255), 15, 1)
	fb4.draw_rect(randint(50,750), randint(50,550), randint(10,100), randint(10,100), (255,0,255,255), 15, 0)
	fb5.draw_rect(randint(50,750), randint(50,550), randint(10,100), randint(10,100), (0,255,255,255), 0, 1)

fb.show()
sdl2.SDL_Delay(3000)
events = sdl2.ext.get_events()
fb2.show()
sdl2.SDL_Delay(3000)
events = sdl2.ext.get_events()
fb3.show()
sdl2.SDL_Delay(3000)
events = sdl2.ext.get_events()
fb4.show()
sdl2.SDL_Delay(3000)
events = sdl2.ext.get_events()
fb5.show()

processor = sdl2.ext.TestEventProcessor()
processor.run(c.window)

del([fb,fb2])
sdl2.ext.quit()