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

def _connect(object, indices, offset=0):
    """connect the vertices of a GeomPrimitive
    """
    for index in indices:
        object.addVertex(index + offset)
    object.closePrimitive()

def multiply(s, v):
    """Multiply a vector with a scalar."""
    return (s * v[0], s * v[1], s * v[2])

def dot(i,j):
    """Dot product of 2 vectors."""
    return i[0] * j[0] + i[1] * j[1] + i[2] * j[2]

def cross(i,j):
    """Cross product of 2 vectors."""
    return ( i[2] * j[1] - i[1] * j[2], i[0] * j[2] - i[2] * j[0],
             i[1] * j[0] - i[0] * j[1] )

def det(i,j,k):
    """Triple product (determinant) of 3 vectors.
    """
    return dot(i, cross(j, k))

class Builder:
    """Base geometry builder from primitives.
    """
    def __init__(self):
        self.name = None
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
        """Return the reference frame of the rendered object.
        """
        if self.path is not None:
            M = self.path.getMat()
            origin = tuple(M.xformPoint(LVecBase3f(*self._origin)))
            basis = tuple([
              tuple(M.xformVec(LVecBase3f(*v))) for v in self._basis])
        else:
            origin, basis = self._origin, self._basis
        return origin, basis

    def barycentric_frame(self):
        """Return the barycentric frame of the rendered object.
        """
        origin, basis = self._barycentric
        if self.path is not None:
            M = self.path.getMat()
            origin = tuple(M.xformPoint(LVecBase3f(*origin)))
            basis = tuple([tuple(M.xformVec(LVecBase3f(*v))) for v in basis])
        return origin, basis

    def barycentric_coordinates(self, point):
        """Return the barycentric coordinates of the given point.
        """
        origin, basis = self._barycentric
        if self.path is not None:
            M = self.path.getMat()
            origin = tuple(M.xformPoint(LVecBase3f(*origin)))
            basis = tuple([tuple(M.xformVec(LVecBase3f(*v))) for v in basis])
        c = []
        u = [ point[i] - origin[i] for i in xrange(3) ]
        for b in basis: c.append(dot(u, b))
        return tuple(b)

class TriangularTube(Builder):
    """Builder for a tube with a triangular section.
    """
    def __init__(self, *args, **kwargs):
        Builder.__init__(self)

        # Unpack the arguments.
        frame, section, length = None, None, None
        opts = { "name" : "triangular-tube", "face_color" : (1,1,1,1),
          "line_color" : (0,0,0,1), "texture_scale" : None }
        for k, v in kwargs.items():
            if k not in opts: raise ValueError("unknown option {:}".format(k))
            opts[k] = v
        try:
            section, length = args
        except ValueError:
            frame = args[0]
        self.name = opts["name"]

        # Build the local frame if not provided.
        if frame is None:
            origin = (section[0][0], section[0][1], -0.5 * length)
            basis = (
              (section[1][0] - section[0][0],
                section[1][1] - section[0][1], 0.),
              (section[2][0] - section[0][0],
                section[2][1] - section[0][1], 0.),
              (0., 0., length))
            frame = (origin, basis)

        # Check the orientation of the frame.
        origin, (v0, v1, v2) = frame
        n = cross(v0, v1)
        n = multiply(1. / dot(n, n)**0.5, n)
        dz = dot(v2, n)
        if dz < 0.:
            v0, v1 = v1, v0
            multiply(-1., n)
            dz = -dz
            frame = (origin, (v0, v1, v2))

        # Set the local frame and the barycentric transform.
        self._origin, self._basis = frame
        dxy = det(v0, v1, n)
        self._barycentric = (origin,
          (multiply(1. / dxy, cross(v1, n)), multiply(-1. / dxy, cross(v0, n)),
           multiply(1. / dz, n)))

        # Build the section.
        section = (origin,
          [origin[i] + v0[i] for i in xrange(3)],
          [origin[i] + v1[i] for i in xrange(3)])

        if opts["face_color"] is not None:
            # Build the data vector for the faces.
            format = GeomVertexFormat.getV3c4t2()
            data = GeomVertexData("vertices", format, Geom.UHStatic)
            data.setNumRows(18)
            writer = GeomVertexWriter(data, "vertex")
            for x, y, z in section: writer.addData3f(x, y, z)
            for x, y, z in section: writer.addData3f(
              x + v2[0], y + v2[1], z + v2[2])
            for indices in ((0,1), (1,2), (2,0)):
                for index in indices:
                    writer.addData3f(section[index][0], section[index][1],
                      section[index][2])
                for index in indices[::-1]:
                    writer.addData3f(section[index][0] + v2[0],
                      section[index][1] + v2[1], section[index][2] + v2[2])
            writer = GeomVertexWriter(data, "color")
            n = len(opts["face_color"])
            if n == 4:
                for _ in xrange(18): writer.addData4f(opts["face_color"])
            elif n == 5:
                for _ in xrange(3): writer.addData4f(opts["face_color"][0])
                for _ in xrange(3): writer.addData4f(opts["face_color"][1])
                for i in xrange(2,5):
                    for _ in xrange(4): writer.addData4f(opts["face_color"][i])
            else:
                raise ValueError("Invalid face color")
            writer = GeomVertexWriter(data, "texcoord")
            if opts["texture_scale"] is None:
                L0 = (v0[0]**2 + v0[1]**2 + v0[2]**2)**0.5
                L12 = v1[0]**2 + v1[1]**2 + v1[2]**2
                x1 = (v0[0] * v1[0] + v0[1] * v1[1] + v0[2] * v1[2]) / L0
                y1 = (L12 - x1**2)**0.5
                for _ in xrange(2):
                    writer.addData2f(0., 0.)
                    writer.addData2f(L0, 0.)
                    writer.addData2f(x1, y1)
                for index in ((0,1), (1,2), (2,0)):
                    x0, y0, z0 = section[index[0]]
                    x1, y1, z1 = section[index[1]]
                    u0 = (x1 - x0, y1 - y0, z1 - z0)
                    L0 = (u0[0]**2 + u0[1]**2 + u0[2]**2)**0.5
                    L12 = v2[0]**2 + v2[1]**2 + v2[2]**2
                    x1 = (u0[0] * v2[0] + u0[1] * v2[1] + u0[2] * v2[2]) / L0
                    y1 = (L12 - x1**2)**0.5
                    writer.addData2f(0., 0.)
                    writer.addData2f(L0, 0.)
                    writer.addData2f(L0 + x1, y1)
                    writer.addData2f(x1, y1)
            else:
                for i in xrange(0,2):
                    w0, w1, w2 = opts["texture_scale"][i]
                    writer.addData2f(w0)
                    writer.addData2f(w1)
                    writer.addData2f(w2)
                for i in xrange(2,5):
                    r0, r1 = opts["texture_scale"][i]
                    writer.addData2f(0., 0.)
                    writer.addData2f(r0, 0.)
                    writer.addData2f(r0, r1)
                    writer.addData2f(0., r1)

            # Build the triangles.
            triangles = GeomTriangles(Geom.UHStatic)
            _connect(triangles, (0, 1, 2))
            _connect(triangles, (0, 2, 1), 3)
            for i in xrange(0,3):
                _connect(triangles, (4 * i + 2, 4 * i + 1, 4 * i), 6)
                _connect(triangles, (4 * i + 3, 4 * i + 2, 4 * i), 6)

            # Build the Geom for the faces and initialise the node.
            self.faces = Geom(data)
            self.faces.addPrimitive(triangles)
            if self.node is None: self.node = GeomNode(opts["name"])
            self.node.addGeom(self.faces)

        if opts["line_color"] is not None:
            # Build the data vector for the border lines.
            format = GeomVertexFormat.getV3c4()
            data = GeomVertexData("vertices", format, Geom.UHStatic)
            data.setNumRows(6)
            writer = GeomVertexWriter(data, "vertex")
            for x, y, z in section: writer.addData3f(x, y, z)
            for x, y, z in section: writer.addData3f(
              x + v2[0], y + v2[1], z + v2[2])
            writer = GeomVertexWriter(data, "color")
            for _ in xrange(6): writer.addData4f(opts["line_color"])

            # Build the border lines.
            lines = GeomLines(Geom.UHStatic)
            _connect(lines, (0,1))
            _connect(lines, (0,2))
            _connect(lines, (1,2))
            _connect(lines, (3,4))
            _connect(lines, (3,5))
            _connect(lines, (4,5))
            _connect(lines, (0,3))
            _connect(lines, (1,4))
            _connect(lines, (2,5))

            # Build the Geom for the borders and add it to the node.
            self.lines = Geom(data)
            self.lines.addPrimitive(lines)
            if self.node is None: self.node = GeomNode(opts["name"])
            self.node.addGeom(self.lines)

class Parallelepiped(Builder):
    """Builder for a parallelepiped volume.
    """
    def __init__(self, *args, **kwargs):
        Builder.__init__(self)

        # Unpack the arguments.
        frame, section, length = None, None, None
        opts = { "name" : "parallelepiped", "face_color" : (1,1,1,1),
          "line_color" : (0,0,0,1), "texture_scale" : None }
        for k, v in kwargs.items():
            if k not in opts: raise ValueError("unknown option {:}".format(k))
            opts[k] = v
        try:
            section, length = args
        except ValueError:
            frame = args[0]
        self.name = opts["name"]

        # Build the local frame, if needed.
        if frame is None:
            edge = tuple([ section[1][i] + section[2][i] - section[0][i]
              for i in xrange(2) ])
            section = (section[0], section[1], section[2], edge)
            origin = (section[0][0], section[0][1], -0.5 * length)
            basis = (
              (section[1][0] - section[0][0],
                section[1][1] - section[0][1], 0.),
              (section[2][0] - section[0][0],
                section[2][1] - section[0][1], 0.),
              (0., 0., length))
            frame = (origin, basis)

        # Check the orientation of the frame.
        origin, (v0, v1, v2) = frame
        n = cross(v0, v1)
        n = multiply(1. / dot(n, n)**0.5, n)
        dz = dot(v2, n)
        if dz < 0.:
            v0, v1 = v1, v0
            multiply(-1., n)
            dz = -dz
            frame = (origin, (v0, v1, v2))

        # Set the local frame and the barycentric transform.
        self._origin, self._basis = frame
        dxy = det(v0, v1, n)
        self._barycentric = (origin,
          (multiply(1. / dxy, cross(v1, n)), multiply(-1. / dxy, cross(v0, n)),
           multiply(1. / dz, n)))

        # Build the section.
        origin, (v0, v1, v2) = frame
        section = (origin,
          [origin[i] + v0[i] for i in xrange(3)],
          [origin[i] + v1[i] for i in xrange(3)],
          [origin[i] + v0[i] + v1[i] for i in xrange(3)])

        if opts["face_color"] is not None:
            # Build the data vector for the faces.
            format = GeomVertexFormat.getV3c4t2()
            data = GeomVertexData("vertices", format, Geom.UHStatic)
            data.setNumRows(24)
            writer = GeomVertexWriter(data, "vertex")
            for x, y, z in section: writer.addData3f(x, y, z)
            for x, y, z in section: writer.addData3f(
              x + v2[0], y + v2[1], z + v2[2])
            for indices in ((0,1), (2,0), (1,3), (3,2)):
                for index in indices:
                    writer.addData3f(section[index][0], section[index][1],
                      section[index][2])
                for index in indices[::-1]:
                    writer.addData3f(section[index][0] + v2[0],
                      section[index][1] + v2[1], section[index][2] + v2[2])
            writer = GeomVertexWriter(data, "color")
            n = len(opts["face_color"])
            if n == 4:
                for _ in xrange(24): writer.addData4f(opts["face_color"])
            elif n == 6:
                for i in xrange(6):
                    for _ in xrange(4): writer.addData4f(opts["face_color"][i])
            else:
                raise ValueError("Invalid face color")
            writer = GeomVertexWriter(data, "texcoord")
            if opts["texture_scale"] is None:
                L0 = (v0[0]**2 + v0[1]**2 + v0[2]**2)**0.5
                L12 = v1[0]**2 + v1[1]**2 + v1[2]**2
                x1 = (v0[0] * v1[0] + v0[1] * v1[1] + v0[2] * v1[2]) / L0
                y1 = (L12 - x1**2)**0.5
                for _ in xrange(2):
                    writer.addData2f(0., 0.)
                    writer.addData2f(L0, 0.)
                    writer.addData2f(x1, y1)
                    writer.addData2f(L0 + x1, y1)
                for index in ((0,1), (2,0), (1,3), (3,2)):
                    x0, y0, z0 = section[index[0]]
                    x1, y1, z1 = section[index[1]]
                    u0 = (x1 - x0, y1 - y0, z1 - z0)
                    L0 = (u0[0]**2 + u0[1]**2 + u0[2]**2)**0.5
                    L12 = v2[0]**2 + v2[1]**2 + v2[2]**2
                    x1 = (u0[0] * v2[0] + u0[1] * v2[1] + u0[2] * v2[2]) / L0
                    y1 = (L12 - x1**2)**0.5
                    writer.addData2f(0., 0.)
                    writer.addData2f(L0, 0.)
                    writer.addData2f(L0 + x1, y1)
                    writer.addData2f(x1, y1)
            else:
                for i in xrange(6):
                    r0, r1 = opts["texture_scale"][i]
                    writer.addData2f(0., 0.)
                    writer.addData2f(r0, 0.)
                    writer.addData2f(r0, r1)
                    writer.addData2f(0., r1)

            # Build the triangles.
            triangles = GeomTriangles(Geom.UHStatic)
            _connect(triangles, (0, 1, 2))
            _connect(triangles, (3, 2, 1))
            _connect(triangles, (0, 2, 1), 4)
            _connect(triangles, (3, 1, 2), 4)
            for i in xrange(4):
                _connect(triangles, (4 * i + 2, 4 * i + 1, 4 * i), 8)
                _connect(triangles, (4 * i + 3, 4 * i + 2, 4 * i), 8)

            # Build the Geom for the faces and initialise the node.
            self.faces = Geom(data)
            self.faces.addPrimitive(triangles)
            if self.node is None: self.node = GeomNode(opts["name"])
            self.node.addGeom(self.faces)

        if opts["line_color"] is not None:
            # Build the data vector for the border lines.
            format = GeomVertexFormat.getV3c4()
            data = GeomVertexData("vertices", format, Geom.UHStatic)
            data.setNumRows(8)
            writer = GeomVertexWriter(data, "vertex")
            for x, y, z in section: writer.addData3f(x, y, z)
            for x, y, z in section: writer.addData3f(
              x + v2[0], y + v2[1], z + v2[2])
            writer = GeomVertexWriter(data, "color")
            for _ in xrange(8): writer.addData4f(opts["line_color"])

            # Build the border lines.
            lines = GeomLines(Geom.UHStatic)
            _connect(lines, (0,1))
            _connect(lines, (0,2))
            _connect(lines, (1,3))
            _connect(lines, (3,2))
            _connect(lines, (0,1),4)
            _connect(lines, (0,2),4)
            _connect(lines, (1,3),4)
            _connect(lines, (3,2),4)
            _connect(lines, (0,4))
            _connect(lines, (1,5))
            _connect(lines, (2,6))
            _connect(lines, (3,7))

            # Build the Geom for the borders and add it to the node.
            self.lines = Geom(data)
            self.lines.addPrimitive(lines)
            if self.node is None: self.node = GeomNode(opts["name"])
            self.node.addGeom(self.lines)

class Box(Parallelepiped):
    """3D box builder from a generic parallelepiped.
    """
    def __init__(self, dx, dy, dz, **kwargs):
        section = ((-0.5 * dx, -0.5 * dy), (0.5 * dx, -0.5 * dy),
                   (-0.5 * dx, 0.5 * dy))
        Parallelepiped.__init__(self, section, dz, **kwargs)

class Map(Builder):
    """3D map builder from Panda primitives.
    """
    def __init__(self, x, y, z, face_color=(1,1,1,1), line_color=(0,0,0,1),
      name="map"):
        Builder.__init__(self)
        self.name = name
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
                    writer.addData2f(x[j], y[i])

            # Build the triangles.
            triangles = GeomTriangles(Geom.UHStatic)
            for i in xrange(ny - 1):
                for j in xrange(nx - 1):
                    d1 = abs(z[i][j] - z[i + 1][j + 1])
                    d2 = abs(z[i + 1][j] - z[i][j + 1])
                    if d1 < d2:
                        _connect(triangles,
                          (i * nx + j, i * nx + j + 1, (i + 1) * nx + j + 1))
                        _connect(triangles,
                          ((i + 1) * nx + j, i * nx + j, (i + 1) * nx + j + 1))
                    else:
                        _connect(triangles,
                          (i * nx + j, i * nx + j + 1, (i + 1) * nx + j))
                        _connect(triangles,
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
                    _connect(lines, (j,j + 1), i * nx)
            for j in xrange(nx):
                for i in xrange(ny - 1):
                    _connect(lines, (i * nx,(i + 1) * nx), j)

            # Build the Geom for lines and add it to the node.
            self.lines = Geom(data)
            self.lines.addPrimitive(lines)
            if self.node is None: self.node = GeomNode(name)
            self.node.addGeom(self.lines)

    def frame(self): raise RuntimeError("not implemented")
    def barycentric_frame(self): raise RuntimeError("not implemented")
    def barycentric_coordinates(self, point):
        raise RuntimeError("not implemented")

class Terrain(Builder):
    """3D terrain builder from maps, implementing a level of details.
    """
    def __init__(self, x, y, z, face_color=(1,1,1,1), line_color=(0,0,0,1),
      name="terrain", lod=3, dlim=50.):
        Builder.__init__(self)
        self.name = name
        self.node = True
        self.path = NodePath("Terrain")
        self.path.reparentTo(render)

        size = 2**lod - 2**(lod - 1) + 1
        nx, ny = (len(x) - 1) / (size - 1), (len(y) - 1) / (size - 1)
        yoff = 0
        for iy in xrange(ny):
            y2 = y[yoff:(yoff + size)]
            xoff = 0
            for ix in xrange(nx):
                x2 = x[xoff:(xoff + size)]
                z2 = z[yoff:(yoff + size),xoff:(xoff + size)]
                ln = LODNode("root")
                path = NodePath(ln)
                path.reparentTo(self.path)
                d = 0.
                for i in xrange(lod):
                    p = Map(x2[::2**i], y2[::2**i], z2[::2**i,::2**i],
                      face_color, line_color, name).render()
                    if i == 0: di = dlim
                    elif i == lod - 1: di = 1E+12
                    else: di = 2 * d
                    ln.addSwitch(di, d)
                    d = di
                    p.reparentTo(path)
                xoff += size - 1
            yoff += size - 1

class Track(Builder):
    """3D track builder from Panda primitives.
    """
    def __init__(self, vertices, line_color=(0,0,0,1), name="track"):
        Builder.__init__(self)
        self.name = name
        n = len(vertices)

        # Build the data vector for the line segments.
        format = GeomVertexFormat.getV3c4()
        data = GeomVertexData("vertices", format, Geom.UHStatic)
        data.setNumRows(n)
        writer = GeomVertexWriter(data, "vertex")
        for vertex in vertices:
            writer.addData3f(*vertex)
        writer = GeomVertexWriter(data, "color")
        for _ in xrange(n): writer.addData4f(line_color)

        # Connect the segments.
        lines = GeomLines(Geom.UHStatic)
        for i in xrange(n - 1):
            _connect(lines, (i, i + 1))

        # Build the Geom for lines and add it to the node.
        self.lines = Geom(data)
        self.lines.addPrimitive(lines)
        if self.node is None: self.node = GeomNode(name)
        self.node.addGeom(self.lines)

    def frame(self): raise RuntimeError("not implemented")
    def barycentric_frame(self): raise RuntimeError("not implemented")
    def barycentric_coordinates(self, point):
        raise RuntimeError("not implemented")
