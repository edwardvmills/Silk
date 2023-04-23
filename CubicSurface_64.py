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

class CubicSurface_64():
	def Activated(self):
		poly=Gui.Selection.getSelection()[0]
		a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","CubicSurface_64_000")
		AN.CubicSurface_64(a,poly)
		a.ViewObject.Proxy=0 # just set it to something different from None (this assignment is needed to run an internal notification)
		a.ViewObject.DisplayMode = u"Shaded"
		a.ViewObject.ShapeColor = (0.33,0.67,1.00)
		FreeCAD.ActiveDocument.recompute()
	
	def GetResources(self):
		tooltip = (
			"Creates CubicSurface_64 from a ControlGrid64 of any type. \n"
			"Select one ControlGrid64 object. \n"
			"\n"
			"Used for mixing four point and 6 point polys/edges, or blending edges of four point contours \n"
			"Can produce blends along edges of CubicSurface_44 objects. The edges touching the blended \n"
			"objects are four pointed. The edges reaching from one blended object to the other are 6 pointed"
			"\n"
			"This is still a cubic grid/surface along both directions, but now one direction is Bezier (4 point), \n"
			"WHile the other is not Bezier (6 points).The price paid for these extra control points is that \n"
			"this surface is only garanteed G2 internally along the 6 points (may be G3 under the right setup) \n"
			"The surface is still Bezier and G3 along the 4 points direction \n")

		iconPath = path_Silk_icons + '/CubicSurface_64.svg'

		return {'Pixmap' :  iconPath,
	  			'MenuText': 'CubicSurface_64',
				'ToolTip': tooltip}

Gui.addCommand('CubicSurface_64', CubicSurface_64())
