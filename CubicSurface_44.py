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

class CubicSurface_44():
	def Activated(self):
		grid=Gui.Selection.getSelection()[0]
		a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","CubicSurface_44_000")
		AN.CubicSurface_44(a,grid)
		a.ViewObject.Proxy=0 # just set it to something different from None (this assignment is needed to run an internal notification)
		a.ViewObject.DisplayMode = u"Shaded"
		a.ViewObject.ShapeColor = (0.33,0.67,1.00)
		FreeCAD.ActiveDocument.recompute()

	def GetResources(self):
		return {'Pixmap' : path_Silk_icons + '/CubicSurface_44.svg',
				'MenuText': 'CubicSurface_44',
				'ToolTip': 'Create a CubicSurface from a ControlGrid44. \n Select one ControlGrid44 of any type. \n \n • Can be used for hard edge surfacing, or manually aligned for tangency \n • Can also be blended along edges with other CubicSurface_44 objects with \n   CubicSurface64 objects, for high degree continuity '}

Gui.addCommand('CubicSurface_44', CubicSurface_44())
