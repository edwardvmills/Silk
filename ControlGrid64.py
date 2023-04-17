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

class ControlGrid64():
	def Activated(self):
		sel=Gui.Selection.getSelection()
		if len(sel)==4:
			mode='4sided'
		elif len(sel)!=4:
			mode='undefined'

		if mode=='4sided':
			poly0=Gui.Selection.getSelection()[0]
			poly1=Gui.Selection.getSelection()[1]
			poly2=Gui.Selection.getSelection()[2]
			poly3=Gui.Selection.getSelection()[3]
			a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","ControlGrid64_4_000")
			AN.ControlGrid64_4(a,poly0, poly1, poly2, poly3)
			a.ViewObject.Proxy=0 # just set it to something different from None (this assignment is needed to run an internal notification)
			a.ViewObject.LineWidth = 1.00
			a.ViewObject.LineColor = (0.67,1.00,1.00)
			a.ViewObject.PointSize = 4.00
			a.ViewObject.PointColor = (0.00,0.33,1.00)
			FreeCAD.ActiveDocument.recompute()
			
		if mode=='undefined':
			print ('please select 4 control polygons forming a loop in the following order: 6P, 4P, 6P, 4P')
			
	def GetResources(self):
		tooltip = (
			"Create a ControlGrid64 from two ControlPoly4 and two ControlPoly6 matching on opposite edges. \n"
			"Select each edge in sequence (4,6,4,6), counter clock-wise looking from the outer side. \n"
			"\n"
			"Use to create mixed degree contour surfaces \n"
			"\n"
			"Input for: \n"
			"-CubicSurface_64"
			"\n"
			"MORE INFO. Typically, these types of grids (64) are created automatically by other tools. Manually \n" 
			"creating this type of grid (and associated surface) directly from polys has limitations, because they \n"
			"cannot be segmented (yet). They cannot be blended either (yet). They are still compatible with all tools \n"
			"which take a ControlGrid64 as input, even though those tools assume that the grids were generated \n"
			"automatically.\n"
			"\n"
			"When segmentation does become available, it will be like so: the grid/surface will be cut into three \n"
			"ControlGrid44s at preset locations. This is an exact conversion with no loss of precision. These three \n"
			"pieces will then be workable through all the tools available for ControlGrid44s and CubicSurface_44 \n")

		iconPath = path_Silk_icons + '/ControlGrid64.svg'

		return {'Pixmap' : iconPath,
	  			 'MenuText': 'ControlGrid64',
				 'ToolTip': tooltip}

Gui.addCommand('ControlGrid64', ControlGrid64())
