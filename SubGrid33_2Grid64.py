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

class SubGrid33_2Grid64():
	def Activated(self):
		sel=Gui.Selection.getSelection()

		Grid_a=Gui.Selection.getSelection()[0] 
		Grid_b=Gui.Selection.getSelection()[1]

		a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","SubGrid33_2Grid64")
		AN.SubGrid33_2Grid64(a,Grid_a,Grid_b)
		a.ViewObject.Proxy=0 # just set it to something different from None (this assignment is needed to run an internal notification)
		a.ViewObject.LineWidth = 1.00
		a.ViewObject.LineColor = (0.67,1.00,1.00)
		a.ViewObject.PointSize = 4.00
		a.ViewObject.PointColor = (0.00,0.33,1.00)
		FreeCAD.ActiveDocument.recompute()

	def GetResources(self):
		return {'Pixmap' :  path_Silk_icons + '\SubGrid33_2Grid64.svg', 'MenuText': 'SubGrid33_2Grid64',
		'ToolTip': 'SubGrid33_2Grid64: \n Select two ControlGrid_64 objects meeting at a corner \n to generate a corner blend partial grid. \n this is intended for the case where the two ControlGrid_64 objects \n are blends grids which have segments of one common surface as inputs'}

Gui.addCommand('SubGrid33_2Grid64', SubGrid33_2Grid64())
