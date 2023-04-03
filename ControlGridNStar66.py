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

import FreeCAD, Part, math
from FreeCAD import Base
from FreeCAD import Gui
import ArachNURBS as AN

# Locate Workbench Directory
import os, Silk_dummy
path_Silk = os.path.dirname(Silk_dummy.__file__)
path_Silk_icons =  os.path.join( path_Silk, 'Resources', 'Icons')

class ControlGridNStar66():
	def Activated(self):
		sel=Gui.Selection.getSelection()
		N = len(sel)
		
		if N == 1:
			a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","ControlGridNStar66_StarTrim_000")
			AN.ControlGridNStar66_StarTrim(a,sel[0])
			a.ViewObject.Proxy=0 # just set it to something different from None (this assignment is needed to run an internal notification)
			a.ViewObject.LineWidth = 1.00
			a.ViewObject.LineColor = (1.00,0.67,0.00)
			a.ViewObject.PointSize = 2.00
			a.ViewObject.PointColor = (1.00,1.00,0.00)	
		
		elif N > 1:
			SubList = [0] * N
			for i in range(N):
				SubList[i]=Gui.Selection.getSelection()[i] 
			
			a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","ControlGridNStar66_NSub_000")
			AN.ControlGridNStar66_NSub(a,SubList)
			a.ViewObject.Proxy=0 # just set it to something different from None (this assignment is needed to run an internal notification)
			a.ViewObject.LineWidth = 1.00
			a.ViewObject.LineColor = (1.00,0.67,0.00)
			a.ViewObject.PointSize = 2.00
			a.ViewObject.PointColor = (1.00,1.00,0.00)		
		
		FreeCAD.ActiveDocument.recompute()
	
	def GetResources(self):
		return {'Pixmap' :  path_Silk_icons + '/ControlGridNStar66.svg', 'MenuText': 'ControlGridNStar66', 'ToolTip': 'Creates a ControlGridNStar66 from three or more SubGrid63_2Surf64. \n Select from three to six SubGrid63_2Surf64 sequentially, counter clock-wise \n looking from the outer side. \n \n • Use to create ControlGridNStar66 to blend a corner where three or more \n   CubicSurface_64 meet at a corner \n • Input for CubicNStarSurface66 '}

Gui.addCommand('ControlGridNStar66', ControlGridNStar66())
