#    This file is part of Silk
#    (c) Edward Mills 2016-2025
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
from popup import tipsDialog
import tooltips

# get strings
tooltip = (tooltips.SilkPose_baseTip + tooltips.standardTipFooter)
moreInfo = (tooltips.SilkPose_baseTip + tooltips.SilkPose_moreInfo)

# Locate Workbench Directory & icon
import os, Silk_dummy
path_Silk = os.path.dirname(Silk_dummy.__file__)
path_Silk_icons =  os.path.join( path_Silk, 'Resources', 'Icons')
iconPath = path_Silk_icons + '/WIP.svg' # '/SilkPose.svg'


class SilkPose():
	def Activated(self):
		# display extended tooltip window if function was applied with no selection
		# switch to getSlecetionEx() as needed
		sel=Gui.Selection.getSelectionEx()
		if len(sel)==0:
			tipsDialog("Silk: ControlPoly4", moreInfo)
			return		
		# do other things if there is stuff in the selection
		if len(sel)==1:
			obj_ref = sel[0].Object
			sub_ref = sel[0].SubElementNames
			refs = [[obj_ref,sub_ref]]

		if len(sel)==2:
			obj0_ref = sel[0].Object
			sub0_ref = sel[0].SubElementNames
			obj1_ref = sel[1].Object
			sub1_ref = sel[1].SubElementNames
			refs = [[obj0_ref,sub0_ref],[obj1_ref, sub1_ref]]


		a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","SilkPose_000")
		AN.SilkPose(a,refs)
		a.ViewObject.Proxy=0 # just set it to something different from None (this assignment is needed to run an internal notification)
		a.ViewObject.LineWidth = 1.00
		a.ViewObject.LineColor = (0.80,0.00,0.00)
		a.ViewObject.PointSize = 4.00
		a.ViewObject.PointColor = (1.00,0.00,0.00)
		FreeCAD.ActiveDocument.recompute()


	def GetResources(self):
		return {'Pixmap':  iconPath,
	  			'MenuText': 'SilkPose',
				'ToolTip': tooltip}

Gui.addCommand('SilkPose', SilkPose())
