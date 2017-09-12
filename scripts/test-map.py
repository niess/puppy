#!/usr/bin/env python
import numpy
import puppy.build
import puppy.control

class Test(puppy.control.KeyboardCamera):
    def __init__(self):
        puppy.control.KeyboardCamera.__init__(self)

        # Create a map.
        x = numpy.linspace(-10., 10., 21)
        y = numpy.linspace(-10., 10., 21)
        z = numpy.outer(y, x)
        self.map = puppy.build.Map(x, y, z).render()
        texture = loader.loadTexture("maps/envir-ground.jpg")
        self.map.setTexture(texture)

        # Add a box.
        self.box = puppy.build.Box(1., 1., 1.).render()
        texture = loader.loadTexture("maps/envir-reeds.png")
        self.box.setTexture(texture)
        self.box.setPos(0., 0., 10.)

        # Initialise the camera.
        self.camera.setPos(20., -20., 15.)
        self.camera.lookAt(self.box)

Test().run()
