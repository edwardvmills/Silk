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

class ControlGrid66_4Sub():
	def Activated(self):
		sel=Gui.Selection.getSelection()

		SubGrid_0=Gui.Selection.getSelection()[0]
		SubGrid_1=Gui.Selection.getSelection()[1]
		SubGrid_2=Gui.Selection.getSelection()[2]
		SubGrid_3=Gui.Selection.getSelection()[3]
		a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","ControlGrid66_4Sub_000")
		AN.ControlGrid66_4Sub(a,SubGrid_0, SubGrid_1, SubGrid_2, SubGrid_3)
		a.ViewObject.Proxy=0 # just set it to something different from None (this assignment is needed to run an internal notification)
		a.ViewObject.LineWidth = 1.00
		a.ViewObject.LineColor = (0.67,1.00,1.00)
		a.ViewObject.PointSize = 4.00
		a.ViewObject.PointColor = (0.00,0.33,1.00)
		FreeCAD.ActiveDocument.recompute()

	def GetResources(self):
		tooltip = (
			"Select 4 related SubGrid33_2Grid64 objects in a CC loop to form a ControlGrid66_4Sub object. \n"
			"Read SubGrid33_2Grid64 descrition first.\n"
			"\n"
			"Fills four sided holes between blends (only four sided holes). Fairly high quality final surface. \n"
			"Other tools deal with 3, 5, 6, 7...sided holes but produce lower quality results. \n"
			"\n"
			"Input for: \n"
			"-CubicSurface_66 \n"
			"\n"
			"MORE INFO \n"
			"When blending surfaces across perpendicular edges, you end up with a gap/hole at the corner, because \n"
			"you have to 'set back' both blends so they don't overlap each other. This object joins the SubGrid33 \n"
			"partial grids that extend both input ControlGrid_64s 'into' the gap, creating a single grid. The  \n"
			"surface made from this grid (using CubicSurface_66),will then bridge across all four blends, giving \n"
			"good continuity to the original surfaces \n"
			"\n"
			"Proven use cases (with reasonably high quality results): \n"
			"\n"
			"-four surfaces that share a single corner, and have edges matched bewtween then in pairs (2X2 'square' \n"
			"setup of 4 surfaces). Segment and setback the shared edges, blend them, make corner SubGrids and join \n"
			"them using this tool this to fill the hole where the shared corner was. Now you have smooth transitions \n"
			"across the four original faces\n"
			"\n"
			"-three surfaces meeting to form a hard corner (like a cube corner). Here more sectioning of the original \n"
			"surfaces is required. You end up with 2 small blends, and one larger blend. use ControlGrid64_3_1Grid44 \n"
			"opposite the large blend to create the fourth blend.  Now you have 4 blends across 3 surfaces, and can \n"
			"make the 4 SubGrids. The new grid/surface will produce a 'rolling fillet' corner between the  two small\n"
			"blends and the large blend.\n"
		)

		iconPath = path_Silk_icons + '/ControlGrid66_4Sub.svg'

		return {'Pixmap' :  iconPath, 'MenuText': 'ControlGrid66_4Sub',
		'ToolTip': tooltip}

Gui.addCommand('ControlGrid66_4Sub', ControlGrid66_4Sub())
