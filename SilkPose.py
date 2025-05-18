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

		# currently works for PR mode
		# 3P is tricky and interferes witht the current PR mode assignment.
		# 2 or even three of the clicked points could belong to the same object.
		# so for  1, 2, or 3 objects in selection, need to figure out how many point were clicked
		# then assign mode, then assign refs and subrefs
		if len(sel)==1:
			picked = len(sel[0].PickedPoints)
			if picked == 1:
				mode = 'PR'
				obj_ref = sel[0].Object
				sub_ref = sel[0].SubElementNames
				refs = [[obj_ref,sub_ref]]
			elif picked == 3:
				# for 'PR' mode i throw all SubelementNames in as the Vertex ref,
				# then i always use the first SubElement for the 'PR' class vertex value.
				# now, i need to clearly differentiate the vertices immediately.
				# once that's sorted out...go back and improve 'PR' mode refs?
				mode = '3P'
				obj0_ref = sel[0].Object
				sub0_ref = sel[0].SubElementNames[0]
				obj1_ref = sel[0].Object
				sub1_ref = sel[0].SubElementNames[1]
				obj2_ref = sel[0].Object
				sub2_ref = sel[0].SubElementNames[2]
				refs = [[obj0_ref,sub0_ref], [obj1_ref,sub1_ref], [obj2_ref,sub2_ref]]
			else:
				print('SilkPose: if a single object is selected, then either 1 or 3 vertices should be selected from that object')
				return
		if len(sel)==2:
			picked0 = len(sel[0].PickedPoints) # it is mandatory that the first pick be a vertex
			picked1 = len(sel[1].PickedPoints) # there may be zero picked points here
			if picked0 == 1 and (picked1 == 0 or picked1 == 1): # two objects, and one or two vertices picked between them
				mode = 'PR'
				obj0_ref = sel[0].Object
				sub0_ref = sel[0].SubElementNames
				obj1_ref = sel[1].Object
				sub1_ref = sel[1].SubElementNames
				refs = [[obj0_ref,sub0_ref],[obj1_ref, sub1_ref]]
			if picked0+picked1 == 3: # two objects, three vertices picked altogether
				mode = '3P'
				# code below always lists refs by first and second selected object.
				# cannot discern first pick on first object, second pick on secong object, THIRD PICK on FIRST OBJECT.
				# this is because selection doesn't give a global pick order...only an pick order per object.
				if picked0 == 1:
					obj0_ref = sel[0].Object
					sub0_ref = sel[0].SubElementNames[0]
				elif picked0 == 2:
					obj0_ref = sel[0].Object
					sub0_ref = sel[0].SubElementNames[0]
					obj1_ref = sel[0].Object
					sub1_ref = sel[0].SubElementNames[1]
				if picked1 == 1:
					obj2_ref = sel[1].Object
					sub2_ref = sel[1].SubElementNames[0]
				elif picked1 == 2:
					obj1_ref = sel[1].Object
					sub1_ref = sel[1].SubElementNames[0]
					obj2_ref = sel[1].Object
					sub2_ref = sel[1].SubElementNames[1]
				refs = [[obj0_ref,sub0_ref], [obj1_ref,sub1_ref], [obj2_ref,sub2_ref]]

		if len(sel)==3: # three objects selected, need exactly 1 vertex from each
			mode = '3P'
			picked0 = len(sel[0].PickedPoints) 
			picked1 = len(sel[1].PickedPoints)
			picked2 = len(sel[2].PickedPoints)
			if picked0 != 1 or picked1 != 1 or picked2 != 1:
				print('SilkPose: if three objects are selected, there must be exactly one vertex selected in all three')
				return
			obj0_ref = sel[0].Object
			sub0_ref = sel[0].SubElementNames[0]
			obj1_ref = sel[1].Object
			sub1_ref = sel[1].SubElementNames[0]
			obj2_ref = sel[2].Object
			sub2_ref = sel[2].SubElementNames[0]
			refs = [[obj0_ref,sub0_ref], [obj1_ref,sub1_ref], [obj2_ref,sub2_ref]]

		if mode == 'PR':
			a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","SilkPose_PR_000")
			AN.SilkPose_PR(a,refs)
		if mode == '3P':
			a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","SilkPose_3P_000")
			AN.SilkPose_3P(a,refs)


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
