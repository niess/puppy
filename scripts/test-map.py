#!/usr/bin/env python
from direct.showbase.ShowBase import ShowBase
from primitive import Box, Map
import numpy

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        # Create a map.
        x = numpy.linspace(-10., 10., 21)
        y = numpy.linspace(-10., 10., 21)
        z = numpy.outer(y, x)
        self.map = Map(x, y, z).render()
        texture = loader.loadTexture("maps/envir-ground.jpg")
        self.map.setTexture(texture)

        # Add a box.
        self.box = Box(1., 1., 1.).render()
        texture = loader.loadTexture("maps/envir-reeds.png")
        self.box.setTexture(texture)
        self.box.setPos(0., 0., 10.)

app = MyApp()
app.run()
