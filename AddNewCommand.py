# SPDX-License-Identifier: GPL-3.0-or-later
# SPDX-FileNotice: Part of the Silk addon.

################################################################################
#                                                                              #
#   (c) 2016 Edward Mills <edwardvmills@gmail.com>                             #
#                                                                              #
#   Silk is free software: you can redistribute it and/or modify it            #
#   under the terms of the GNU General Public License as published by          #
#   the Free Software Foundation, either version 3 of the License, or          #
#   (at your option) any later version.                                        #
#                                                                              #
#   This program is distributed in the hope that it will be useful,            #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of             #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.                       #
#                                                                              #
#   See the GNU General Public License for more details.                       #
#                                                                              #
#   You should have received a copy of the GNU General Public License          #
#   along with this program. If not, see <http://www.gnu.org/licenses/>.       #
#                                                                              #
################################################################################


import FreeCAD, Part, math
from FreeCAD import Base
from FreeCAD import Gui
import ArachNURBS as AN
from popup import tipsDialog
import Silk_tooltips

# get strings
tooltip = (Silk_tooltips.AddNewCommand_baseTip + Silk_tooltips.standardTipFooter)
moreInfo = (Silk_tooltips.AddNewCommand_baseTip + Silk_tooltips.AddNewCommand_moreInfo)

# Locate Workbench Directory & icon
import os, Silk_dummy
path_Silk = os.path.dirname(Silk_dummy.__file__)
path_Silk_icons =  os.path.join( path_Silk, 'Resources', 'Icons')
iconPath = path_Silk_icons + '/AddNewCommand.svg'


class AddNewCommand():
	def Activated(self):
		# display extended tooltip window if function was applied with no selection
		# switch to getSlecetionEx() as needed
		sel=Gui.Selection.getSelection()
		if len(sel)==0:
			tipsDialog("Silk: ControlPoly4", moreInfo)
			return		
		# do other things if there is stuff in the selection
		a = 0 # replace with functional macro

	def GetResources(self):
		return {'Pixmap':  iconPath,
	  			'MenuText': 'AddNewCommand',
				'ToolTip': tooltip}

Gui.addCommand('AddNewCommand', AddNewCommand())
