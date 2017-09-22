# -*- coding: utf-8 -*-
#
#  Copyright (C) 2017 Université Clermont Auvergne, CNRS/IN2P3, LPC
#  Author: Valentin NIESS (niess@in2p3.fr)
#
#  This software is a Python library whose purpose is to provide procedural
#  builders for the Panda3D engine.
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import sys
# Panda3D modules.
from direct.showbase.ShowBase import ShowBase
from panda3d.core import MouseButton

class KeyboardCamera(ShowBase):
    """Implement a keyboard controlled camera (US:wsad+mouse view rotation).
    """
    def __init__(self):
        ShowBase.__init__(self)

        # Initialise the keyboard task.
        self.disableMouse()
        self.mouse_anchor = None
        self.accept("escape", sys.exit)
        m = self.win.getKeyboardMap()
        self.key = {
              "forward" : m.getMappedButton("w"),
              "backward" : m.getMappedButton("s"),
              "left" : m.getMappedButton("a"),
              "right" : m.getMappedButton("d"),
              "mouse1" : MouseButton.one(),
              "mouse3" : MouseButton.three() }
        self.taskMgr.add(self.move, "moveTask")
        self.reset_acceleration()

    def reset_acceleration(self):
        self.acceleration = [8., 5.]

    def move(self, task):
        # 1st let us check the keys state.
        speed = [0., 0.]
        is_down = self.mouseWatcherNode.isButtonDown

        moving = True
        if is_down(self.key["forward"]):
            speed[0] += self.acceleration[0]
        elif is_down(self.key["backward"]):
            speed[0] -= self.acceleration[0]
        else:
            moving = False
        if is_down(self.key["left"]):
            speed[1] -= self.acceleration[1]
        elif is_down(self.key["right"]):
            speed[1] += self.acceleration[1]
        else:
            moving = moving or False

        if is_down(self.key["mouse3"]) and moving:
            self.acceleration[0] += 1
            self.acceleration[1] += 1
        else:
            self.reset_acceleration()

        if is_down(self.key["mouse1"]):
            m = self.win.getPointer(0)
            p = m.getX(), m.getY()
            if self.mouse_anchor is None:
                self.mouse_anchor = (p, self.camera.getHpr())
            else:
                hpr = (
                  self.mouse_anchor[1][0] + 1E-01 *
                    (self.mouse_anchor[0][0] - p[0]),
                  self.mouse_anchor[1][1] + 1E-01 *
                    (self.mouse_anchor[0][1] - p[1]), 0)
                self.camera.setHpr(hpr)
        else:
            self.mouse_anchor = None

        # Then let us move the camera.
        dt = globalClock.get_dt()
        self.camera.setY(self.camera, speed[0] * dt)
        self.camera.setX(self.camera, speed[1] * dt)

        return task.cont
