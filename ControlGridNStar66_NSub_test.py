import Part
import FreeCAD
from FreeCAD import Base
from FreeCAD import Gui

class ControlGridNStar66_NSub:
	def __init__(self, fp , SubList):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nControlGridNStar66_NSub class Init\n")
		fp.addProperty("App::PropertyLinkList","SubList","ControlGridNStar66_NSub","Reference Sub Grids").SubList = SubList
		fp.addProperty("Part::PropertyGeometryList","Legs","ControlGridNStar66_NSub","control segments").Legs
		self.normalproperty = 'a normal non-fancy string property' # this line runs, but the property is not accessible through freecad python console.
		fp.Proxy = self

	def execute(self, fp):

		# clear unneeded properties
		#for i in range
		#fp.removeProperty("Poles_%d" % i)

		for i, sub in enumerate(fp.SubList):
			fp.addProperty('App::PropertyVectorList', "Poles_%d" % i, "ControlGridNStar66_NSub", "Poles_%d" % i)
			fp.addProperty('App::PropertyFloatList', "Weights_%d" % i, "ControlGridNStar66_NSub", "Weights_%d" % i)

		print 'pull data from each linked sub grid:'
		for i, sub in enumerate(fp.SubList):
			print "Sub Grid %d pole[0] = " % i, fp.SubList[i].Poles[0]
		# build poles and weights nested lists
		Poles = [0]*len(fp.SubList)
		Weights = [0]*len(fp.SubList)

		for i, sub in enumerate(fp.SubList):
			Poles[i] = fp.SubList[i].Poles
			Weights[i] = fp.SubList[i].Weights

		# manipulate lists in Poles and weights....

		# set Poles[i] to to Poles_i and Weights[i] to Weights_i
		for i, sub in enumerate(fp.SubList):
			setattr(fp, "Poles_%d" % i, Poles[i])
			print getattr(fp, "Poles_%d" % i)
			setattr(fp, "Weights_%d" % i, Weights[i])
			print getattr(fp, "Weights_%d" % i)


sel=Gui.Selection.getSelection()
Sub_0=Gui.Selection.getSelection()[0] 
Sub_1=Gui.Selection.getSelection()[1]
Sub_2=Gui.Selection.getSelection()[2]

SubList = [Sub_0, Sub_1, Sub_2]


a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","ControlGridNStar66_NSub")
ControlGridNStar66_NSub(a,SubList)
a.ViewObject.Proxy=0 # just set it to something different from None (this assignment is needed to run an internal notification)
a.ViewObject.LineWidth = 1.00
a.ViewObject.LineColor = (1.00,0.67,0.00)
a.ViewObject.PointSize = 2.00
a.ViewObject.PointColor = (1.00,1.00,0.00)
FreeCAD.ActiveDocument.recompute()