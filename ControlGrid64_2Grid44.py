#    This file is part of Silk
#    (c) Edward Mills 2016-2017
#    edwardvmills@gmail.com
#	
#    Silk is the user interface of ArachNURBS. This implementation is a FreeCAD workbench.
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

class ControlGrid64_2Grid44():
	def Activated(self):
		sel=Gui.Selection.getSelection()

		grid0=Gui.Selection.getSelection()[0]
		grid1=Gui.Selection.getSelection()[1]

		a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","ControlGrid64_2Grid44")
		AN.ControlGrid64_2Grid44(a,grid0,grid1)
		a.ViewObject.Proxy=0 # just set it to something different from None (this assignment is needed to run an internal notification)
		a.ViewObject.LineWidth = 1.00
		a.ViewObject.LineColor = (0.67,1.00,1.00)
		a.ViewObject.PointSize = 4.00
		a.ViewObject.PointColor = (0.00,0.33,1.00)
		FreeCAD.ActiveDocument.recompute()
			
	def GetResources(self):
		return {'Pixmap' :  FreeCAD.__path__[3] + '\Silk\Resources\Icons\ControlGrid64_2Grid44.svg', 'MenuText': 'ControlGrid64_2Grid44', 'ToolTip': 'ControlGrid64_2Grid44: \n select two ControlGrid_44 objects that share an edge (forming a corner) to generate \n a grid that blends the corner. This new grid preserves the curvature of the input grids \n on the edges away from the corner'}

Gui.addCommand('ControlGrid64_2Grid44', ControlGrid64_2Grid44())
