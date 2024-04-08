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
from popup import tipsDialog
import tooltips

# get strings
tooltip = "work in progress" #(tooltips.ControlGrid64_Surf44_baseTip + tooltips.standardTipFooter)
moreInfo = "work in progress" #(tooltips.ControlGrid64_Surf44_baseTip + tooltips.ControlGrid64_Surf44_moreInfo)

# Locate Workbench Directory
import os, Silk_dummy
path_Silk = os.path.dirname(Silk_dummy.__file__)
path_Silk_icons =  os.path.join( path_Silk, 'Resources', 'Icons')
iconPath = path_Silk_icons + '/WIP.svg'

class ControlGrid64_Surf44():
	def Activated(self):
		sel=Gui.Selection.getSelection()
		if len(sel)==0:
			tipsDialog("Silk: ControlGrid64_Surf44", moreInfo)
			return	

		selx=Gui.Selection.getSelectionEx()[0]
		Surf44 =selx.Object					# this is a resilient link to the underlying object
		Pick=selx.PickedPoints[0]				# this is the point where the surface was picked		
		uv =Surf44.Shape.Surface.parameter(Pick)	# picked point is used for an initial value

				# determine if picked point was close to a u or v edge
		u_pick = uv[0]
		v_pick = uv[1]

		if (u_pick < 0.5):
			u_toEdge = u_pick
		else:
			u_toEdge = 1 - u_pick

		if (v_pick < 0.5):
			v_toEdge = v_pick
		else:
			v_toEdge = 1 - v_pick

		if (u_toEdge < v_toEdge):
			direction_to_raise = "v"
		else:
			direction_to_raise = "u"

		a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","ControlGrid64_Surf44_000")
		AN.ControlGrid64_Surf44(a,Surf44, direction_to_raise)
		a.ViewObject.Proxy=0 # just set it to something different from None (this assignment is needed to run an internal notification)
		a.ViewObject.LineWidth = 1.00
		a.ViewObject.LineColor = (0.67,1.00,1.00)
		a.ViewObject.PointSize = 4.00
		a.ViewObject.PointColor = (0.00,0.33,1.00)
		FreeCAD.ActiveDocument.recompute()
			
	def GetResources(self):
		return {'Pixmap' :  iconPath,
	  			'MenuText': 'ControlGrid64_Surf44',
				'ToolTip': tooltip}

Gui.addCommand('ControlGrid64_Surf44', ControlGrid64_Surf44())
