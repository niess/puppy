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

# Panda3D modules.
from direct.showbase.Loader import Loader
from panda3d.core import SamplerState, Texture, TextureStage

# Global rendering options.
ANISOTROPIC_FILTERING = 4
MIPMAP = True
MIRROR = True

# Instanciate a Panda3D loader.
loader = Loader(None)

def load(path, anisotropic=None, mipmap=None, mirror=None):
    """Load a texture and apply some rendering properties.
    """
    if anisotropic is None: anisotropic = ANISOTROPIC_FILTERING
    if mipmap is None: mipmap = MIPMAP
    if mirror is None: mirror = MIRROR

    texture = loader.loadTexture(path)
    texture.setAnisotropicDegree(anisotropic)
    if mipmap:
        texture.setMagfilter(SamplerState.FT_linear_mipmap_linear)
        texture.setMinfilter(SamplerState.FT_linear_mipmap_linear)
    if mirror:
        texture.setWrapU(Texture.WM_mirror)
        texture.setWrapV(Texture.WM_mirror)
    return texture

def splatting(node, first, second, stencil, scale=None):
    """Apply a texture splatting to the provided NodePath.
    """
    # Apply the first texture.
    ts1 = TextureStage("stage-first")
    ts1.setSort(0)
    ts1.setMode(TextureStage.MReplace)
    ts1.setSavedResult(True)
    node.setTexture(ts1, first)
    # Apply the second texture.
    ts2 = TextureStage("stage-second")
    ts2.setSort(1)
    ts2.setMode(TextureStage.MReplace)
    node.setTexture(ts2, second)
    # Apply the stencil.
    ts3 = TextureStage("stage-stencil")
    ts3.setSort(2)
    ts3.setCombineRgb(TextureStage.CMInterpolate, TextureStage.CSPrevious,
      TextureStage.COSrcColor, TextureStage.CSLastSavedResult,
      TextureStage.COSrcColor, TextureStage.CSTexture,
      TextureStage.COSrcColor)
    node.setTexture(ts3, stencil)
    if scale: node.setTexScale(ts3, scale, scale)
