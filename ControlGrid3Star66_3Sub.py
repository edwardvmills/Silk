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

class ControlGrid3Star66_3Sub():
	def Activated(self):
		sel=Gui.Selection.getSelection()
		Sub_0=Gui.Selection.getSelection()[0] 
		Sub_1=Gui.Selection.getSelection()[1]
		Sub_2=Gui.Selection.getSelection()[2]
		
		a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","ControlGrid3Star66_3Sub")
		AN.ControlGrid3Star66_3Sub(a,Sub_0,Sub_1, Sub_2)
		a.ViewObject.Proxy=0 # just set it to something different from None (this assignment is needed to run an internal notification)
		a.ViewObject.LineWidth = 1.00
		a.ViewObject.LineColor = (1.00,0.67,0.00)
		a.ViewObject.PointSize = 2.00
		a.ViewObject.PointColor = (1.00,1.00,0.00)		
		FreeCAD.ActiveDocument.recompute()
	
	def GetResources(self):
		return {'Pixmap' :  path_Silk_icons + '/ControlGrid3Star66_3Sub.svg', 'MenuText': 'ControlGrid3Star66_3Sub', 'ToolTip': 'ControlGrid3Star66_3Sub'}

Gui.addCommand('ControlGrid3Star66_3Sub', ControlGrid3Star66_3Sub())
