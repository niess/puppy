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

from panda3d.core import *

def connect(object, indices, offset=0):
    """Connect the vertices of a GeomPrimitive
    """
    for index in indices:
        object.addVertex(index + offset)
    object.closePrimitive()

class Builder:

    def __init__(self):
        self.node = None
        self.path = None

    def render(self):
        """Render the GeomNode.

        Return: a NodePath to the rendered object.
        """
        if self.node is None:
            raise ValueError("empty GeomNode")
        if self.path is None:
            self.path = render.attachNewNode(self.node)
        return self.path

    def frame(self):
        """Return the local frame of the rendered object.
        """
        if self.path is not None:
            M = self.path.getMat()
            origin = M.xformPoint(self.origin)
            basis = tuple([M.xformVec(v) for v in self.basis])
        else:
            origin, basis = self.origin, self.basis
        return origin, basis

    def coordinates(self, point):
        """Return the local coordinates of the given point.
        """
        origin, basis = self.frame()
        c = []
        for b in basis:
            c.append(sum((point[i] - origin[i]) * b[i]))
        return tuple(b)

class Box(Builder):
    """3D box builder from Panda primitives.
    """
    def __init__(self, dx, dy, dz, name="box", face_color=(1,1,1,1),
      line_color=(0,0,0,1), texture_scale=None):
        Builder.__init__(self)

        self.origin = (-0.5 * dx, -0.5 * dy, -0.5 * dz)
        self.basis = ((1. / dx, 0., 0.), (0., 1. / dy, 0.), (0., 0., 1. / dz))

        if face_color is not None:
            # Build the data vector for the faces.
            format = GeomVertexFormat.getV3c4t2()
            data = GeomVertexData("vertices", format, Geom.UHStatic)
            data.setNumRows(24)
            writer = GeomVertexWriter(data, "vertex")
            for axis in ((0, 1, 2), (1, 2, 0), (2, 0, 1)):
                for c in ((0, 0, 0), (0, 1, 0), (1, 1, 0), (1, 0, 0)):
                    writer.addData3f((c[axis[0]] - 0.5) * dx,
                                     (c[axis[1]] - 0.5) * dy,
                                     (c[axis[2]] - 0.5) * dz)
                for c in ((0, 0, 1), (1, 0, 1), (1, 1, 1), (0, 1, 1)):
                    writer.addData3f((c[axis[0]] - 0.5) * dx,
                                     (c[axis[1]] - 0.5) * dy,
                                     (c[axis[2]] - 0.5) * dz)
            writer = GeomVertexWriter(data, "color")
            n = len(face_color)
            if n == 4:
                for _ in xrange(24): writer.addData4f(face_color)
            elif n == 6:
                for i in xrange(6):
                    for _ in xrange(4): writer.addData4f(face_color[i])
            else:
                raise ValueError("Invalid face color")
            writer = GeomVertexWriter(data, "texcoord")
            dmax = max(dx, dy, dz)
            for i, (dc0, dc1) in enumerate(((dx,dy), (dy,dx), (dz,dx), (dx,dz),
              (dy,dz), (dz,dy))):
                if texture_scale is None:
                    r0 = dc0 / dmax
                    r1 = dc1 / dmax
                else:
                    r0, r1 = texture_scale[i]
                writer.addData2f(0, 0)
                writer.addData2f(0, r1)
                writer.addData2f(r0, r1)
                writer.addData2f(r0, 0)

            # Build the triangles.
            triangles = GeomTriangles(Geom.UHStatic)
            for i in xrange(6):
                connect(triangles, (4 * i + 1, 4 * i + 2, 4 * i))
                connect(triangles, (4 * i + 2, 4 * i + 3, 4 * i))

            # Build the Geom for the faces and initialise the node.
            self.faces = Geom(data)
            self.faces.addPrimitive(triangles)
            if self.node is None: self.node = GeomNode(name)
            self.node.addGeom(self.faces)

        if line_color is not None:
            # Build the data vector for the border lines.
            format = GeomVertexFormat.getV3c4()
            data = GeomVertexData("vertices", format, Geom.UHStatic)
            data.setNumRows(8)
            writer = GeomVertexWriter(data, "vertex")
            for i in xrange(2):
                for j in xrange(2):
                    for k in xrange(2):
                        writer.addData3f(
                          (i - 0.5) * dx, (j - 0.5) * dy, (k - 0.5) * dz)
            writer = GeomVertexWriter(data, "color")
            for _ in xrange(8): writer.addData4f(line_color)

            # Build the border lines.
            lines = GeomLines(Geom.UHStatic)
            connect(lines, (0,1))
            connect(lines, (0,2))
            connect(lines, (0,4))
            connect(lines, (3,1))
            connect(lines, (3,2))
            connect(lines, (3,7))
            connect(lines, (5,1))
            connect(lines, (5,4))
            connect(lines, (5,7))
            connect(lines, (6,2))
            connect(lines, (6,4))
            connect(lines, (6,7))

            # Build the Geom for the borders and add it to the node.
            self.lines = Geom(data)
            self.lines.addPrimitive(lines)
            if self.node is None: self.node = GeomNode(name)
            self.node.addGeom(self.lines)

class TriangularTube(Builder):
    """Builder for a tube with a triangular section.
    """
    def __init__(self, section, length, name="triangular-tube",
      face_color=(1,1,1,1), line_color=(0,0,0,1), texture_scale=None):
        Builder.__init__(self)

        # check the orientation of the triangular section.
        u1 = (section[1][0] - section[0][0], section[1][1] - section[0][1])
        u2 = (section[2][0] - section[0][0], section[2][1] - section[0][1])
        c = u1[0] * u2[1] - u1[1] * u2[0]
        if c > 0: section = (section[0], section[2], section[1])

        self.origin = (section[2][0], section[2][1], 0.)
        d = (section[1][1] - section[2][1]) * (section[0][0] - section[2][0])
        d += (section[2][0] - section[1][0]) * (section[0][1] - section[2][1])
        self.basis = (((section[1][1] - section[2][1]) / d,
          (section[2][0] - section[1][0]) / d, 0.),
          ((section[2][1] - section[0][1]) / d,
          (section[0][0] - section[2][0]) / d, 0.), (0., 0., 1. / length))

        if face_color is not None:
            # Build the data vector for the faces.
            format = GeomVertexFormat.getV3c4t2()
            data = GeomVertexData("vertices", format, Geom.UHStatic)
            data.setNumRows(18)
            writer = GeomVertexWriter(data, "vertex")
            for x, y in section: writer.addData3f(x,y,0)
            for x, y in section: writer.addData3f(x,y,length)
            for indices in ((0,1), (1,2), (2,0)):
                for index in indices:
                    writer.addData3f(section[index][0],section[index][1],0)
                for index in indices[::-1]:
                    writer.addData3f(section[index][0],section[index][1],length)
            writer = GeomVertexWriter(data, "color")
            n = len(face_color)
            if n == 4:
                for _ in xrange(18): writer.addData4f(face_color)
            elif n == 5:
                for _ in xrange(3): writer.addData4f(face_color[0])
                for _ in xrange(3): writer.addData4f(face_color[1])
                for i in xrange(2,5):
                    for _ in xrange(4): writer.addData4f(face_color[i])
            else:
                raise ValueError("Invalid face color")
            writer = GeomVertexWriter(data, "texcoord")
            if texture_scale is None:
                xmax = max(v[0] for v in section)
                xmin = min(v[0] for v in section)
                dx = xmax - xmin
                ymax = max(v[1] for v in section)
                ymin = min(v[1] for v in section)
                dy = ymax - ymin
                dmax = max(dx, dy, length)
                r0 = dx / dmax
                r1 = dy / dmax
                for _ in xrange(2):
                    for (x,y) in section:
                        writer.addData2f((x - xmin) / dmax, (y - ymin) / dmax)
                for index in ((0,1), (1,2), (2,0)):
                    d = ((section[index[0]][0] - section[index[1]][0])**2 +
                         (section[index[0]][1] - section[index[1]][1])**2)**0.5
                    writer.addData2f(0., 0.)
                    writer.addData2f(d / dmax, 0.)
                    writer.addData2f(d / dmax, length / dmax)
                    writer.addData2f(0., length / dmax)
            else:
                for i in xrange(5):
                    r0, r1 = texture_scale[0]
                    writer.addData2f(0., 0.)
                    writer.addData2f(r0, 0.)
                    writer.addData2f(r0, r1)
                    writer.addData2f(0., r1)

            # Build the triangles.
            triangles = GeomTriangles(Geom.UHStatic)
            connect(triangles, (0, 1, 2))
            connect(triangles, (0, 2, 1), 3)
            for i in xrange(0,3):
                connect(triangles, (4 * i + 2, 4 * i + 1, 4 * i), 6)
                connect(triangles, (4 * i + 3, 4 * i + 2, 4 * i), 6)

            # Build the Geom for the faces and initialise the node.
            self.faces = Geom(data)
            self.faces.addPrimitive(triangles)
            if self.node is None: self.node = GeomNode(name)
            self.node.addGeom(self.faces)

        if line_color is not None:
            # Build the data vector for the border lines.
            format = GeomVertexFormat.getV3c4()
            data = GeomVertexData("vertices", format, Geom.UHStatic)
            data.setNumRows(18)
            writer = GeomVertexWriter(data, "vertex")
            for x, y in section: writer.addData3f(x,y,0)
            for x, y in section: writer.addData3f(x,y,length)
            for indices in ((0,1), (1,2), (2,0)):
                for index in indices:
                    writer.addData3f(section[index][0],section[index][1],0)
                for index in indices[::-1]:
                    writer.addData3f(section[index][0],section[index][1],length)
            writer = GeomVertexWriter(data, "color")
            for _ in xrange(18): writer.addData4f(line_color)

            # Build the border lines.
            lines = GeomLines(Geom.UHStatic)
            connect(lines, (0,1))
            connect(lines, (0,2))
            connect(lines, (1,2))
            connect(lines, (3,4))
            connect(lines, (3,5))
            connect(lines, (4,5))
            connect(lines, (0,3))
            connect(lines, (1,4))
            connect(lines, (2,5))

            # Build the Geom for the borders and add it to the node.
            self.lines = Geom(data)
            self.lines.addPrimitive(lines)
            if self.node is None: self.node = GeomNode(name)
            self.node.addGeom(self.lines)

class Map(Builder):
    """3D map builder from Panda primitives.
    """
    def __init__(self, x, y, z, face_color=(1,1,1,1), line_color=(0,0,0,1),
      texture=None, name="map"):
        Builder.__init__(self)
        nx, ny = len(x), len(y)
        n = nx * ny

        if face_color is not None:
            # Build the data vector for the faces.
            format = GeomVertexFormat.getV3c4t2()
            data = GeomVertexData("vertices", format, Geom.UHStatic)
            data.setNumRows(n)
            writer = GeomVertexWriter(data, "vertex")
            for i, yi in enumerate(y):
                for j, xj in enumerate(x):
                    writer.addData3f(xj, yi, z[i,j])
            writer = GeomVertexWriter(data, "color")
            try:
                if len(face_color[0]) != nx:
                    raise ValueError("Invalid face colors")
            except TypeError:
                for _ in xrange(n): writer.addData4f(face_color)
            else:
                for i in xrange(ny):
                    for j in xrange(nx):
                        writer.addData4f(face_color[i][j])
            writer = GeomVertexWriter(data, "texcoord")
            for i in xrange(ny):
                for j in xrange(nx):
                    writer.addData2f(j, i)

            # Build the triangles.
            triangles = GeomTriangles(Geom.UHStatic)
            for i in xrange(ny - 1):
                for j in xrange(nx - 1):
                    d1 = abs(z[i][j] - z[i + 1][j + 1])
                    d2 = abs(z[i + 1][j] - z[i][j + 1])
                    if d1 < d2:
                        connect(triangles,
                          (i * nx + j, i * nx + j + 1, (i + 1) * nx + j + 1))
                        connect(triangles,
                          ((i + 1) * nx + j, i * nx + j, (i + 1) * nx + j + 1))
                    else:
                        connect(triangles,
                          (i * nx + j, i * nx + j + 1, (i + 1) * nx + j))
                        connect(triangles,
                          ((i + 1) * nx + j + 1, (i + 1) * nx + j,
                          i * nx + j + 1))

            # Build the Geom for the faces and initialise the node.
            self.faces = Geom(data)
            self.faces.addPrimitive(triangles)
            if self.node is None: self.node = GeomNode(name)
            self.node.addGeom(self.faces)

        if line_color is not None:
            # Build the data vector for the lines.
            format = GeomVertexFormat.getV3c4()
            data = GeomVertexData("vertices", format, Geom.UHStatic)
            data.setNumRows(n)
            writer = GeomVertexWriter(data, "vertex")
            for i, yi in enumerate(y):
                for j, xj in enumerate(x):
                    writer.addData3f(xj, yi, z[i,j])
            writer = GeomVertexWriter(data, "color")
            for _ in xrange(n): writer.addData4f(line_color)

            # Build the lines.
            lines = GeomLines(Geom.UHStatic)
            for i in xrange(ny):
                for j in xrange(nx - 1):
                    connect(lines, (j,j + 1), i * nx)
            for j in xrange(nx):
                for i in xrange(ny - 1):
                    connect(lines, (i * nx,(i + 1) * nx), j)

            # Build the Geom for lines and add it to the node.
            self.lines = Geom(data)
            self.lines.addPrimitive(lines)
            if self.node is None: self.node = GeomNode(name)
            self.node.addGeom(self.lines)
