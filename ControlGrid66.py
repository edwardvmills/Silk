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

class ControlGrid66():
	def Activated(self):
		sel=Gui.Selection.getSelection()
		if len(sel)==4:
			mode='4sided'
		elif len(sel)==3:
			mode='3sided'

		if mode=='4sided':
			poly0=Gui.Selection.getSelection()[0]
			poly1=Gui.Selection.getSelection()[1]
			poly2=Gui.Selection.getSelection()[2]
			poly3=Gui.Selection.getSelection()[3]
			a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","ControlGrid66_4_000")
			AN.ControlGrid66_4(a,poly0, poly1, poly2, poly3)
			a.ViewObject.Proxy=0 # just set it to something different from None (this assignment is needed to run an internal notification)
			a.ViewObject.LineWidth = 1.00
			a.ViewObject.LineColor = (0.67,1.00,1.00)
			a.ViewObject.PointSize = 4.00
			a.ViewObject.PointColor = (0.00,0.33,1.00)
			FreeCAD.ActiveDocument.recompute()
			
		if mode=='3sided':
			print ('triangle mode not implemented')
			
	def GetResources(self):
		return {'Pixmap' :  path_Silk_icons + '/ControlGrid66.svg',
				'MenuText': 'ControlGrid66',
				'ToolTip': 'Create a ControlGrid66 from four connected ControlPoly6 edges. \n Select each ControlPoly6 sequentially, counter clock-wise looking from the outer side. \n \n • Input for CubicSurface_66 '}

Gui.addCommand('ControlGrid66', ControlGrid66())
