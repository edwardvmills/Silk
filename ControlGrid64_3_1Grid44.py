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

class ControlGrid64_3_1Grid44():
	def Activated(self):
			sel=Gui.Selection.getSelection()
			selx=Gui.Selection.getSelectionEx()[0]
			NL_Grid=selx.Object			# this is a resilient link to the underlying object
			Pick=selx.PickedPoints[0]	# this is the point where the grid was picked. this corner will be rounded

			#3D view pick is not in tolerance for == check to grid points

			test_scale = (NL_Grid.Poles[15]-NL_Grid.Poles[0]).Length

			if ((NL_Grid.Poles[0]-Pick).Length / test_scale) < 0.0001:
				Corner = 0
				print 'corner 0 at Grid index 0'
			elif ((NL_Grid.Poles[3]-Pick).Length / test_scale) < 0.0001:
				Corner = 1
				print 'corner 1 at Grid index 3'
			elif ((NL_Grid.Poles[15]-Pick).Length / test_scale) < 0.0001:
				Corner = 2
				print 'corner 2 at Grid index 15'	
			elif ((NL_Grid.Poles[12]-Pick).Length / test_scale) < 0.0001:
				Corner = 3
				print 'corner 3 at Grid index 12'	
			else:
				print 'unable to identify which corner the grid was pick on. please select the grid by one of its corners in the 3D view'
				
			a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","ControlGrid64_3_Grid44")
			AN.ControlGrid64_3_1Grid44(a,NL_Grid, Corner)
			a.ViewObject.Proxy=0 # just set it to something different from None (this assignment is needed to run an internal notification)
			a.ViewObject.LineWidth = 1.00
			a.ViewObject.LineColor = (0.67,1.00,1.00)
			a.ViewObject.PointSize = 4.00
			a.ViewObject.PointColor = (0.00,0.33,1.00)
			FreeCAD.ActiveDocument.recompute()
			
	def GetResources(self):
		return {'Pixmap' :  path_Silk_icons + '\ControlGrid64_3_1Grid44.svg', 'MenuText': 'ControlGrid64_3_1Grid44', 'ToolTip': 'ControlGrid64_3_1Grid44'}

Gui.addCommand('ControlGrid64_3_1Grid44', ControlGrid64_3_1Grid44())
