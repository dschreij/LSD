# -*- coding: utf-8 -*-
"""
Created on Wed May  6 22:52:13 2015

@author: daniel
"""

import LSD
import sdl2.ext
from LSD.drawing import FrameBuffer
from random import randint

c = LSD.create_window((800,600))

print c

fb = FrameBuffer(c, background_color="#222222")

row1 = 50
row2 = 150
row3 = 320

# Circle
fb.draw_circle(50, row1, 40, color=randint(0, 0xFFFFFFFF), fill=False, aa=False)
# Anti aliased circle
fb.draw_circle(150, row1, 40, color=randint(0, 0xFFFFFFFF), fill=False, aa=True)
# Filled circle
fb.draw_circle(250, row1, 40, color=randint(0, 0xFFFFFFFF), fill=True, aa=True)

# Ellipse
fb.draw_ellipse(400, row1, 60, 40, color=randint(0, 0xFFFFFFFF), fill=False, aa=False)
# Anti aliased ellipse
fb.draw_ellipse(550, row1, 60, 40, color=randint(0, 0xFFFFFFFF), fill=False, aa=True)
# Filled ellipse
fb.draw_ellipse(700, row1, 60, 40, color=randint(0, 0xFFFFFFFF), fill=True, aa=False)

# Rect
fb.draw_rect(50, row2, 80, 80, color=randint(0, 0xFFFFFFFF), fill=False)
# Filled rect
fb.draw_rect(150, row2, 80, 80, color=randint(0, 0xFFFFFFFF), fill=True)

# Line
fb.draw_line(300, row2+10, 380, row2+70, color=randint(0, 0xFFFFFFFF), aa=False, width=1)
# anti aliased Line
fb.draw_line(400, row2+10, 480, row2+70, color=randint(0, 0xFFFFFFFF), aa=True, width=1)
# Thick line
fb.draw_line(500, row2+10, 580, row2+70, color=randint(0, 0xFFFFFFFF), aa=True, width=5)

# Text
fb.draw_text(600, row2, "Test 1 2 3", color=randint(0, 0xFFFFFFFF) )

# Arc
start = randint(0,90)
end = randint(180,270)
fb.draw_arc(50, row3, 40, start, end, color=randint(0, 0xFFFFFFFF))

# Pie
start = randint(0,90)
end = randint(270,320)
fb.draw_pie(150, row3, 40, start, end, color=randint(0, 0xFFFFFFFF), fill=False)

# Filled pie
start = randint(0,90)
end = randint(180,320)
fb.draw_pie(250, row3, 40, start, end, color=randint(0, 0xFFFFFFFF))

# Trigon
x = 400
row3 -= 40
fb.draw_trigon(x, row3, x+80, row3, x+40, row3+80, color=randint(0, 0xFFFFFFFF), fill=False, aa=False)
# AA Trigon
x += 100
fb.draw_trigon(x, row3+80, x+80, row3+80, x+40, row3, color=randint(0, 0xFFFFFFFF), fill=False, aa=True)
# Filled trigon
x += 100
fb.draw_trigon(x, row3, x+80, row3, x+40, row3+80, color=randint(0, 0xFFFFFFFF), fill=True, aa=False)

fb.show()

processor = sdl2.ext.TestEventProcessor()
processor.run(c.window)

sdl2.ext.quit()