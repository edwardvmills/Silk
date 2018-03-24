from __future__ import division # allows floating point division from integers
import Part
import FreeCAD
from FreeCAD import Base
from FreeCAD import Gui


class ControlGridNStar66_NSub:	# all in one version - 
	def __init__(self, fp , SubList):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nControlGridNStar66_NSub class Init\n")
		fp.addProperty("App::PropertyLinkList","SubList","ControlGridNStar66_NSub","Reference Sub Grids").SubList = SubList
		fp.addProperty("App::PropertyInteger","N","ControlGrid3Star66_3Sub","N").N
		fp.setEditorMode("N", 2)
		fp.addProperty("Part::PropertyGeometryList","Legs","ControlGridNStar66_NSub","control segments").Legs
		fp.addProperty("App::PropertyPythonObject","StarGrid","ControlGrid3Star66_3Sub","Poles").StarGrid
		fp.Proxy = self

	def getL1Scale(self, p0, p1, p2):
		L1_scale = (((p1 - p0).normalize()).dot(p2-p1)) / ((p1 - p0).Length)
		return L1_scale

	def StarRow2_2Sub(self, fp, Sub_0_i, Sub_1_i):
		L1Scale_Sub0_v = self.getL1Scale(fp.StarGrid[Sub_0_i][2][0], fp.StarGrid[Sub_0_i][8][0], fp.StarGrid[Sub_0_i][14][0])
		L1Scale_Sub1_u = self.getL1Scale(fp.StarGrid[Sub_1_i][12][0], fp.StarGrid[Sub_1_i][13][0], fp.StarGrid[Sub_1_i][14][0])
		L1Scale_Mid = 0.5 * (L1Scale_Sub0_v + L1Scale_Sub1_u)
		Mid_p2 = fp.StarGrid[Sub_0_i][17][0] + L1Scale_Mid * (fp.StarGrid[Sub_0_i][11][0]-fp.StarGrid[Sub_0_i][5][0])

		fp.StarGrid[Sub_0_i][17][0] = Mid_p2
		fp.StarGrid[Sub_1_i][32][0] = Mid_p2
		fp.StarGrid[Sub_0_i][16][0] = fp.StarGrid[Sub_0_i][16][0] + L1Scale_Mid * (fp.StarGrid[Sub_0_i][10][0]-fp.StarGrid[Sub_0_i][4][0])
		fp.StarGrid[Sub_1_i][26][0] = fp.StarGrid[Sub_1_i][26][0] + L1Scale_Mid * (fp.StarGrid[Sub_1_i][25][0]-fp.StarGrid[Sub_1_i][24][0])

		L1Scale_15 = 0.5 * (L1Scale_Sub0_v + L1Scale_Mid)
		L1Scale_20 = 0.5 * (L1Scale_Sub1_u + L1Scale_Mid)
		fp.StarGrid[Sub_0_i][15][0] = fp.StarGrid[Sub_0_i][15][0] + L1Scale_15 * (fp.StarGrid[Sub_0_i][9][0]-fp.StarGrid[Sub_0_i][3][0])
		fp.StarGrid[Sub_1_i][20][0] = fp.StarGrid[Sub_1_i][20][0] + L1Scale_20 * (fp.StarGrid[Sub_1_i][19][0]-fp.StarGrid[Sub_1_i][18][0])

		# control leg visualization
		Legs_Row2 = []
		Legs_Row2_i = [[[9,15],[10,16],[11,17],[14,15],[15,16],[16,17]],[[14,20],[19,20],[20,26],[25,26],[26,32]]]
		for i in Legs_Row2_i[0]:
			Legs_Row2.append(Part.LineSegment(fp.StarGrid[Sub_0_i][i[0]][0],fp.StarGrid[Sub_0_i][i[1]][0]))

		for i in Legs_Row2_i[1]:
			Legs_Row2.append(Part.LineSegment(fp.StarGrid[Sub_1_i][i[0]][0],fp.StarGrid[Sub_1_i][i[1]][0]))
		Legs = fp.Legs
		fp.Legs = Legs + Legs_Row2 # this explicit assignment works. it modifies the subclass instance property from within the parent class function.
		return 0

	def StarRow2_SubLoop(self, fp, N):
		# loop in pairs from first element to last
		for i in range(N-1):
			self.StarRow2_2Sub(fp, i, i+1)

		# close sequence by looping back a pair from last to first element
		self.StarRow2_2Sub(fp, N-1, 0)
		return 0

	def StarDiag3_Sub(self, fp, Sub_i):
		fp.StarGrid[Sub_i][21][0] = fp.StarGrid[Sub_i][20][0] + fp.StarGrid[Sub_i][15][0] - fp.StarGrid[Sub_i][14][0]

		# control leg visualization
		Legs_Diag3 = [0,0]
		Legs_Diag3[0] = Part.LineSegment(fp.StarGrid[Sub_i][15][0], fp.StarGrid[Sub_i][21][0])
		Legs_Diag3[1] = Part.LineSegment(fp.StarGrid[Sub_i][20][0], fp.StarGrid[Sub_i][21][0])

		Legs = fp.Legs
		fp.Legs = Legs + Legs_Diag3
		return 0

	def StarDiag3_SubLoop(self, fp, N):
		# loop from first element to last. no pairs, no loop back required.
		for i in range(N):
			self.StarDiag3_Sub(fp, i)
		return 0

	def StarRow3_2Sub(self, fp, Sub_0_i, Sub_1_i):
		# prepare seam point
		Mid_p2 = fp.StarGrid[Sub_0_i][17][0] + 0.5 * (fp.StarGrid[Sub_0_i][21][0]-fp.StarGrid[Sub_0_i][15][0]+fp.StarGrid[Sub_1_i][21][0]-fp.StarGrid[Sub_1_i][20][0])

		# apply seam point locally
		fp.StarGrid[Sub_0_i][23][0] = Mid_p2
		fp.StarGrid[Sub_1_i][33][0] = Mid_p2

		# average to seam neighbor locally
		fp.StarGrid[Sub_0_i][22][0] = fp.StarGrid[Sub_0_i][16][0] + 0.5 * (fp.StarGrid[Sub_0_i][21][0]-fp.StarGrid[Sub_0_i][15][0]+fp.StarGrid[Sub_0_i][23][0]-fp.StarGrid[Sub_0_i][17][0])
		fp.StarGrid[Sub_1_i][27][0] = fp.StarGrid[Sub_1_i][26][0] + 0.5 * (fp.StarGrid[Sub_1_i][21][0]-fp.StarGrid[Sub_1_i][20][0]+fp.StarGrid[Sub_1_i][33][0]-fp.StarGrid[Sub_1_i][32][0])

		Legs_Row3 = []
		Legs_Row3_i = [[[16,22],[17,23],[21,22],[22,23]],[[21,27],[26,27],[27,33]]]
		for i in Legs_Row3_i[0]:
			Legs_Row3.append(Part.LineSegment(fp.StarGrid[Sub_0_i][i[0]][0],fp.StarGrid[Sub_0_i][i[1]][0]))

		for i in Legs_Row3_i[1]:
			Legs_Row3.append(Part.LineSegment(fp.StarGrid[Sub_1_i][i[0]][0],fp.StarGrid[Sub_1_i][i[1]][0]))

		Legs = fp.Legs
		fp.Legs = Legs + Legs_Row3 
		return 0

	def StarRow3_SubLoop(self, fp, N):
		# loop in pairs from first element to last
		for i in range(N-1):
			self.StarRow3_2Sub(fp, i, i+1)
		# close sequence by looping back a pair from last to first element
		self.StarRow3_2Sub(fp, N-1, 0)
		return 0

	def StarDiag4_3Sub(self, fp, Sub_prev_i, Sub_i, Sub_next_i):
		# parallelogram diagonal 
		Sub_28_raw = fp.StarGrid[Sub_i][27][0] + (fp.StarGrid[Sub_i][22][0]-fp.StarGrid[Sub_i][21][0])
		# scaling factor. based on N? 
		# no. need to fix this. the scaling factor needs to achieve alignment between neighboring subgrids if they align,
		# and a smooth rotation if they do not align.
		# something...something...angle in the normal or maybe tangent plane. something...(1-cos()) factor.
		if fp.N == 3:
			scale = 0.75 # scaled down 75% to spread out center this works quite well for triangles actually
		if fp.N == 5:
		 scale = 1.25 # this is a mess. a single factor doesn't do it. oh well, moving on.

		Sub_28_scaled = fp.StarGrid[Sub_i][21][0] + scale * (Sub_28_raw - fp.StarGrid[Sub_i][21][0])

		Plane_prev = Part.Plane(fp.StarGrid[Sub_i][33][0],fp.StarGrid[Sub_i][23][0],fp.StarGrid[Sub_prev_i][33][0])
		Plane_next = Part.Plane(fp.StarGrid[Sub_i][33][0],fp.StarGrid[Sub_i][23][0],fp.StarGrid[Sub_next_i][23][0])

		Sub_28_prev_param = Plane_prev.parameter(Sub_28_scaled)
		Sub_28_prev_proj = Plane_prev.value(Sub_28_prev_param[0],Sub_28_prev_param[1])

		Sub_28_next_param = Plane_next.parameter(Sub_28_scaled)
		Sub_28_next_proj = Plane_next.value(Sub_28_next_param[0],Sub_28_next_param[1])

		fp.StarGrid[Sub_i][28][0] = 0.5 * Sub_28_scaled + 0.25 * (Sub_28_prev_proj + Sub_28_next_proj)

		# control leg visualization
		Legs_Diag4 = [0,0]
		Legs_Diag4[0] = Part.LineSegment(fp.StarGrid[Sub_i][22][0],fp.StarGrid[Sub_i][28][0])
		Legs_Diag4[1] = Part.LineSegment(fp.StarGrid[Sub_i][27][0],fp.StarGrid[Sub_i][28][0])

		# update instance property. direct assignment
		Legs = fp.Legs
		fp.Legs = Legs + Legs_Diag4
		return 0

	def StarDiag4_SubLoop(self, fp, N):
		# loop in triples from first element to second to last
		for i in range(N-2):
			self.StarDiag4_3Sub(fp, i, i+1, i+2)
		# close sequence by looping back two triples spanning first and last elements
		self.StarDiag4_3Sub(fp, N-2, N-1, 0)
		self.StarDiag4_3Sub(fp, N-1, 0, 1)
		return 0

	def StarDiag4_squish(self, fp, N):
		# we are going to average all poles [28] around the loop to define the squish center

		# sum all poles [28]
		Poles_28_total = Base.Vector(0,0,0)
		for i in range(N):
			Poles_28_total = Poles_28_total + fp.StarGrid[i][28][0]

		SquishCenter = (1.0 / N) * Poles_28_total

		# do cross products in pairs around the loops to get a list of normal direction approximations
		cross_total = Base.Vector(0,0,0)
		for i in range(N-1):
			cross_total = cross_total + (fp.StarGrid[i][28][0]-SquishCenter).cross(fp.StarGrid[i+1][28][0]-SquishCenter)
		# close sequence by looping back
		cross_total = cross_total + (fp.StarGrid[N-1][28][0]-SquishCenter).cross(fp.StarGrid[0][28][0]-SquishCenter)

		# define squish plane from squish center and squish normal
		Squish_Plane = Part.Plane(SquishCenter, cross_total)

		# project all diag4 points to this plane.
		projections = [0] * N
		for i in range(N):
			param = Squish_Plane.parameter(fp.StarGrid[i][28][0])
			fp.StarGrid[i][28][0] = Squish_Plane.value(param[0],param[1])

	def StarRow4_2Sub(self, fp, Sub_0_i, Sub_1_i):
		# pull up the seam at row 4
		Mid_p4 = 0.5 * (fp.StarGrid[Sub_0_i][28][0] + fp.StarGrid[Sub_1_i][28][0])
		fp.StarGrid[Sub_0_i][29][0] = Mid_p4
		fp.StarGrid[Sub_1_i][34][0] = Mid_p4

		# control leg visualization
		Legs_Row4 = [0,0,0]
		Legs_Row4[0] = Part.LineSegment(fp.StarGrid[Sub_0_i][23][0],fp.StarGrid[Sub_0_i][29][0])
		Legs_Row4[1] = Part.LineSegment(fp.StarGrid[Sub_0_i][28][0],fp.StarGrid[Sub_0_i][29][0])
		Legs_Row4[2] = Part.LineSegment(fp.StarGrid[Sub_1_i][28][0],fp.StarGrid[Sub_1_i][34][0])

		# update instance property. direct assignment
		Legs = fp.Legs
		fp.Legs = Legs + Legs_Row4
		return 0

	def StarRow4_SubLoop(self, fp, N):
		# loop in pairs from first element to last
		for i in range(N-1):
			self.StarRow4_2Sub(fp, i, i+1)
		# close sequence by looping back a pair from last to first element
		self.StarRow4_2Sub(fp, N-1, 0)
		return 0

	def StarCenter(self, fp, N):
		# we are going to average all poles [29] around the loop to define the center
		# sum all poles [29]
		Vector_total = Base.Vector(0,0,0)
		for i in range(N):
			Vector_total = Vector_total + fp.StarGrid[i][29][0]

		StarCenter = (1.0 / N) * Vector_total 

		# Apply center point to all Poles lists
		for i in range(N):
			fp.StarGrid[i][35][0] = StarCenter

		# control leg visualization
		Legs_Row5 = []
		for i in range(N):
			Legs_Row5.append(Part.LineSegment(fp.StarGrid[i][29][0],fp.StarGrid[i][35][0]))

		# update instance property. direct assignment
		Legs = fp.Legs
		fp.Legs = Legs + Legs_Row5

		return 0

	def execute(self, fp):
		# refresh properties back to linked SubGrids every time the Star gets recomputed
		# determine number of SubGrids
		fp.N=len(fp.SubList)
		# set size of Stargrid attribute
		fp.StarGrid = [0] * N
		# compile all SubGrid Poles and Weights into StarGrid attribute
		for n in range(N):
			#set size of single SubGrid
			StarGrid_n = [0] * 36
			for i in range(36):
				# set Pole/Weight format [Base.Vector(), Float]
				StarGrid_n_i = [0,0]
				StarGrid_n_i[0] = fp.SubList[n].Poles[i]
				StarGrid_n_i[1] = fp.SubList[n].Weights[i]
				StarGrid_n[i] = StarGrid_n_i
			fp.StarGrid[n] = StarGrid_n
		# a specific Pole is now addressed as StarGrid[n][i][0]
		# a specific Weight is now addresses as StarGrid[n][i][1]


		fp.Legs = []
		self.StarRow2_SubLoop(fp, fp.N)
		self.StarDiag3_SubLoop(fp, fp.N)
		self.StarRow3_SubLoop(fp, fp.N)
		self.StarDiag4_SubLoop(fp, fp.N)
		self.StarDiag4_squish(fp, N)
		self.StarRow4_SubLoop(fp, fp.N)
		self.StarCenter(fp, fp.N)

		fp.Shape = Part.Shape(fp.Legs)





sel=Gui.Selection.getSelection()
N = len(sel)

SubList = [0] * N
for i in range(N):
	SubList[i]=Gui.Selection.getSelection()[i] 




a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","ControlGridNStar66_NSub")
ControlGridNStar66_NSub(a,SubList)
a.ViewObject.Proxy=0 # just set it to something different from None (this assignment is needed to run an internal notification)
a.ViewObject.LineWidth = 1.00
a.ViewObject.LineColor = (1.00,0.67,0.00)
a.ViewObject.PointSize = 2.00
a.ViewObject.PointColor = (1.00,1.00,0.00)
FreeCAD.ActiveDocument.recompute()



