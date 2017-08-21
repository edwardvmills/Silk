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

import FreeCAD

class Silk (Workbench):
	
	def __init__(self):
		self.__class__.Icon = FreeCAD.getUserAppDataDir()+"Mod" + "/Silk/Resources/Icons/Silk.svg"
		self.__class__.MenuText = "Silk"
		self.__class__.ToolTip = "NURBS Surface modeling tools focused on low degree and seam continuity "

	def Initialize(self):
		"This function is executed when FreeCAD starts"
		import ArachNURBS
		import ControlPoly4
		import CubicCurve_4
		import Point_onCurve
		import ControlPoly4_segment
		import ControlGrid44
		import CubicSurface_44
		import ControlGrid44_EdgeSegment
		import ControlGrid44_2EdgeSegments
		import ControlPoly6
		import CubicCurve_6
		import ControlGrid66
		import CubicSurface_66
		import ControlGrid64
		import CubicSurface_64
		import ControlGrid64_2Grid44
		import ControlGrid64_3_1Grid44
		import SubGrid33_2Grid64
		import ControlGrid66_4Sub
		import SubGrid63_2Surf64
		import ControlGrid3Star66_3Sub
		import ControlGrid5Star66_5Sub
		import CubicNStarSurface_NStar66
		self.list = ["ControlPoly4",
					"CubicCurve_4", 
					"Point_onCurve", 
					"ControlPoly4_segment",
					"ControlGrid44",
					"CubicSurface_44",
					"ControlGrid44_EdgeSegment",
					"ControlGrid44_2EdgeSegments",
					"ControlPoly6",
					"CubicCurve_6",
					"ControlGrid66",
					"CubicSurface_66",
					"ControlGrid64",
					"CubicSurface_64",
					"ControlGrid64_2Grid44",
					"ControlGrid64_3_1Grid44",
					"SubGrid33_2Grid64",
					"ControlGrid66_4Sub",
					"SubGrid63_2Surf64",
					"ControlGrid3Star66_3Sub",
					"ControlGrid5Star66_5Sub",
					"CubicNStarSurface_NStar66"] 
					# A list of command names created in the line above
		
		self.appendToolbar("Silk Commands",self.list) # creates a new toolbar with your commands
		self.appendMenu("Silk",self.list) # creates a new menu
		#self.appendMenu(["An existing Menu","My submenu"],self.list) # appends a submenu to an existing menu

	def Activated(self):
		"This function is executed when the workbench is activated"
		return

	def Deactivated(self):
		"This function is executed when the workbench is deactivated"
		return

	def ContextMenu(self, recipient):
		"This is executed whenever the user right-clicks on screen"
		# "recipient" will be either "view" or "tree"
		self.appendContextMenu("My commands",self.list) # add commands to the context menu

	def GetClassName(self): 
		# this function is mandatory if this is a full python workbench
		return "Gui::PythonWorkbench"
       
Gui.addWorkbench(Silk())




