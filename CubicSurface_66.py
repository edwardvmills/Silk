#    This file is part of Silk
#    (c) Edward Mills 2016-2017
#    edwardvmills@gmail.com
#	
#    NURBS Surface modeling tools focused on low degree and seam continuity (FreeCAD Workbench) 
#
#    Silk is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import division # allows floating point division from integers
import FreeCAD, Part, math
from FreeCAD import Base
from FreeCAD import Gui
import ArachNURBS as AN

# Locate Workbench Directory
import os, Silk_dummy
path_Silk = os.path.dirname(Silk_dummy.__file__)
path_Silk_icons =  os.path.join( path_Silk, 'Resources', 'Icons')

class CubicSurface_66():
	def Activated(self):
		poly=Gui.Selection.getSelection()[0]
		a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","CubicSurface_66_000")
		AN.CubicSurface_66(a,poly)
		a.ViewObject.Proxy=0 # just set it to something different from None (this assignment is needed to run an internal notification)
		a.ViewObject.DisplayMode = u"Shaded"
		a.ViewObject.ShapeColor = (0.33,0.67,1.00)
		FreeCAD.ActiveDocument.recompute()
	
	def GetResources(self):
		tooltip = (
			"Create a CubicSurface_66 from a ControlGrid66. \n"
			"Select one ControlGrid66. \n"
			"\n"
			"Main purpose is to to be applied to automatically generated grids. Can also be used manually for hard \n"
			"edge surfacing, manually aligned for tangency, or even manually aligned for G2 (very difficult and limited). \n"
			"\n"
			"6 point edges cannot be blended with Silk tools (yet). \n"
			"\n"
			"MORE INFO: \n"
			"This is still a cubic surface (degree 3). But it is no longer Bezier, so additional control points are \n"
			"allowed. The price paid for these extra control points is that this surface is only garanteed G2 \n"
			" internally (may be G3 under the right setup) \n"
			"\n"
			"When segmentation does become available, it will be like so: the grid/surface will be cut into nine(9) \n"
			"ControlGrid44s at preset locations. This is an exact conversion with no loss of precision. These nine \n"
			"pieces will then be workable through all the tools available for ControlGrid44s and CubicSurface_44 \n")

		iconPath = path_Silk_icons + '/CubicSurface_66.svg'

		return {'Pixmap' :  iconPath,
	  			'MenuText': 'CubicSurface_66',
				'ToolTip': tooltip}

Gui.addCommand('CubicSurface_66', CubicSurface_66())
