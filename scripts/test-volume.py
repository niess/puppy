#!/usr/bin/env python
import puppy.build
import puppy.control

class Test(puppy.control.KeyboardCamera):
    def __init__(self):
        puppy.control.KeyboardCamera.__init__(self)

        # Grab some default texture.
        texture = loader.loadTexture("maps/envir-reeds.png")

        # Create a box.
        self.box = puppy.build.Box(1., 1., 1.).render()
        self.box.setTexture(texture)
        self.box.setPos(0., 0., 2.)

        # Create a tube with a triangular section.
        section = ((0., 0.), (0., 1.), (1., 0.))
        self.tube = puppy.build.TriangularTube(section, 1.).render()
        self.tube.setTexture(texture)
        self.tube.setPos(0., 0., -2.)

        # Create a parallelepiped.
        section = ((0., 0.), (0., 1.), (1., 0.5))
        self.parallelepiped = puppy.build.Parallelepiped(section, 1.).render()
        self.parallelepiped.setTexture(texture)
        self.parallelepiped.setPos(0., -2., 0.)

        # Initialise the camera.
        self.camera.setPos(8., 8., 8.)
        self.camera.lookAt(self.parallelepiped)

Test().run()
