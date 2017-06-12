#    ArachNURBS
#    (c) Edward Mills 2016-2017
#    edwardvmills@gmail.com
#    
#    ArachNURBS is a library of functions and classes to manipulate NURBS curves, surfaces, and the associated control polygons and grids
#
#    This program is free software: you can redistribute it and/or modify
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
#


import Part
import FreeCAD
from FreeCAD import Base
from FreeCAD import Gui
import math
import numpy as np

#
## Basic NURBS rules and terms
## Order >= 2
## Order:  2 = line, 3 = quadratic, 4 = cubic ...
## Degree = Order - 1
## Order = Degree + 1
## nPoles >= Order
## nPoles >= Degree + 1
## nKnots = nPoles + Order
## nKnots = nPoles + degree + 1
## knot vector strictly ascending
## Pinned knot vector: k=Order, first k knots are equal, last k knots are equal

####
#### SECTION 1: DIRECT FUNCTIONS - NO PARAMETRIC LINKING BETWEEN OBJECTS
#### SECTION 2: PYTHON FEATURE CLASSES - PARAMETRIC LINKING BETWEEN OBJECTS (start around line 340)
####

### SECTION 1: DIRECT FUNCTIONS - NO PARAMETRIC LINKING BETWEEN OBJECTS 
## Bottom up view:
## poles = 3D points with weights, as [[x,y,z],w], or [x,y,z] (these are leftovers waiting to receive weights). 
## These are the basic input data for all that follows. They are obtained from the FreeCAD functions .getPoles() and .getWeights()
## NOTE: Poles in FreeCAD, such as returned by .getPoles(), refer only to xyz coordinates of a control point, THROUGHOUT the following functions, pole means [[x,y,z],w]
## lists are probably not efficient, but until FreeCAD has fully integrated homogenous coordinates for all NURBS functions, this is easier for me :)
## right now, the computation of these scripts is ridiculously fast compared to the time taken to generate the surfaces using the FreeCAD Part.BSplineSurface() function

## direct functions actually used in the Classes / available through the Silk FreeCAD workbench:

def equalVectors(vector0,vector1,tol):	# 3D point equality test
	if (vector1-vector0).Length <= tol:
		return 1
	elif (vector1-vector0).Length <= tol:
		return 0
	
def orient_a_to_b(polesa,polesb):	# polesa and polesb are lists of poles that share one endpoint. if needed, this function reorders a so that a.end = b.start or b.end b is never modified

	if equalVectors(polesa[-1],polesb[0],0.000001):  # last point of first curve is first point of second curve
		# curve 1 is oriented properly
		return polesa
	elif equalVectors(polesa[-1],polesb[-1],0.000001):  # last point of first curve is last point of second curve
		# curve 1 is oriented properly
		return polesa
	elif equalVectors(polesa[0],polesb[0],0.000001):  # first point of first curve is first point of second curve
		# curve 1 is reversed
		return polesa[::-1]
	elif equalVectors(polesa[0],polesb[-1],0.000001):  # first point of first curve is last point of second curve
		# curve 1 is reversed
		return polesa[::-1]
	else:
		print 'curves do not share endpoints'
		return 0

def Bezier_Cubic_curve(poles):	# pinned cubic rational B spline, 4 control points Part.BSplineCurve(), cubic bezier form
#draws a degree 3 rational bspline from first to last point,
# second and third act as tangents
# poles is a list: [[[x,y,z],w],[[x,y,z],w],[[x,y,z],w],[[x,y,z],w]]
## nKnot = 4 + 3 +1 = 8
## Order = 3 + 1 = 4
	degree=3
	nPoles=4
	knot=[0,0,0,0,1,1,1,1]
	bs=Part.BSplineCurve()
	bs.increaseDegree(degree)
	id=1
	for i in range(0,len(knot)):    #-1):
		bs.insertKnot(knot[i],id,0.0000001)
	i=0
	for ii in range(0,nPoles):
		bs.setPole(ii+1,poles[i][0],poles[i][1])
		i=i+1;
	return bs

def Bezier_Bicubic_surf(grid_44):	# given a 4 x 4 control grid, build the bicubic bezier surface from a Part.BSplineSurface() in Bicubic Bezier form
	# len(knot_u) := nNodes_u + degree_u + 1
	# len(knot_v) := nNodes_v + degree_v + 1
	degree_u=3
	degree_v=3
	nNodes_u=4
	nNodes_v=4
	knot_u=[0,0,0,0,1,1,1,1]
	knot_v=[0,0,0,0,1,1,1,1]
	Bezier_Bicubic_surf=Part.BSplineSurface()
	Bezier_Bicubic_surf.increaseDegree(degree_u,degree_v)
	id=1
	for i in range(0,len(knot_u)):    #-1):
		Bezier_Bicubic_surf.insertUKnot(knot_u[i],id,0.0000001)
	id=1
	for i in range(0,len(knot_v)):    #-1):
		Bezier_Bicubic_surf.insertVKnot(knot_v[i],id,0.0000001)
	i=0
	for jj in range(0,nNodes_v):
		for ii in range(0,nNodes_u):
			Bezier_Bicubic_surf.setPole(ii+1,jj+1,grid_44[i][0], grid_44[i][1]);
			i=i+1;
	return Bezier_Bicubic_surf
	
def NURBS_Cubic_6P_curve(poles): 	# pinned cubic rational Bspline, 6 control points Part.BSplineCurve(), just enough to have independent endpoint curvature
# draws a degree 3 rational bspline from first to last point,
# second and third act as tangents
# poles is a list: [[[x,y,z],w],[[x,y,z],w],[[x,y,z],w],[[x,y,z],w],[[x,y,z],w],[[x,y,z],w]]
## nKnot = 6 + 3 +1 = 10
## Order = 3 + 1 = 4
	degree=3
	nPoles=6
	knot=[0,0,0,0,0.3333,0.6666,1,1,1,1]
	bs=Part.BSplineCurve()
	bs.increaseDegree(degree)
	id=1
	for i in range(0,len(knot)):    #-1):
		bs.insertKnot(knot[i],id,0.0000001)
	i=0
	for ii in range(0,nPoles):
		bs.setPole(ii+1,poles[i][0],poles[i][1])
		i=i+1;
	return bs

def NURBS_Cubic_66_surf(grid_66):	# given a 6 x 6 control grid, build the cubic NURBS surface from a Part.BSplineSurface().
	# len(knot_u) := nNodes_u + degree_u + 1
	# len(knot_v) := nNodes_v + degree_v + 1
	degree_u=3
	degree_v=3
	nNodes_u=6
	nNodes_v=6
	knot_u=[0,0,0,0,0.3333,0.6666,1,1,1,1]
	knot_v=[0,0,0,0,0.3333,0.6666,1,1,1,1]
	NURBS_Cubic_66_surf=Part.BSplineSurface()
	NURBS_Cubic_66_surf.increaseDegree(degree_u,degree_v)
	id=1
	for i in range(0,len(knot_u)):    #-1):
		NURBS_Cubic_66_surf.insertUKnot(knot_u[i],id,0.0000001)
	id=1
	for i in range(0,len(knot_v)):    #-1):
		NURBS_Cubic_66_surf.insertVKnot(knot_v[i],id,0.0000001)
	i=0
	for jj in range(0,nNodes_v):
		for ii in range(0,nNodes_u):
			NURBS_Cubic_66_surf.setPole(ii+1,jj+1,grid_66[i][0],grid_66[i][1]);
			i=i+1;
	return  NURBS_Cubic_66_surf

def NURBS_Cubic_64_surf(grid_64):	# given a 6 x 4 control grid, build the cubic NURBS surface from a Part.BSplineSurface().
	# len(knot_u) := nNodes_u + degree_u + 1
	# len(knot_v) := nNodes_v + degree_v + 1
	degree_u=3
	degree_v=3
	nNodes_u=6
	nNodes_v=4
	knot_u=[0,0,0,0,0.3333,0.6666,1,1,1,1]
	knot_v=[0,0,0,0,1,1,1,1]
	NURBS_Cubic_64_surf=Part.BSplineSurface()
	NURBS_Cubic_64_surf.increaseDegree(degree_u,degree_v)
	id=1
	for i in range(0,len(knot_u)):    #-1):
		NURBS_Cubic_64_surf.insertUKnot(knot_u[i],id,0.0000001)
	id=1
	for i in range(0,len(knot_v)):    #-1):
		NURBS_Cubic_64_surf.insertVKnot(knot_v[i],id,0.0000001)
	i=0
	for jj in range(0,nNodes_v):
		for ii in range(0,nNodes_u):
			NURBS_Cubic_64_surf.setPole(ii+1,jj+1,grid_64[i][0],grid_64[i][1]);
			i=i+1;
	return  NURBS_Cubic_64_surf

def blend_poly_2x4_1x6(poles_0,weights_0, poles_1, weights_1, scale_0, scale_1, scale_2, scale_3):	# blend two cubic bezier into a 6 point cubic NURBS. this function assumes poles_0 flow into poles_1 without checking.
	WeightedPoles_0=[[poles_0[0],weights_0[0]], [poles_0[1],weights_0[1]], [poles_0[2],weights_0[2]], [poles_0[3],weights_0[3]]]
	CubicCurve4_0= Bezier_Cubic_curve(WeightedPoles_0) 
	CubicCurve6_0=CubicCurve4_0
	CubicCurve6_0.insertKnot(1.0/3.0) # add knots to convert bezier to 6P
	CubicCurve6_0.insertKnot(2.0/3.0)
	
	WeightedPoles_1=[[poles_1[0],weights_1[0]], [poles_1[1],weights_1[1]], [poles_1[2],weights_1[2]], [poles_1[3],weights_1[3]]]
	CubicCurve4_1= Bezier_Cubic_curve(WeightedPoles_1) # checked good BSplineSurface object.
	CubicCurve6_1=CubicCurve4_1
	CubicCurve6_1.insertKnot(1.0/3.0) # add knots to convert bezier to 6P
	CubicCurve6_1.insertKnot(2.0/3.0)	
	
	poles_6_0=CubicCurve6_0.getPoles()
	weights_6_0=CubicCurve6_0.getWeights()
	
	poles_6_1=CubicCurve6_1.getPoles()
	weights_6_1=CubicCurve6_1.getWeights()
	
	p0=[poles_6_0[0],weights_6_0[0]]
	p1=[poles_6_0[1],weights_6_0[1]]
	p2=[poles_6_0[2],weights_6_0[2]]
	p3=[poles_6_1[3],weights_6_0[3]]
	p4=[poles_6_1[4],weights_6_0[4]]
	p5=[poles_6_1[5],weights_6_0[5]]
	corner='p01p10'
	
			
	### calculate curvature components
	## start point
	l0 = p1[0]-p0[0]					# first control leg
	tan0=Base.Vector(l0)				# make clean copy
	tan0.normalize()					# unit tangent direction
	l1=Base.Vector(tan0)				# make clean copy
	l1.multiply(tan0.dot(p2[0]-p1[0])) 	# scalar projection of second control leg along unit tangent
	h1=(p2[0]-p1[0])-l1					# height of second control leg orthogonal to tangent
	## end point
	l4 = p4[0]-p5[0]					# last control leg
	tan4=Base.Vector(l4)				# make clean copy
	tan4.normalize()					# unit tangent direction
	l3=Base.Vector(tan4)				# make clean copy
	l3.multiply(tan4.dot(p3[0]-p4[0])) 	# scalar projection of second to last control leg along unit tangent
	h3=(p3[0]-p4[0])-l3					# height of second control leg orthogonal to tangent
		
	### scale first and last control legs
	L0=Base.Vector(l0)					# make clean copy
	L0.multiply(scale_0)				# apply tangent scale
	p1_scl = [p0[0] + L0, p1[1]]		# reposition second control point
		
	L4=Base.Vector(l4)					# make clean copy
	L4.multiply(scale_3)				# apply tangent scale
	p4_scl = [p5[0] + L4, p4[1]]		# reposition fifth control point
		
	### calc new heights for inner control legs
	H1 = Base.Vector(h1)				# make clean copy
	H1.multiply(scale_0.__pow__(2))		# apply height scale
		
	H3 = Base.Vector(h3)				# make clean copy
	H3.multiply(scale_3.__pow__(2))		# apply height scale
		
	L1 = Base.Vector(l1) 				# make clean copy
	L1 = L1.multiply(scale_1)			# apply inner tangent scale
	p2_scl = [p1[0] + H1 + L1, p2[1]]	# reposition third control point
				
	L3 = Base.Vector(l3) 				# make clean copy
	L3 = L3.multiply(scale_2)			# apply inner tangent scale
	p3_scl = [p4[0] + H3 + L3, p3[1]]	# reposition third control point
		
		
	poles=[p0[0], p1_scl[0], p2_scl[0], p3_scl[0], p4_scl[0], p5[0]]
	# set the weights. No scaling at this point. No idea what happens if one of the input curve is an arc.
	# it would probably be a mess, since the curvature formulas above do not incorporate weights yet.
	weights = [p0[1], p1[1], p2[1], p3[1], p4[1], p5[1]]
	
	WeightedPoles= [[poles[0],weights[0]], [poles[1],weights[1]], [poles[2],weights[2]], [poles[3],weights[3]], [poles[4],weights[4]], [poles[5],weights[5]]]
	
	current_test = NURBS_Cubic_6P_curve(WeightedPoles)
	
	return [poles,weights]

	
## direct functions currently unused in the Classes / unavailable through the Silk FreeCAD workbench:
	
def Cubic_Bezier_ddu(pole1, pole2):   # cubic derivative at curve start (pole1) based on first two poles (no curve required). Weights not included yet
	P1=Base.Vector(pole1)
	P2=Base.Vector(pole2)
	Cubic_Bezier_ddu = (P2 - P1)*3
	return Cubic_Bezier_ddu

def Cubic_6P_ddu(pole1, pole2):   # cubic derivative at curve start (pole1) based on first two poles (no curve required). Weights not included yet
	P1=Base.Vector(pole1)
	P2=Base.Vector(pole2)
	Cubic_6P_ddu = (P2 - P1)*9
	return Cubic_6P_ddu

def Cubic_Bezier_d2du2(pole1, pole2, pole3): # cubic second derivative at curve start (pole1) based on first three poles (no curve required). Weights not included yet
	P1=Base.Vector(pole1)
	P2=Base.Vector(pole2)
	P3=Base.Vector(pole3)	
	Cubic_Bezier_d2du2 = (P1- P2*2 + P3)*6
	return Cubic_Bezier_d2du2

def Cubic_6P_d2du2(pole1, pole2, pole3): # cubic second derivative at curve start (pole1) based on first three poles (no curve required). Weights not included yet
	P1=Base.Vector(pole1)
	P2=Base.Vector(pole2)
	P3=Base.Vector(pole3)	
	Cubic_6P_d2du2 = (P1*2- P2*3 + P3)*27
	return Cubic_6P_d2du2

def Cubic_Bezier_curvature(pole1, pole2, pole3): # curvature at curve start (pole1) based on the first three poles (no curve required). Weights not included yet
	ddu = Cubic_Bezier_ddu(pole1, pole2)
	d2du2 = Cubic_Bezier_d2du2(pole1, pole2, pole3)
	Cubic_Bezier_curvature = ddu.cross(d2du2).Length/ddu.Length.__pow__(3)
	return Cubic_Bezier_curvature

def Cubic_6P_curvature(pole1, pole2, pole3): # curvature at curve start (pole1) based on the first three poles (no curve required). Weights not included yet
	ddu = Cubic_6P_ddu(pole1, pole2)
	d2du2 = Cubic_6P_d2du2(pole1, pole2, pole3)
	Cubic_6P_curvature = ddu.cross(d2du2).Length/ddu.Length.__pow__(3)
	return Cubic_6P_curvature

def isect_test(curve, surf, u):		# provides information about a curve point at parameter u as a surface intersection candidate.						
	test_point = curve.value(u)											# point on curve
	test_proj_param = surf.parameter(test_point)							# parameter of projection of curve point onto surface
	test_proj = surf.value(test_proj_param[0],test_proj_param[1])			# projection of curve point onto surface
	test_proj_tan = surf.tangent(test_proj_param[0],test_proj_param[1])		# tangents of surface at projection
	test_proj_n = test_proj_tan[0].cross(test_proj_tan[1])					# get surface normal from tangents
	test_error = test_proj - test_point									# error vector
	error = test_error.Length											# distance between curve point and its surface projection
	testdot = test_error.dot(test_proj_n)									# compare orientation of point and surface
	test_center = [test_point, test_error, error, testdot,test_proj_param]					# prepare list of results
	return test_center

def isect_curve_surf(curve, surf):	# curve / surface intersection point
	tol= 0.00000001
	# setup the parameter search span 
	test_span = [curve.FirstParameter, curve.LastParameter]
	# determine whether the curve grows from inside or outside the surface. this will govern how to split the search span
	test_u_direction =  isect_test(curve, surf, curve.FirstParameter) 	# project curve startpoint to determine if it is 'inside' or 'outside' the surface.
	if (test_u_direction[3] < 0):								# compare projection path to surface normal: dot product negative
		direction = 1											# > curve grows 'into' the surface
	elif (test_u_direction[3] > 0):								# compare projection path to surface normal: dot product positive
		direction = -1										# > curve grows 'out of' the surface
	# initialize error
	error = 1.0	
	# set up binary search loop
	loop_count = 0
	while (error > tol  and loop_count < 100):
		test_u = (test_span[1] + test_span[0]) / 2	# pick u in the center of the search span
		test =  isect_test(curve, surf, test_u)			# project curve(u) onto surface
		error = test[2]							# set current intersection error
		if ((test[3]*direction) < 0):					# is the projection still coming from outside the surface?
			test_span = [test_u, test_span[1]]		# > use second half of current span for the next search
		if ((test[3]*direction) > 0):					# is the projection coming from inside the surface?
			test_span = [test_span[0], test_u]		# > use first half of current span for the next search
		loop_count=loop_count + 1
	print 'step ', loop_count, '  u ', test_u, '  error ', test[2]
	if error > tol:
		print 'no intersection found within ', tol
		isect_curve_surf = 'NONE'
	else:
		isect_curve_surf = [test[0], test_u, test[4]]
	return  isect_curve_surf


#### SECTION 2: PYTHON FEATURE CLASSES - PARAMETRIC LINKING BETWEEN OBJECTS - IN PROGRESS

### control polygons (+sketch to input)

class ControlPoly4_3L:	# made from a single sketch containing 3 line objects connected end to end
	def __init__(self, obj , sketch):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nControlPoly4_3L class Init\n")
		obj.addProperty("App::PropertyLink","Sketch","ControlPoly4_3L","reference Sketch").Sketch = sketch
		obj.addProperty("Part::PropertyGeometryList","Legs","ControlPoly4_3L","control segments").Legs
		obj.addProperty("App::PropertyVectorList","Poles","ControlPoly4_3L","Poles").Poles
		obj.addProperty("App::PropertyFloatList","Weights","ControlPoly4_3L","Weights").Weights = [1.0,1.0,1.0,1.0]
		obj.Proxy = self

	def execute(self, fp):
		'''Do something when doing a recomputation, this method is mandatory'''
		# get all points on first three lines...error check later
		p00s=fp.Sketch.Geometry[0].StartPoint
		p01s=fp.Sketch.Geometry[0].EndPoint
		p10s=fp.Sketch.Geometry[1].StartPoint
		p11s=fp.Sketch.Geometry[1].EndPoint
		p20s=fp.Sketch.Geometry[2].StartPoint
		p21s=fp.Sketch.Geometry[2].EndPoint
		# to world
		mat=fp.Sketch.Placement.toMatrix()
		p00=mat.multiply(p00s)
		p01=mat.multiply(p01s)
		p20=mat.multiply(p20s)
		p21=mat.multiply(p21s)
		#for now assume
		fp.Poles=[p00,p01,p20,p21]
		# prepare the lines to draw the polyline
		Leg0=Part.LineSegment(p00,p01)
		Leg1=Part.LineSegment(p01,p20)
		Leg2=Part.LineSegment(p20,p21)
		#set the polygon legs property
		fp.Legs=[Leg0, Leg1, Leg2]
		# define the shape for visualization
		fp.Shape = Part.Shape(fp.Legs)

class ControlPoly4_2N:	# made from 2 node sketches. each node sketch contain one line (tangent), and one circle (endpoint) located at one end of the line.
	def __init__(self, obj , sketch0, sketch1):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nControlPoly4_2N class Init\n")
		obj.addProperty("App::PropertyLink","Sketch0","ControlPoly4_2N","reference Sketch").Sketch0 = sketch0
		obj.addProperty("App::PropertyLink","Sketch1","ControlPoly4_2N","reference Sketch").Sketch1 = sketch1
		obj.addProperty("Part::PropertyGeometryList","Legs","ControlPoly4_2N","control segments").Legs
		obj.addProperty("App::PropertyVectorList","Poles","ControlPoly4_2N","Poles").Poles
		obj.addProperty("App::PropertyFloatList","Weights","ControlPoly4_2N","Weights").Weights = [1.0,1.0,1.0,1.0]
		obj.Proxy = self

	def execute(self, fp):
		'''Do something when doing a recomputation, this method is mandatory'''
		# process Sketch0
		obj00=fp.Sketch0.Geometry[0]
		obj01=fp.Sketch0.Geometry[1]
		if obj00.__class__==Part.Circle:
			cir0=obj00
		if obj01.__class__==Part.Circle:
			cir0=obj01
		if obj00.__class__==Part.LineSegment:
			lin0=obj00
		if obj01.__class__==Part.LineSegment:
			lin0=obj01
		p00s=cir0.Center
		if lin0.StartPoint==p00s:
			p01s=lin0.EndPoint
		elif lin0.EndPoint==p00s:
			p01s=lin0.StartPoint
		# to world
		mat0=fp.Sketch0.Placement.toMatrix()
		p00=mat0.multiply(p00s)
		p01=mat0.multiply(p01s)
		# process Sketch1
		obj10=fp.Sketch1.Geometry[0]
		obj11=fp.Sketch1.Geometry[1]
		if obj10.__class__==Part.Circle:
			cir1=obj10
		if obj11.__class__==Part.Circle:
			cir1=obj11
		if obj10.__class__==Part.LineSegment:
			lin1=obj10
		if obj11.__class__==Part.LineSegment:
			lin1=obj11
		p11s=cir1.Center
		if lin1.StartPoint==p11s:
			p10s=lin1.EndPoint
		elif lin1.EndPoint==p11s:
			p10s=lin1.StartPoint
		# to world
		mat1=fp.Sketch1.Placement.toMatrix()
		p10=mat1.multiply(p10s)
		p11=mat1.multiply(p11s)
		# set the poles
		fp.Poles=[p00,p01,p10,p11]
		# prepare the polygon
		Leg0=Part.LineSegment(p00,p01)
		Leg1=Part.LineSegment(p01,p10)
		Leg2=Part.LineSegment(p10,p11)
		#set the polygon legs property
		fp.Legs=[Leg0, Leg1, Leg2]
		# define the shape for visualization
		fp.Shape = Part.Shape(fp.Legs)

class ControlPoly4_FirstElement:	# made from the first element of a single sketch. tested for straight line, circular arc (less than 90 degrees), and elliptic arc.
	def __init__(self, obj , sketch):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nControlPoly4_FirstElement class Init\n")
		obj.addProperty("App::PropertyLink","Sketch","ControlPoly4_FirstElement","reference Sketch").Sketch = sketch
		obj.addProperty("Part::PropertyGeometryList","Legs","ControlPoly4_FirstElement","control segments").Legs
		obj.addProperty("App::PropertyVectorList","Poles","ControlPoly4_FirstElement","Poles").Poles
		obj.addProperty("App::PropertyFloatList","Weights","ControlPoly4_FirstElement","Weights").Weights = [1.0,1.0,1.0,1.0]
		obj.Proxy = self

	def execute(self, fp):
		'''Do something when doing a recomputation, this method is mandatory'''
		# process the sketch...error check later
		ElemNurbs=fp.Sketch.Shape.Edges[0].toNurbs().Edge1.Curve
		ElemNurbs.increaseDegree(3)
		p0=ElemNurbs.getPole(1)
		p1=ElemNurbs.getPole(2)
		p2=ElemNurbs.getPole(3)
		p3=ElemNurbs.getPole(4)
		# already to world?
		#mat=fp.Sketch.Placement.toMatrix()
		#p0=mat.multiply(p0s)
		#p1=mat.multiply(p1s)
		#p2=mat.multiply(p2s)
		#p3=mat.multiply(p3s)
		fp.Poles=[p0,p1,p2,p3]
		# set the weights
		fp.Weights = ElemNurbs.getWeights()
		# prepare the lines to draw the polyline
		Leg0=Part.LineSegment(p0,p1)
		Leg1=Part.LineSegment(p1,p2)
		Leg2=Part.LineSegment(p2,p3)
		#set the polygon legs property
		fp.Legs=[Leg0, Leg1, Leg2]
		# define the shape for visualization
		fp.Shape = Part.Shape(fp.Legs)

class ControlPoly6_5L:	# made from a single sketch containing 5 line objects connected end to end
	def __init__(self, obj , sketch):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nControlPoly6_5L class Init\n")
		obj.addProperty("App::PropertyLink","Sketch","ControlPoly4_3L","reference Sketch").Sketch = sketch
		obj.addProperty("Part::PropertyGeometryList","Legs","ControlPoly4_3L","control segments").Legs
		obj.addProperty("App::PropertyVectorList","Poles","ControlPoly4_3L","Poles").Poles
		obj.addProperty("App::PropertyFloatList","Weights","ControlPoly4_3L","Weights").Weights = [1.0,1.0,1.0,1.0,1.0,1.0]
		obj.Proxy = self

	def execute(self, fp):
		'''Do something when doing a recomputation, this method is mandatory'''
		# get all points on first three lines...error check later
		p00s=fp.Sketch.Geometry[0].StartPoint
		p01s=fp.Sketch.Geometry[0].EndPoint
		p10s=fp.Sketch.Geometry[1].StartPoint
		p11s=fp.Sketch.Geometry[1].EndPoint
		p20s=fp.Sketch.Geometry[2].StartPoint
		p21s=fp.Sketch.Geometry[2].EndPoint
		p30s=fp.Sketch.Geometry[3].StartPoint
		p31s=fp.Sketch.Geometry[3].EndPoint
		p40s=fp.Sketch.Geometry[4].StartPoint
		p41s=fp.Sketch.Geometry[4].EndPoint
		# to world
		mat=fp.Sketch.Placement.toMatrix()
		p00=mat.multiply(p00s)
		p01=mat.multiply(p01s)
		p20=mat.multiply(p20s)
		p21=mat.multiply(p21s)
		p40=mat.multiply(p40s)
		p41=mat.multiply(p41s)
		#for now assume
		fp.Poles=[p00,p01,p20,p21,p40,p41]
		# prepare the lines to draw the polyline
		Leg0=Part.LineSegment(p00,p01)
		Leg1=Part.LineSegment(p01,p20)
		Leg2=Part.LineSegment(p20,p21)
		Leg4=Part.LineSegment(p21,p40)
		Leg5=Part.LineSegment(p40,p41)
		#set the polygon legs property
		fp.Legs=[Leg0, Leg1, Leg2, Leg4, Leg5]
		# define the shape for visualization
		fp.Shape = Part.Shape(fp.Legs)

class ControlPoly6_2N:	# made from 2 node sketches. each node sketch contain 2 lines, and one circle.
	def __init__(self, obj , sketch0, sketch1):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nControlPoly6_2N class Init\n")
		obj.addProperty("App::PropertyLink","Sketch0","ControlPoly6_2N","reference Sketch").Sketch0 = sketch0
		obj.addProperty("App::PropertyLink","Sketch1","ControlPoly6_2N","reference Sketch").Sketch1 = sketch1
		obj.addProperty("Part::PropertyGeometryList","Legs","ControlPoly6_2N","control segments").Legs
		obj.addProperty("App::PropertyVectorList","Poles","ControlPoly6_2N","Poles").Poles
		obj.addProperty("App::PropertyFloatList","Weights","ControlPoly6_2N","Weights").Weights = [1.0,1.0,1.0,1.0,1.0,1.0]
		obj.Proxy = self

	def execute(self, fp):
		'''Do something when doing a recomputation, this method is mandatory'''
		# process Sketch0
		obj00=fp.Sketch0.Geometry[0]
		obj01=fp.Sketch0.Geometry[1]
		obj02=fp.Sketch0.Geometry[2]
		# must draw the pieces in the correct order! improve later
		p00s=obj00.Center
		p01s=obj01.EndPoint
		p02s=obj02.EndPoint
		# to world
		mat0=fp.Sketch0.Placement.toMatrix()
		p00=mat0.multiply(p00s)
		p01=mat0.multiply(p01s)
		p02=mat0.multiply(p02s)
		# process Sketch1
		obj10=fp.Sketch1.Geometry[0]
		obj11=fp.Sketch1.Geometry[1]
		obj12=fp.Sketch1.Geometry[2]
		# must draw the pieces in the correct order! improve later
		p12s=obj10.Center
		p11s=obj11.EndPoint
		p10s=obj12.EndPoint
		# to world
		mat1=fp.Sketch1.Placement.toMatrix()
		p10=mat1.multiply(p10s)
		p11=mat1.multiply(p11s)
		p12=mat1.multiply(p12s)
		# set the poles
		fp.Poles=[p00,p01,p02,p10,p11, p12]
		# prepare the polygon
		Leg0=Part.LineSegment(p00,p01)
		Leg1=Part.LineSegment(p01,p02)
		Leg2=Part.LineSegment(p02,p10)
		Leg3=Part.LineSegment(p10,p11)
		Leg4=Part.LineSegment(p11,p12)
		#set the polygon legs property
		fp.Legs=[Leg0, Leg1, Leg2, Leg3, Leg4]
		# define the shape for visualization
		fp.Shape = Part.Shape(fp.Legs)

class ControlPoly6_FirstElement:	# made from the first element of a single sketch
	def __init__(self, obj , sketch):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nControlPoly6_FirstElement class Init\n")
		obj.addProperty("App::PropertyLink","Sketch","ControlPoly6_FirstElement","reference Sketch").Sketch = sketch
		obj.addProperty("Part::PropertyGeometryList","Legs","ControlPoly6_FirstElement","control segments").Legs
		obj.addProperty("App::PropertyVectorList","Poles","ControlPoly6_FirstElement","Poles").Poles
		obj.addProperty("App::PropertyFloatList","Weights","ControlPoly6_FirstElement","Weights").Weights = [1.0,1.0,1.0,1.0]
		obj.Proxy = self

	def execute(self, fp):
		'''Do something when doing a recomputation, this method is mandatory'''
		# process the sketch element...error check later
		ElemNurbs=fp.Sketch.Shape.Edges[0].toNurbs().Edge1.Curve
		ElemNurbs.increaseDegree(3)
		start=ElemNurbs.FirstParameter
		end=ElemNurbs.LastParameter
		knot1=start+(end-start)/3.0
		knot2=end-(end-start)/3.0
		ElemNurbs.insertKnot(knot1)
		ElemNurbs.insertKnot(knot2)
		p0=ElemNurbs.getPole(1)
		p1=ElemNurbs.getPole(2)
		p2=ElemNurbs.getPole(3)
		p3=ElemNurbs.getPole(4)
		p4=ElemNurbs.getPole(5)
		p5=ElemNurbs.getPole(6)
		# already to world?
		#mat=fp.Sketch.Placement.toMatrix()
		#p0=mat.multiply(p0s)
		#p1=mat.multiply(p1s)
		#p2=mat.multiply(p2s)
		#p3=mat.multiply(p3s)
		fp.Poles=[p0,p1,p2,p3,p4,p5]
		# set the weights
		fp.Weights = ElemNurbs.getWeights()
		# prepare the lines to draw the polyline
		Leg0=Part.LineSegment(p0,p1)
		Leg1=Part.LineSegment(p1,p2)
		Leg2=Part.LineSegment(p2,p3)
		Leg3=Part.LineSegment(p3,p4)
		Leg4=Part.LineSegment(p4,p5)
		#set the polygon legs property
		fp.Legs=[Leg0, Leg1, Leg2, Leg3, Leg4]
		# define the shape for visualization
		fp.Shape = Part.Shape(fp.Legs)

### control grids (+poly to input)

class ControlGrid44_4:	# made from 4 CubicControlPoly4.
	def __init__(self, obj , poly0, poly1, poly2, poly3):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nControlGrid44_4 class Init\n")
		obj.addProperty("App::PropertyLink","Poly0","ControlGrid44_4","control polygon").Poly0 = poly0
		obj.addProperty("App::PropertyLink","Poly1","ControlGrid44_4","control polygon").Poly1 = poly1
		obj.addProperty("App::PropertyLink","Poly2","ControlGrid44_4","control polygon").Poly2 = poly2
		obj.addProperty("App::PropertyLink","Poly3","ControlGrid44_4","control polygon").Poly3 = poly3
		obj.addProperty("Part::PropertyGeometryList","Legs","ControlGrid44_4","control segments").Legs
		obj.addProperty("App::PropertyVectorList","Poles","ControlGrid44_4","Poles").Poles
		obj.addProperty("App::PropertyFloatList","Weights","ControlGrid44_4","Weights").Weights
		obj.Proxy = self

	def execute(self, fp):
		'''Do something when doing a recomputation, this method is mandatory'''
		poles1=fp.Poly0.Poles
		poles2=fp.Poly1.Poles
		poles3=fp.Poly2.Poles
		poles4=fp.Poly3.Poles	
		weights1=fp.Poly0.Weights
		weights2=fp.Poly1.Weights
		weights3=fp.Poly2.Weights
		weights4=fp.Poly3.Weights
		quad12 = orient_a_to_b(poles1,poles2)
		quad23 = orient_a_to_b(poles2,poles3)
		quad34 = orient_a_to_b(poles3,poles4)
		quad41 = orient_a_to_b(poles4,poles1)	
		if quad12[0]!=poles1[0] and quad12[0]==poles1[-1]:
			weights1=weights1[::-1]
		if quad23[0]!=poles2[0] and quad23[0]==poles2[-1]:
			weights2=weights2[::-1]
		if quad34[0]!=poles3[0] and quad34[0]==poles3[-1]:
			weights3=weights3[::-1]
		if quad41[0]!=poles4[0] and quad41[0]==poles4[-1]:
			weights4=weights4[::-1]
		p00 = quad12[0]
		p01 = quad12[1]
		p02 = quad12[2]	
		p03 = quad12[3]
		p13 = quad23[1]
		p23 = quad23[2]
		p33 = quad23[3]
		p32 = quad34[1]
		p31 = quad34[2]
		p30 = quad34[3]
		p20 = quad41[1]
		p10 = quad41[2]
		p11 = p00 + (p01 - p00) +  (p10 - p00)
		p12 = p03 + (p02 - p03) +  (p13 - p03)
		p21 = p30 + (p31 - p30) +  (p20 - p30)
		p22 = p33 + (p23 - p33) +  (p32 - p33)
		fp.Poles = [p00 ,p01, p02, p03,
					p10, p11, p12, p13,
					p20, p21, p22, p23,
					p30, p31, p32, p33]
		w00 = weights1[0]
		w01 = weights1[1]
		w02 = weights1[2]
		w03 = weights1[3]
		w13 = weights2[1]
		w23 = weights2[2]
		w33 = weights2[3]
		w32 = weights3[1]
		w31 = weights3[2]
		w30 = weights3[3]
		w20 = weights4[1]
		w10 = weights4[2]
		w11 = w01*w20
		w12 = w02*w13
		w21 = w32*w10
		w22 = w23*w31
		fp.Weights = [w00 ,w01, w02, w03,
					w10, w11, w12, w13,
					w20, w21, w22, w23,
					w30, w31, w32, w33]
		Legs=[0]*24
		for i in range(0,3):
			Legs[i]=Part.LineSegment(fp.Poles[i],fp.Poles[i+1])
		for i in range(3,6):
			Legs[i]=Part.LineSegment(fp.Poles[i+1],fp.Poles[i+2])
		for i in range(6,9):
			Legs[i]=Part.LineSegment(fp.Poles[i+2],fp.Poles[i+3])
		for i in range(9,12):
			Legs[i]=Part.LineSegment(fp.Poles[i+3],fp.Poles[i+4])
		for i in range(12,16):
			Legs[i]=Part.LineSegment(fp.Poles[i-12],fp.Poles[i-8])
		for i in range(16,20):
			Legs[i]=Part.LineSegment(fp.Poles[i-12],fp.Poles[i-8])
		for i in range(20,24):
			Legs[i]=Part.LineSegment(fp.Poles[i-12],fp.Poles[i-8])
		fp.Legs=Legs
		fp.Shape = Part.Shape(fp.Legs)

class ControlGrid44_3:	# made from 3 CubicControlPoly4. degenerate grid.
	def __init__(self, obj , poly0, poly1, poly2):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nControlGrid44_3 class Init\n")
		obj.addProperty("App::PropertyLink","Poly0","ControlGrid44_3","control polygon").Poly0 = poly0
		obj.addProperty("App::PropertyLink","Poly1","ControlGrid44_3","control polygon").Poly1 = poly1
		obj.addProperty("App::PropertyLink","Poly2","ControlGrid44_3","control polygon").Poly2 = poly2
		obj.addProperty("Part::PropertyGeometryList","Legs","ControlGrid44_3","control segments").Legs
		obj.addProperty("App::PropertyVectorList","Poles","ControlGrid44_3","Poles").Poles
		obj.addProperty("App::PropertyFloatList","Weights","ControlGrid44_3","Weights").Weights
		obj.addProperty("App::PropertyFloat","TweakWeight11","ControlGrid44_3","Weights").TweakWeight11 = 1.0
		obj.Proxy = self

	def execute(self, fp):
		'''Do something when doing a recomputation, this method is mandatory'''
		poles1=fp.Poly0.Poles
		poles2=fp.Poly1.Poles
		poles3=fp.Poly2.Poles	
		weights1=fp.Poly0.Weights
		weights2=fp.Poly1.Weights
		weights3=fp.Poly2.Weights
		quad12 = orient_a_to_b(poles1,poles2)
		quad23 = orient_a_to_b(poles2,poles3)
		quad31 = orient_a_to_b(poles3,poles1)
	
		if quad12[0]!=poles1[0] and quad12[0]==poles1[-1]:
			weights1=weights1[::-1]
		if quad23[0]!=poles2[0] and quad23[0]==poles2[-1]:
			weights2=weights2[::-1]
		if quad31[0]!=poles3[0] and quad31[0]==poles3[-1]:
			weights3=weights3[::-1]
		# make sure this is a degenerate quadrangle, i.e. a triangle
		if (quad31[3] != quad12[0]):
			print 'edge loop does not form a triangle'
		#no further error handling is implemented

		p00 = quad12[0]
		p01 = quad12[1]
		p02 = quad12[2]	
		p03 = quad12[3]

		p13 = quad23[1]
		p23 = quad23[2]
		p33 = quad23[3]

		p32 = quad31[1]
		p31 = quad31[2]
		p30 = p00

		p20 = p00
		p10 = p00

		p11 = p01+p31-p30
		p12 = p02+p13-p03
		p21 = p11
		p22 = p23+p32-p33

		fp.Poles = [p00 ,p01, p02, p03,
					p10, p11, p12, p13,
					p20, p21, p22, p23,
					p30, p31, p32, p33]

		# weights below are meh. surface edges follow curves, but internal degenerate point has too much draw.
		w00 = weights1[0]
		w01 = weights1[1]
		w02 = weights1[2]
		w03 = weights1[3]

		w13 = weights2[1]
		w23 = weights2[2]
		w33 = weights2[3]

		w32 = weights3[1]
		w31 = weights3[2]
		w30 = weights3[3]

		w10 = fp.TweakWeight11
		w20 = fp.TweakWeight11

		w11 = w01*w10
		w12 = w02*w13
		w21 = w31*w20
		w22 = w23*w31
		

		fp.Weights = [w00 ,w01, w02, w03,
					w10, w11, w12, w13,
					w20, w21, w22, w23,
					w30, w31, w32, w33]
		Legs=[0]*20
		for i in range(0,3):
			Legs[i]=Part.LineSegment(fp.Poles[i],fp.Poles[i+1])
		for i in range(3,6):
			Legs[i]=Part.LineSegment(fp.Poles[i+1],fp.Poles[i+2])
		for i in range(6,9):
			Legs[i]=Part.LineSegment(fp.Poles[i+2],fp.Poles[i+3])
		for i in range(9,12):
			Legs[i]=Part.LineSegment(fp.Poles[i+3],fp.Poles[i+4])
		for i in range(12,15): #skip 0-4
			Legs[i]=Part.LineSegment(fp.Poles[i-11],fp.Poles[i-7])
		for i in range(15,17): #skip 4-8 and 5-9
			Legs[i]=Part.LineSegment(fp.Poles[i-9],fp.Poles[i-5])
		for i in range(17,20): #skip 8-12
			Legs[i]=Part.LineSegment(fp.Poles[i-8],fp.Poles[i-4])
		fp.Legs=Legs
		fp.Shape = Part.Shape(fp.Legs)

class ControlGrid66_4:	# made from 4 CubicControlPoly6.
# ControlGrid66_4(poly0, poly1, poly2, poly3)	
	def __init__(self, obj , poly0, poly1, poly2, poly3):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nControlGrid66_4 class Init\n")
		obj.addProperty("App::PropertyLink","Poly0","ControlGrid66_4","control polygon").Poly0 = poly0
		obj.addProperty("App::PropertyLink","Poly1","ControlGrid66_4","control polygon").Poly1 = poly1
		obj.addProperty("App::PropertyLink","Poly2","ControlGrid66_4","control polygon").Poly2 = poly2
		obj.addProperty("App::PropertyLink","Poly3","ControlGrid66_4","control polygon").Poly3 = poly3
		obj.addProperty("Part::PropertyGeometryList","Legs","ControlGrid66_4","control segments").Legs
		obj.addProperty("App::PropertyVectorList","Poles","ControlGrid66_4","Poles").Poles
		obj.addProperty("App::PropertyFloatList","Weights","ControlGrid66_4","Weights").Weights
		obj.Proxy = self

	def execute(self, fp):
		'''Do something when doing a recomputation, this method is mandatory'''
		poles1=fp.Poly0.Poles
		poles2=fp.Poly1.Poles
		poles3=fp.Poly2.Poles
		poles4=fp.Poly3.Poles	
		weights1=fp.Poly0.Weights
		weights2=fp.Poly1.Weights
		weights3=fp.Poly2.Weights
		weights4=fp.Poly3.Weights
		sext12 = orient_a_to_b(poles1,poles2)
		sext23 = orient_a_to_b(poles2,poles3)
		sext34 = orient_a_to_b(poles3,poles4)
		sext41 = orient_a_to_b(poles4,poles1)	
		if sext12[0]!=poles1[0] and sext12[0]==poles1[-1]:
			weights1=weights1[::-1]
		if sext23[0]!=poles2[0] and sext23[0]==poles2[-1]:
			weights2=weights2[::-1]
		if sext34[0]!=poles3[0] and sext34[0]==poles3[-1]:
			weights3=weights3[::-1]
		if sext41[0]!=poles4[0] and sext41[0]==poles4[-1]:
			weights4=weights4[::-1]
		p00 = sext12[0]
		p01 = sext12[1]
		p02 = sext12[2]	
		p03 = sext12[3]
		p04 = sext12[4]
		p05 = sext12[5]
		p15 = sext23[1]
		p25 = sext23[2]
		p35 = sext23[3]
		p45 = sext23[4]
		p55 = sext23[5]
		p54 = sext34[1]
		p53 = sext34[2]
		p52 = sext34[3]
		p51 = sext34[4]
		p50 = sext34[5]
		p40 = sext41[1]
		p30 = sext41[2]
		p20 = sext41[3]
		p10 = sext41[4]
		p11 = p01 + (p10 - p00)
		p14 = p04 + (p15 - p05)
		p41 = p51 + (p40 - p50)
		p44 = p45 + (p54 - p55)
		p12 = p02 + (p10 - p00)
		p13 = p03 + (p15 - p05)	
		p24 = p25 + (p04 - p05)
		p34 = p35 + (p54 - p55)	
		p42 = p52 + (p40 - p50)
		p43 = p53 + (p45 - p55)
		p21 = p20 + (p01 - p00)
		p31 = p30 + (p51 - p50)
		p22 = p12 + (p20 - p10)
		p23 = p13 + (p25 - p15)
		p32 = p42 + (p30 - p40)
		p33 = p43 + (p35 - p45)
		fp.Poles = [p00, p01, p02, p03, p04, p05,
					p10, p11, p12, p13, p14, p15,
					p20, p21, p22, p23, p24, p25,
					p30, p31, p32, p33, p34, p35,
					p40, p41, p42, p43, p44, p45,
					p50, p51, p52, p53, p54, p55]
		w00 = weights1[0]
		w01 = weights1[1]
		w02 = weights1[2]
		w03 = weights1[3]
		w04 = weights1[4]
		w05 = weights1[5]
		w15 = weights2[1]
		w25 = weights2[2]
		w35 = weights2[3]
		w45 = weights2[4]
		w55 = weights2[5]
		w54 = weights3[1]
		w53 = weights3[2]
		w52 = weights3[3]
		w51 = weights3[4]
		w50 = weights3[5]
		w40 = weights4[1]
		w30 = weights4[2]		
		w20 = weights4[3]
		w10 = weights4[4]
		# maybe i should average instead of multiply? needs testing.
		# currently based on the idea all wights are between 0 and 1.
		# previous used cumulative neighbor mulitplication. this drives weights too low.
		# current method multiplies the two weights along isos to the closest edge
		w11 = w01*w10
		w12 = w02*w10 
		w21 = w01*w20
		w22 = w02*w20
		w14 = w04*w15
		w13 = w03*w15
		w24 = w04*w25
		w23 = w03*w25
		w44 = w45*w54
		w34 = w35*w54
		w43 = w54*w45
		w33 = w35*w53
		w41 = w40*w51
		w31 = w30*w51
		w42 = w52*w40
		w32 = w30*w52

		fp.Weights = [w00, w01, w02, w03, w04, w05,
					w10, w11, w12, w13, w14, w15,
					w20, w21, w22, w23, w24, w25,
					w30, w31, w32, w33, w34, w35,
					w40, w41, w42, w43, w44, w45,
					w50, w51, w52, w53, w54, w55]
		Legs=[0]*60
		for i in range(0,5):
			Legs[i]=Part.LineSegment(fp.Poles[i],fp.Poles[i+1])
		for i in range(5,10):
			Legs[i]=Part.LineSegment(fp.Poles[i+1],fp.Poles[i+2])
		for i in range(10,15):
			Legs[i]=Part.LineSegment(fp.Poles[i+2],fp.Poles[i+3])
		for i in range(15,20):
			Legs[i]=Part.LineSegment(fp.Poles[i+3],fp.Poles[i+4])
		for i in range(20,25):
			Legs[i]=Part.LineSegment(fp.Poles[i+4],fp.Poles[i+5])
		for i in range(25,30):
			Legs[i]=Part.LineSegment(fp.Poles[i+5],fp.Poles[i+6])
		for i in range(30,36):
			Legs[i]=Part.LineSegment(fp.Poles[i-30],fp.Poles[i-24])
		for i in range(36,42):
			Legs[i]=Part.LineSegment(fp.Poles[i-30],fp.Poles[i-24])
		for i in range(42,48):
			Legs[i]=Part.LineSegment(fp.Poles[i-30],fp.Poles[i-24])
		for i in range(48,54):
			Legs[i]=Part.LineSegment(fp.Poles[i-30],fp.Poles[i-24])
		for i in range(54,60):
			Legs[i]=Part.LineSegment(fp.Poles[i-30],fp.Poles[i-24])

		fp.Legs=Legs
		fp.Shape = Part.Shape(fp.Legs)

class ControlGrid64_4:	# made from 2 CubicControlPoly6 and 2 CubicControlPoly4.
	def __init__(self, obj , poly6_0, poly4_1, poly6_2, poly4_3):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nControlGrid64_4 class Init\n")
		obj.addProperty("App::PropertyLink","Poly6_0","ControlGrid64_4","control polygon").Poly6_0 = poly6_0
		obj.addProperty("App::PropertyLink","Poly4_1","ControlGrid64_4","control polygon").Poly4_1 = poly4_1
		obj.addProperty("App::PropertyLink","Poly6_2","ControlGrid64_4","control polygon").Poly6_2 = poly6_2
		obj.addProperty("App::PropertyLink","Poly4_3","ControlGrid64_4","control polygon").Poly4_3 = poly4_3
		obj.addProperty("Part::PropertyGeometryList","Legs","ControlGrid64_4","control segments").Legs
		obj.addProperty("App::PropertyVectorList","Poles","ControlGrid64_4","Poles").Poles
		obj.addProperty("App::PropertyFloatList","Weights","ControlGrid64_4","Weights").Weights
		obj.Proxy = self

	def execute(self, fp):
		'''Do something when doing a recomputation, this method is mandatory'''
		poles6_0=fp.Poly6_0.Poles
		poles4_1=fp.Poly4_1.Poles
		poles6_2=fp.Poly6_2.Poles
		poles4_3=fp.Poly4_3.Poles	
		weights6_0=fp.Poly6_0.Weights
		weights4_1=fp.Poly4_1.Weights
		weights6_2=fp.Poly6_2.Weights
		weights4_3=fp.Poly4_3.Weights
		sext12 = orient_a_to_b(poles6_0,poles4_1)
		quad23 = orient_a_to_b(poles4_1,poles6_2)
		sext34 = orient_a_to_b(poles6_2,poles4_3)
		quad41 = orient_a_to_b(poles4_3,poles6_0)	
		if sext12[0]!=poles6_0[0] and sext12[0]==poles6_0[-1]:
			weights6_0=weights6_0[::-1]
		if quad23[0]!=poles4_1[0] and quad23[0]==poles4_1[-1]:
			weights4_1=weights4_1[::-1]
		if sext34[0]!=poles6_2[0] and sext34[0]==poles6_2[-1]:
			weights6_2=weights6_2[::-1]
		if quad41[0]!=poles4_3[0] and quad41[0]==poles4_3[-1]:
			weights4_3=weights4_3[::-1]
		p00 = sext12[0]
		p01 = sext12[1]
		p02 = sext12[2]	
		p03 = sext12[3]
		p04 = sext12[4]
		p05 = sext12[5]
		p15 = quad23[1]
		p25 = quad23[2]
		p35 = quad23[3]
		p34 = sext34[1]
		p33 = sext34[2]
		p32 = sext34[3]
		p31 = sext34[4]
		p30 = sext34[5]
		p20 = quad41[1]
		p10 = quad41[2]
		p11 = p01 + (p10 - p00)
		p14 = p04 + (p15 - p05)
		p21 = p31 + (p20 - p30)
		p24 = p25 + (p34 - p35)
		p12 = p02 + (p10 - p00)
		p13 = p03 + (p15 - p05)	
		p22 = p32 + (p20 - p30)
		p23 = p33 + (p25 - p35)
		fp.Poles = [p00, p01, p02, p03, p04, p05,
					p10, p11, p12, p13, p14, p15,
					p20, p21, p22, p23, p24, p25,
					p30, p31, p32, p33, p34, p35]
		w00 = weights6_0[0]
		w01 = weights6_0[1]
		w02 = weights6_0[2]
		w03 = weights6_0[3]
		w04 = weights6_0[4]
		w05 = weights6_0[5]
		w15 = weights4_1[1]
		w25 = weights4_1[2]
		w35 = weights4_1[3]
		w34 = weights6_2[1]
		w33 = weights6_2[2]
		w32 = weights6_2[3]
		w31 = weights6_2[4]
		w30 = weights6_2[5]
		w20 = weights4_3[1]
		w10 = weights4_3[2]
		# maybe i should average instead of multiply? needs testing.
		# currently based on the idea all wights are between 0 and 1.
		# previous used cumulative neighbor mulitplication. this drives weights too low.
		# current method multiplies the two weights along isos to the closest edge
		w11 = w01*w10
		w12 = w02*w10
		w13 = w03*w15
		w14 = w04*w15
		w21 = w31*w20
		w22 = w32*w20		
		w23 = w33*w25		
		w24 = w34*w25
		fp.Weights = [w00, w01, w02, w03, w04, w05,
					w10, w11, w12, w13, w14, w15,
					w20, w21, w22, w23, w24, w25,
					w30, w31, w32, w33, w34, w35]
		Legs=[0]*38
		for i in range(0,5):
			Legs[i]=Part.LineSegment(fp.Poles[i],fp.Poles[i+1])
		for i in range(5,10):
			Legs[i]=Part.LineSegment(fp.Poles[i+1],fp.Poles[i+2])
		for i in range(10,15):
			Legs[i]=Part.LineSegment(fp.Poles[i+2],fp.Poles[i+3])
		for i in range(15,20):
			Legs[i]=Part.LineSegment(fp.Poles[i+3],fp.Poles[i+4])

		for i in range(20,26):
			Legs[i]=Part.LineSegment(fp.Poles[i-20],fp.Poles[i-14])
		for i in range(26,32):
			Legs[i]=Part.LineSegment(fp.Poles[i-20],fp.Poles[i-14])
		for i in range(32,38):
			Legs[i]=Part.LineSegment(fp.Poles[i-20],fp.Poles[i-14])
		fp.Legs=Legs
		fp.Shape = Part.Shape(fp.Legs)

class ControlGrid64_3:	# made from 2 CubicControlPoly4 and 1 CubicControlPoly6. degenerate grid.
	def __init__(self, obj , poly4_0, poly6_1, poly4_2):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nControlGrid64_4 class Init\n")
		obj.addProperty("App::PropertyLink","Poly4_0","ControlGrid64_3","control polygon").Poly4_0 = poly4_0
		obj.addProperty("App::PropertyLink","Poly6_1","ControlGrid64_3","control polygon").Poly6_1 = poly6_1
		obj.addProperty("App::PropertyLink","Poly4_2","ControlGrid64_3","control polygon").Poly4_2 = poly4_2
		obj.addProperty("Part::PropertyGeometryList","Legs","ControlGrid64_3","control segments").Legs
		obj.addProperty("App::PropertyVectorList","Poles","ControlGrid64_3","Poles").Poles
		obj.addProperty("App::PropertyFloatList","Weights","ControlGrid64_3","Weights").Weights
		obj.Proxy = self

	def execute(self, fp):
		'''Do something when doing a recomputation, this method is mandatory'''
		print 'first one'
		poles4_0=fp.Poly4_0.Poles
		poles6_1=fp.Poly6_1.Poles
		poles4_2=fp.Poly4_2.Poles

		weights4_0=fp.Poly4_0.Weights
		weights6_1=fp.Poly6_1.Weights
		weights4_2=fp.Poly4_2.Weights

		sext12 = orient_a_to_b(poles6_1,poles4_2)
		quad23 = orient_a_to_b(poles4_2,poles4_0)
		quad31 = orient_a_to_b(poles4_0,poles6_1)

		if sext12[0]!=poles6_1[0] and sext12[0]==poles6_1[-1]:
			weights6_1=weights6_1[::-1]
		if quad23[0]!=poles4_2[0] and quad23[0]==poles4_2[-1]:
			weights4_2=weights4_2[::-1]
		if quad31[0]!=poles4_0[0] and quad31[0]==poles4_0[-1]:
			weights4_0=weights4_0[::-1]

		p00 = sext12[0]
		p01 = sext12[1]
		p02 = sext12[2]	
		p03 = sext12[3]
		p04 = sext12[4]
		p05 = sext12[5]

		p15 = quad23[1]
		p25 = quad23[2]
		p35 = quad23[3]

		p34 = p35
		p33 = p35
		p32 = p35
		p31 = p35
		p30 = p35

		p20 = quad31[1]
		p10 = quad31[2]

		p11 = p01 + (p10 - p00)
		p14 = p04 + (p15 - p05)
		p12 = p11
		p13 = p14
		p21 = p20 + (p25 - p35)
		p22 = p21
		p23 = p21
		p24 = p21
		fp.Poles = [p00, p01, p02, p03, p04, p05,
					p10, p11, p12, p13, p14, p15,
					p20, p21, p22, p23, p24, p25,
					p30, p31, p32, p33, p34, p35]

		w00 = weights6_1[0]
		w01 = weights6_1[1]
		w02 = weights6_1[2]
		w03 = weights6_1[3]
		w04 = weights6_1[4]
		w05 = weights6_1[5]
		w15 = weights4_2[1]
		w25 = weights4_2[2]
		w35 = weights4_2[3]
		w34 = 1
		w33 = 1
		w32 = 1
		w31 = 1
		w30 = weights4_0[0]
		w20 = weights4_0[1]
		w10 = weights4_0[2]
		
		# maybe i should average instead of multiply? needs testing.
		# currently based on the idea all weights are between 0 and 1.
		# previous used cumulative neighbor mulitplication. this drives weights too low.
		# current method multiplies the two weights along isos to the closest edge
		w11 = w01*w10*0.5
		w12 = w02*w10*0.5
		w13 = w03*w15*0.5
		w14 = w04*w15*0.5
		w21 = w31*w20*0.25
		w22 = w32*w20*0.25		
		w23 = w33*w25*0.25		
		w24 = w34*w25*0.25
		fp.Weights = [w00, w01, w02, w03, w04, w05,
					w10, w11, w12, w13, w14, w15,
					w20, w21, w22, w23, w24, w25,
					w30, w31, w32, w33, w34, w35]
		Legs=[0]*22
		for i in range(0,5):
			Legs[i]=Part.LineSegment(fp.Poles[i],fp.Poles[i+1])
		Legs[5]=Part.LineSegment(p10,p11)
		Legs[6]=Part.LineSegment(p12,p13)
		Legs[7]=Part.LineSegment(p14,p15)
		Legs[8]=Part.LineSegment(p20,p21)
		Legs[9]=Part.LineSegment(p24,p25)
		
		for i in range(10,16):
			Legs[i]=Part.LineSegment(fp.Poles[i-10],fp.Poles[i-4])
		
		Legs[16]=Part.LineSegment(p10,p20)
		Legs[17]=Part.LineSegment(p11,p21)
		Legs[18]=Part.LineSegment(p14,p24)
		Legs[19]=Part.LineSegment(p15,p25)
		Legs[20]=Part.LineSegment(p20,p30)
		Legs[21]=Part.LineSegment(p25,p35)
		
		fp.Legs=Legs
		fp.Shape = Part.Shape(fp.Legs)

### NURBS curves (+poly to input)

class CubicCurve_4:
	def __init__(self, obj , poly):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nCubicCurve_4 class Init\n")
		obj.addProperty("App::PropertyLink","Poly","CubicCurve_4","control polygon").Poly = poly
		obj.Proxy = self

	def execute(self, fp):
		'''Do something when doing a recomputation, this method is mandatory'''
		# get the poles list from the poly. legacy shape function wants 'homogeneous' coords as [[x,y,z],w]
		WeightedPoles=[[fp.Poly.Poles[0],fp.Poly.Weights[0]],
				[fp.Poly.Poles[1],fp.Poly.Weights[1]],
				[fp.Poly.Poles[2],fp.Poly.Weights[2]],
				[fp.Poly.Poles[3],fp.Poly.Weights[3]]]
		# the legacy function below sets the degree and knot vector
		fp.Shape = Bezier_Cubic_curve(WeightedPoles).toShape()

class CubicCurve_6:
	def __init__(self, obj , poly):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nCubicCurve_6 class Init\n")
		obj.addProperty("App::PropertyLink","Poly","CubicCurve_6","control polygon").Poly = poly
		obj.Proxy = self

	def execute(self, fp):
		'''Do something when doing a recomputation, this method is mandatory'''
		# get the poles list from the poly. legacy shape function wants 'homogeneous' coords as [[x,y,z],w]
		WeightedPoles=[[fp.Poly.Poles[0],fp.Poly.Weights[0]],
				[fp.Poly.Poles[1],fp.Poly.Weights[1]],
				[fp.Poly.Poles[2],fp.Poly.Weights[2]],
				[fp.Poly.Poles[3],fp.Poly.Weights[3]],
				[fp.Poly.Poles[4],fp.Poly.Weights[4]],
				[fp.Poly.Poles[5],fp.Poly.Weights[5]]]
		# the legacy function below sets the degree and knot vector
		fp.Shape = NURBS_Cubic_6P_curve(WeightedPoles).toShape()

class ControlPoly6_Bezier:
	def __init__(self, obj , cubiccurve4_0):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nControlPoly6_Bezier class Init\n")
		obj.addProperty("App::PropertyLink","Sketch","ControlPoly6_Bezier","reference Bezier Curve").CubicCurve4_0 = cubiccurve4_0
		obj.addProperty("Part::PropertyGeometryList","Legs","ControlPoly6_Bezier","control segments").Legs
		obj.addProperty("App::PropertyVectorList","Poles","ControlPoly6_Bezier","Poles").Poles
		obj.addProperty("App::PropertyFloatList","Weights","ControlPoly6_Bezier","Weights").Weights = [1.0,1.0,1.0,1.0]
		obj.Proxy = self

	def execute(self, fp):
		'''Do something when doing a recomputation, this method is mandatory'''
		# process the sketch arc...error check later
		curve=fp.fp.CubicCurve4_0.Shape
		curve.increaseDegree(3)
		start=curve.FirstParameter
		end=curve.LastParameter
		knot1=start+(end-start)/3.0
		knot2=end-(end-start)/3.0
		curve.insertKnot(knot1)
		curve.insertKnot(knot2)
		p0=curve.getPole(1)
		p1=curve.getPole(2)
		p2=curve.getPole(3)
		p3=curve.getPole(4)
		p4=curve.getPole(5)
		p5=curve.getPole(6)
		fp.Poles=[p0,p1,p2,p3,p4,p5]
		# set the weights
		fp.Weights = curve.getWeights()
		# prepare the lines to draw the polyline
		Leg0=Part.LineSegment(p0,p1)
		Leg1=Part.LineSegment(p1,p2)
		Leg2=Part.LineSegment(p2,p3)
		Leg3=Part.LineSegment(p3,p4)
		Leg4=Part.LineSegment(p4,p5)
		#set the polygon legs property
		fp.Legs=[Leg0, Leg1, Leg2, Leg3, Leg4]
		# define the shape for visualization
		fp.Shape = Part.Shape(fp.Legs)
	
### curve derived objects (+curve to input)
class ControlPoly6_FilletBezier:
	def __init__(self, obj , cubiccurve4_0, cubiccurve4_1):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nControlPoly6_FilletBezier class Init\n")
		obj.addProperty("App::PropertyLink","CubicCurve4_0","ControlPoly6_FilletBezier","First reference Bezier Curve").CubicCurve4_0 = cubiccurve4_0
		obj.addProperty("App::PropertyLink","CubicCurve4_1","ControlPoly6_FilletBezier","Second reference Bezier Curve").CubicCurve4_1 = cubiccurve4_1
		obj.addProperty("App::PropertyFloat","Scale_1","ControlPoly6_FilletBezier","First curve tangent scaling").Scale_1 = 2.0
		obj.addProperty("App::PropertyFloat","Scale_4","ControlPoly6_FilletBezier","Second curve tangent scaling").Scale_4 = 2.0
		obj.addProperty("App::PropertyFloat","Scale_2","ControlPoly6_FilletBezier","First curve inner scaling").Scale_2 = 3.0
		obj.addProperty("App::PropertyFloat","Scale_3","ControlPoly6_FilletBezier","Second curve inner scaling").Scale_3 = 3.0
		obj.addProperty("Part::PropertyGeometryList","Legs","ControlPoly6_FilletBezier","control segments").Legs
		obj.addProperty("App::PropertyVectorList","Poles","ControlPoly6_FilletBezier","Poles").Poles
		obj.addProperty("App::PropertyFloatList","Weights","ControlPoly6_FilletBezier","Weights").Weights = [1.0,1.0,1.0,1.0]
		obj.Proxy = self

	def execute(self, fp):
		'''Do something when doing a recomputation, this method is mandatory'''
		CubicCurve6_0=fp.CubicCurve4_0.Shape.Curve.copy() # make copy to keep original selection intact
		CubicCurve6_0.insertKnot(1.0/3.0) # add knots to convert bezier to 6P
		CubicCurve6_0.insertKnot(2.0/3.0)

		CubicCurve6_1=fp.CubicCurve4_1.Shape.Curve.copy() # make copy to keep original selection intact
		CubicCurve6_1.insertKnot(1.0/3.0) # add knots to convert bezier to 6P
		CubicCurve6_1.insertKnot(2.0/3.0)

		# get all poles and weights
		poles_0=CubicCurve6_0.getPoles()
		weights_0=CubicCurve6_0.getWeights()
		poles_1=CubicCurve6_1.getPoles()
		weights_1=CubicCurve6_1.getWeights()

		# get all start/end points of the curves to determine how they are connected. 
		p00 = CubicCurve6_0.StartPoint
		p01 = CubicCurve6_0.EndPoint
		p10 = CubicCurve6_1.StartPoint
		p11 = CubicCurve6_1.EndPoint

		# reorder so control points flow from first curve into second curve. this is analogous to orient_a_to_b()
		# the 'fillet' CubicCurve6 will be built based on the first three control points of the first curve, 
		# and the last three control points of the second curve (after they are oriented correctly). 
		# This allows start and end curvature control.

		corner='none'
		if equalVectors(p00,p10,0.000001): 
			p0=[poles_0[5],weights_0[5]]
			p1=[poles_0[4],weights_0[4]]
			p2=[poles_0[3],weights_0[3]]
			p3=[poles_1[3],weights_0[3]]
			p4=[poles_1[4],weights_0[4]]
			p5=[poles_1[5],weights_0[5]]
			corner='p00p10'
		
		if equalVectors(p00,p11,0.000001):
			p0=[poles_0[5],weights_0[5]]
			p1=[poles_0[4],weights_0[4]]
			p2=[poles_0[3],weights_0[3]]
			p3=[poles_1[2],weights_0[2]]
			p4=[poles_1[1],weights_0[1]]
			p5=[poles_1[0],weights_0[0]]
			corner='p00p11'
		
		if equalVectors(p01,p10,0.000001):
			p0=[poles_0[0],weights_0[0]]
			p1=[poles_0[1],weights_0[1]]
			p2=[poles_0[2],weights_0[2]]
			p3=[poles_1[3],weights_0[3]]
			p4=[poles_1[4],weights_0[4]]
			p5=[poles_1[5],weights_0[5]]
			corner='p01p10'
		
		if equalVectors(p01,p11,0.000001):
			p0=[poles_0[0],weights_0[0]]
			p1=[poles_0[1],weights_0[1]]
			p2=[poles_0[2],weights_0[2]]
			p3=[poles_1[2],weights_0[2]]
			p4=[poles_1[1],weights_0[1]]
			p5=[poles_1[0],weights_0[0]]
			corner='p01p11'

		# print warning if input curves do not join at a 'corner'		
		if corner=='none':
			print 'bezier blend/fillet only works if the curves are connected end to end'
		#no further error handling is implemented

		# at this stage, these poles are clustered around the curve start and end of the final curve.
		# They need to get 'spread out' a bit
		
		#### find start/end curvatures, scale start and end tangents, then reposition innermost control points to maintain curvature. 
		#### set the height to the tangent, but leave the length along the tangent as numeric input. what to use for a start value?
		
		############## rewrite checkpoint
		
		### calculate curvature components
		## start point
		l0 = p1[0]-p0[0]					# first control leg
		tan0=Base.Vector(l0)				# make clean copy
		tan0.normalize()					# unit tangent direction
		l1=Base.Vector(tan0)				# make clean copy
		l1.multiply(tan0.dot(p2[0]-p1[0])) 	# scalar projection of second control leg along unit tangent
		h1=(p2[0]-p1[0])-l1					# height of second control leg orthogonal to tangent
		## end point
		l4 = p4[0]-p5[0]					# last control leg
		tan4=Base.Vector(l4)				# make clean copy
		tan4.normalize()					# unit tangent direction
		l3=Base.Vector(tan4)				# make clean copy
		l3.multiply(tan4.dot(p3[0]-p4[0])) 	# scalar projection of second to last control leg along unit tangent
		h3=(p3[0]-p4[0])-l3					# height of second control leg orthogonal to tangent
		
		### scale first and last control legs
		L0=Base.Vector(l0)					# make clean copy
		L0.multiply(fp.Scale_1)				# apply tangent scale
		p1_scl = [p0[0] + L0, p1[1]]		# reposition second control point
		
		L4=Base.Vector(l4)					# make clean copy
		L4.multiply(fp.Scale_4)				# apply tangent scale
		p4_scl = [p5[0] + L4, p4[1]]		# reposition fifth control point
		
		### calc new heights for inner control legs
		H1 = Base.Vector(h1)				# make clean copy
		H1.multiply(fp.Scale_1.__pow__(2))		# apply height scale
		
		H3 = Base.Vector(h3)				# make clean copy
		H3.multiply(fp.Scale_4.__pow__(2))		# apply height scale
		
		L1 = Base.Vector(l1) 				# make clean copy
		L1 = L1.multiply(fp.Scale_2)			# apply inner tangent scale
		p2_scl = [p1[0] + H1 + L1, p2[1]]	# reposition third control point
				
		L3 = Base.Vector(l3) 				# make clean copy
		L3 = L3.multiply(fp.Scale_3)			# apply inner tangent scale
		p3_scl = [p4[0] + H3 + L3, p3[1]]	# reposition third control point
		
		
		fp.Poles=[p0[0], p1_scl[0], p2_scl[0], p3_scl[0], p4_scl[0], p5[0]]
		# set the weights. No scaling at this point. No idea what happens if one of the input curve is an arc.
		# it would probably be a mess, since the curvature formulas above do not incorporate weights yet.
		fp.Weights = [p0[1], p1[1], p2[1], p3[1], p4[1], p5[1]]
		# prepare the lines to draw the polyline
		Leg0=Part.LineSegment(p0[0],p1_scl[0])
		Leg1=Part.LineSegment(p1_scl[0],p2_scl[0])
		Leg2=Part.LineSegment(p2_scl[0],p3_scl[0])
		Leg3=Part.LineSegment(p3_scl[0],p4_scl[0])
		Leg4=Part.LineSegment(p4_scl[0],p5[0])
		#set the polygon legs property
		fp.Legs=[Leg0, Leg1, Leg2, Leg3, Leg4]
		# define the shape for visualization
		fp.Shape = Part.Shape(fp.Legs)

class Point_onCurve:
	def __init__(self, obj ,NL_Curve,u):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nPoint_onCurve class Init\n")
		obj.addProperty("App::PropertyLink","NL_Curve","Point_onCurve","reference curve").NL_Curve = NL_Curve
		obj.addProperty("App::PropertyFloat","u","Point_onCurve","parameter along curve").u = u		
		obj.addProperty("App::PropertyVector","Position","Point_onCurve","position vector").Position	
		obj.Proxy = self

	def execute(self, fp):
		'''Do something when doing a recomputation, this method is mandatory'''
		fp.Position=fp.NL_Curve.Shape.Curve.value(fp.u)
		fp.Shape = Part.Point(fp.Position).toShape()

### point derived objects (+point to input)
class ControlPoly4_segment:
	def __init__(self, obj , NL_Curve, Point_onCurve_0, Point_onCurve_1):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nControlPoly4_segment class Init\n")
		obj.addProperty("App::PropertyLink","NL_Curve","ControlPoly4_segment","reference Curve").NL_Curve = NL_Curve
		obj.addProperty("App::PropertyLink","Point_onCurve_0","ControlPoly4_segment","first reference point").Point_onCurve_0 = Point_onCurve_0
		obj.addProperty("App::PropertyLink","Point_onCurve_1","ControlPoly4_segment","second reference point").Point_onCurve_1 = Point_onCurve_1
		obj.addProperty("Part::PropertyGeometryList","Legs","ControlPoly4_3L","control segments").Legs
		obj.addProperty("App::PropertyVectorList","Poles","ControlPoly4_3L","Poles").Poles
		obj.addProperty("App::PropertyFloatList","Weights","ControlPoly4_3L","Weights").Weights = [1.0,1.0,1.0,1.0]
		obj.Proxy = self

	def execute(self, fp):
		'''Do something when doing a recomputation, this method is mandatory'''
		# get the curve
		curve=fp.NL_Curve.Shape.Curve
		# get the u span
		u0=curve.parameter(fp.Point_onCurve_0.Position)
		print(u0)
		u1=curve.parameter(fp.Point_onCurve_1.Position)
		print(u1)
		if u0<u1:
			a=u0
			b=u1
		elif u1<u0:
			a=u1
			b=u0
		# cut the curve...need to copy first to keep original?
		curve.segment(a,b)
		fp.Poles=curve.getPoles()
		fp.Weights=curve.getWeights()

		# prepare visualization elements
		p00=fp.Poles[0]
		p01=fp.Poles[1]
		p20=fp.Poles[2]
		p21=fp.Poles[3]

		# prepare the lines to draw the polyline
		Leg0=Part.LineSegment(p00,p01)
		Leg1=Part.LineSegment(p01,p20)
		Leg2=Part.LineSegment(p20,p21)
		#set the polygon legs property
		fp.Legs=[Leg0, Leg1, Leg2]
		# define the shape for visualization
		fp.Shape = Part.Shape(fp.Legs)
				
### NURBS surfaces (+grid to input)

class CubicSurface_44:
	def __init__(self, obj , grid):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nCubicSurface_44 class Init\n")
		obj.addProperty("App::PropertyLink","Grid","CubicSurface_44","control grid").Grid = grid
		obj.Proxy = self

	def execute(self, fp):
		'''Do something when doing a recomputation, this method is mandatory'''
		# get the poles list from the poly. legacy shape function wants 'homogeneous' coords as [[x,y,z],w]
		WeightedPoles=[
			[fp.Grid.Poles[0],fp.Grid.Weights[0]],
			[fp.Grid.Poles[1],fp.Grid.Weights[1]],
			[fp.Grid.Poles[2],fp.Grid.Weights[2]],
			[fp.Grid.Poles[3],fp.Grid.Weights[3]],
			[fp.Grid.Poles[4],fp.Grid.Weights[4]],
			[fp.Grid.Poles[5],fp.Grid.Weights[5]],
			[fp.Grid.Poles[6],fp.Grid.Weights[6]],
			[fp.Grid.Poles[7],fp.Grid.Weights[7]],
			[fp.Grid.Poles[8],fp.Grid.Weights[8]],
			[fp.Grid.Poles[9],fp.Grid.Weights[9]],
			[fp.Grid.Poles[10],fp.Grid.Weights[10]],
			[fp.Grid.Poles[11],fp.Grid.Weights[11]],
			[fp.Grid.Poles[12],fp.Grid.Weights[12]],
			[fp.Grid.Poles[13],fp.Grid.Weights[13]],
			[fp.Grid.Poles[14],fp.Grid.Weights[14]],
			[fp.Grid.Poles[15],fp.Grid.Weights[15]]]
		# the legacy function below sets the degree and knot vector
		fp.Shape = Bezier_Bicubic_surf(WeightedPoles).toShape()

class CubicSurface_66:
	def __init__(self, obj , grid):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nCubicSurface_66 class Init\n")
		obj.addProperty("App::PropertyLink","Grid","CubicSurface_66","control grid").Grid = grid
		obj.Proxy = self

	def execute(self, fp):
		'''Do something when doing a recomputation, this method is mandatory'''
		# get the poles list from the poly. legacy shape function wants 'homogeneous' coords as [[x,y,z],w]
		WeightedPoles=[
			[fp.Grid.Poles[0],fp.Grid.Weights[0]],
			[fp.Grid.Poles[1],fp.Grid.Weights[1]],
			[fp.Grid.Poles[2],fp.Grid.Weights[2]],
			[fp.Grid.Poles[3],fp.Grid.Weights[3]],
			[fp.Grid.Poles[4],fp.Grid.Weights[4]],
			[fp.Grid.Poles[5],fp.Grid.Weights[5]],
			[fp.Grid.Poles[6],fp.Grid.Weights[6]],
			[fp.Grid.Poles[7],fp.Grid.Weights[7]],
			[fp.Grid.Poles[8],fp.Grid.Weights[8]],
			[fp.Grid.Poles[9],fp.Grid.Weights[9]],
			[fp.Grid.Poles[10],fp.Grid.Weights[10]],
			[fp.Grid.Poles[11],fp.Grid.Weights[11]],
			[fp.Grid.Poles[12],fp.Grid.Weights[12]],
			[fp.Grid.Poles[13],fp.Grid.Weights[13]],
			[fp.Grid.Poles[14],fp.Grid.Weights[14]],
			[fp.Grid.Poles[15],fp.Grid.Weights[15]],
			[fp.Grid.Poles[16],fp.Grid.Weights[16]],
			[fp.Grid.Poles[17],fp.Grid.Weights[17]],
			[fp.Grid.Poles[18],fp.Grid.Weights[18]],
			[fp.Grid.Poles[19],fp.Grid.Weights[19]],
			[fp.Grid.Poles[20],fp.Grid.Weights[20]],
			[fp.Grid.Poles[21],fp.Grid.Weights[21]],
			[fp.Grid.Poles[22],fp.Grid.Weights[22]],
			[fp.Grid.Poles[23],fp.Grid.Weights[23]],
			[fp.Grid.Poles[24],fp.Grid.Weights[24]],
			[fp.Grid.Poles[25],fp.Grid.Weights[25]],
			[fp.Grid.Poles[26],fp.Grid.Weights[26]],
			[fp.Grid.Poles[27],fp.Grid.Weights[27]],
			[fp.Grid.Poles[28],fp.Grid.Weights[28]],
			[fp.Grid.Poles[29],fp.Grid.Weights[29]],
			[fp.Grid.Poles[30],fp.Grid.Weights[30]],
			[fp.Grid.Poles[31],fp.Grid.Weights[31]],
			[fp.Grid.Poles[32],fp.Grid.Weights[32]],
			[fp.Grid.Poles[33],fp.Grid.Weights[33]],
			[fp.Grid.Poles[34],fp.Grid.Weights[34]],
			[fp.Grid.Poles[35],fp.Grid.Weights[35]]]
		# the legacy function below sets the degree and knot vector
		fp.Shape = NURBS_Cubic_66_surf(WeightedPoles).toShape()

class CubicSurface_64:
	def __init__(self, obj , grid):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nCubicSurface_64 class Init\n")
		obj.addProperty("App::PropertyLink","Grid","CubicSurface_64","control grid").Grid = grid
		obj.Proxy = self

	def execute(self, fp):
		'''Do something when doing a recomputation, this method is mandatory'''
		# get the poles list from the poly. legacy shape function wants 'homogeneous' coords as [[x,y,z],w]
		WeightedPoles=[
			[fp.Grid.Poles[0],fp.Grid.Weights[0]],
			[fp.Grid.Poles[1],fp.Grid.Weights[1]],
			[fp.Grid.Poles[2],fp.Grid.Weights[2]],
			[fp.Grid.Poles[3],fp.Grid.Weights[3]],
			[fp.Grid.Poles[4],fp.Grid.Weights[4]],
			[fp.Grid.Poles[5],fp.Grid.Weights[5]],
			[fp.Grid.Poles[6],fp.Grid.Weights[6]],
			[fp.Grid.Poles[7],fp.Grid.Weights[7]],
			[fp.Grid.Poles[8],fp.Grid.Weights[8]],
			[fp.Grid.Poles[9],fp.Grid.Weights[9]],
			[fp.Grid.Poles[10],fp.Grid.Weights[10]],
			[fp.Grid.Poles[11],fp.Grid.Weights[11]],
			[fp.Grid.Poles[12],fp.Grid.Weights[12]],
			[fp.Grid.Poles[13],fp.Grid.Weights[13]],
			[fp.Grid.Poles[14],fp.Grid.Weights[14]],
			[fp.Grid.Poles[15],fp.Grid.Weights[15]],
			[fp.Grid.Poles[16],fp.Grid.Weights[16]],
			[fp.Grid.Poles[17],fp.Grid.Weights[17]],
			[fp.Grid.Poles[18],fp.Grid.Weights[18]],
			[fp.Grid.Poles[19],fp.Grid.Weights[19]],
			[fp.Grid.Poles[20],fp.Grid.Weights[20]],
			[fp.Grid.Poles[21],fp.Grid.Weights[21]],
			[fp.Grid.Poles[22],fp.Grid.Weights[22]],
			[fp.Grid.Poles[23],fp.Grid.Weights[23]]]
		# the legacy function below sets the degree and knot vector
		fp.Shape = NURBS_Cubic_64_surf(WeightedPoles).toShape()

# 11/25/2016. update 12/09/2016.
# There a mess to clean up in re. passing the pole/weight list to FreeCAD. 
# The 3 legacy _surf functions used above want a list of 16 X [[x,y,z],w] as input,
# but internally, they run two loops to break it back into 2D array form to feed into the actual BSplineSurface(). 
# This is only because this was the first working example i found for BSplineSurface. This was fine for a long time.
# To rotate grids easily, i need to rewrite all the code to stay in 2D array form at all times. 'all the code' means anything related to 
# grid generators and nurbs surfaces.
#
# a BSplineSurface with u along x, v along y, looked at from the top returns the following poles list
#
# [[00,01,02,03],[10,11,12,13],[20,21,22,23],[30,31,32,33]]
#
# with the following topology (rows of the list read UP in xyz topo)
#	v=1			1,1
#	03 13 23 33
#	02 12 22 32
#	01 11 21 31
#	00 10 20 30 	
#u,v=0,0		u=1
#
# So the pole list is  list of pole columns
# But the list reads as follows in the interpreter (rows DOWN)
#	00 10 20 30
#	01 11 21 31
#	02 12 22 23
#	03 13 23 33
#
# numpy.Rot90(array,n) operates ccw on the DOWN version, which is cw in xyz topo.
#
# Unfortunately, all my grid numbering schemes so far were row>column, as in
#
#	30 31 32 33 
#	20 21 22 23
#	10 11 12 13
#	00 01 02 03
#
# this will be annoying to rewrite.				
		
#### surface derived objects (+surf to input)		
		
class ControlGrid44_EdgeSegment:
	def __init__(self, obj , NL_Surface, NL_Curve):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nControlGrid44_EdgeSegment class Init\n")
		obj.addProperty("App::PropertyLink","NL_Surface","ControlGrid44_EdgeSegment","Base Surface").NL_Surface = NL_Surface
		obj.addProperty("App::PropertyLink","NL_Curve","ControlGrid44_EdgeSegment","reference Curve").NL_Curve = NL_Curve
		obj.addProperty("Part::PropertyGeometryList","Legs","ControlGrid44_EdgeSegment","control segments").Legs
		obj.addProperty("App::PropertyVectorList","Poles","ControlGrid44_EdgeSegment","Poles").Poles
		obj.addProperty("App::PropertyFloatList","Weights","ControlGrid44_EdgeSegment","Weights").Weights
		obj.Proxy = self

	def execute(self, fp):
		'''Do something when doing a recomputation, this method is mandatory'''
		# get surface
		surface=fp.NL_Surface.Shape.Surface
		# get cutting points from curve
		curve=fp.NL_Curve.Shape.Curve
		p0 = curve.StartPoint
		p1 = curve.EndPoint
		# determine u or v segmentation and get parameter span fron cutting points
		param0=surface.parameter(p0)
		print 'param0: ', param0
		param1=surface.parameter(p1)
		print 'param1: ', param1
		if ((param0[0]<0.001 and param1[0]<0.001) or (param0[0]>0.999 and param1[0]>0.999)): # if u is constant 0 or constant 1 along curve
			segdir = 'v'
			if param0[1] < param1[1]:
				t0=param0[1]
				t1=param1[1]
			if param0[1] > param1[1]:
				t0=param1[1]
				t1=param0[1]
		if ((param0[1]<0.001 and param1[1]<0.001) or (param0[1]>0.999 and param1[1]>0.999)): # if v is constant 0 or constant 1 along curve
			segdir = 'u'
			if param0[0] < param1[0]:
				t0=param0[0]
				t1=param1[0]
			if param0[0] > param1[0]:
				t0=param1[0]
				t1=param0[0]
		# filter out t0<0 and t1>1 that may occur when the xyz position is projected to uv
		if t0<0:
			t0=0
		if t1>1:
			t1=1

		# create surface segment. this works very nicely most of the time, but! 
		#sometimes .segment returns [[vector],[vector],[vector],[vector]] instad of a whole grid.
		
		print 'sgdir: ', segdir 
		print 't0 ', t0
		print 't1 ', t1
		if segdir=='u':
			surface.segment(t0,t1,0,1)
		if segdir=='v':
			surface.segment(0,1,t0,t1) # 
		# extract the control grid information from the surface segment
		poles_2dArray = surface.getPoles()
		print(poles_2dArray)
		fp.Poles = [poles_2dArray[0][0],
					poles_2dArray[0][1],
					poles_2dArray[0][2],
					poles_2dArray[0][3],
					poles_2dArray[1][0],
					poles_2dArray[1][1],
					poles_2dArray[1][2],
					poles_2dArray[1][3],
					poles_2dArray[2][0],
					poles_2dArray[2][1],
					poles_2dArray[2][2],
					poles_2dArray[2][3],
					poles_2dArray[3][0],
					poles_2dArray[3][1],
					poles_2dArray[3][2],
					poles_2dArray[3][3]]

		weights_2dArray = surface.getWeights()
		print(weights_2dArray)
		fp.Weights = [weights_2dArray[0][0],
					weights_2dArray[0][1],
					weights_2dArray[0][2],
					weights_2dArray[0][3],
					weights_2dArray[1][0],
					weights_2dArray[1][1],
					weights_2dArray[1][2],
					weights_2dArray[1][3],
					weights_2dArray[2][0],
					weights_2dArray[2][1],
					weights_2dArray[2][2],
					weights_2dArray[2][3],
					weights_2dArray[3][0],
					weights_2dArray[3][1],
					weights_2dArray[3][2],
					weights_2dArray[3][3]]



		Legs=[0]*24
		for i in range(0,3):
			Legs[i]=Part.LineSegment(fp.Poles[i],fp.Poles[i+1])
		for i in range(3,6):
			Legs[i]=Part.LineSegment(fp.Poles[i+1],fp.Poles[i+2])
		for i in range(6,9):
			Legs[i]=Part.LineSegment(fp.Poles[i+2],fp.Poles[i+3])
		for i in range(9,12):
			Legs[i]=Part.LineSegment(fp.Poles[i+3],fp.Poles[i+4])
		for i in range(12,16):
			Legs[i]=Part.LineSegment(fp.Poles[i-12],fp.Poles[i-8])
		for i in range(16,20):
			Legs[i]=Part.LineSegment(fp.Poles[i-12],fp.Poles[i-8])
		for i in range(20,24):
			Legs[i]=Part.LineSegment(fp.Poles[i-12],fp.Poles[i-8])
		fp.Legs=Legs
		fp.Shape = Part.Shape(fp.Legs)

class ControlGrid44_2EdgeSegments:
	def __init__(self, obj , NL_Surface, NL_Curve_a,NL_Curve_b):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nControlGrid44_2EdgeSegments class Init\n")
		obj.addProperty("App::PropertyLink","NL_Surface","ControlGrid44_2EdgeSegments","Base Surface").NL_Surface = NL_Surface
		obj.addProperty("App::PropertyLink","NL_Curve_a","ControlGrid44_2EdgeSegments","reference Curve a").NL_Curve_a = NL_Curve_a
		obj.addProperty("App::PropertyLink","NL_Curve_b","ControlGrid44_2EdgeSegments","reference Curve b").NL_Curve_b = NL_Curve_b		
		obj.addProperty("Part::PropertyGeometryList","Legs","ControlGrid44_2EdgeSegments","control segments").Legs
		obj.addProperty("App::PropertyVectorList","Poles","ControlGrid44_2EdgeSegments","Poles").Poles
		obj.addProperty("App::PropertyFloatList","Weights","ControlGrid44_2EdgeSegments","Weights").Weights
		obj.Proxy = self

	def execute(self, fp):
		'''Do something when doing a recomputation, this method is mandatory'''
		# get surface
		surface=fp.NL_Surface.Shape.Surface
		# get cutting points from curves
		curve_a=fp.NL_Curve_a.Shape.Curve
		a0 = curve_a.StartPoint
		a1 = curve_a.EndPoint
		
		curve_b=fp.NL_Curve_b.Shape.Curve
		b0 = curve_b.StartPoint
		b1 = curve_b.EndPoint
		
		
		# determine u or v segmentation and get parameter span fron cutting points for curve a
		param_a0=surface.parameter(a0)
		#print 'param_a0: ', param_a0
		param_a1=surface.parameter(a1)
		#print 'param_a1: ', param_a1
		if ((param_a0[0]<0.001 and param_a1[0]<0.001) or (param_a0[0]>0.999 and param_a1[0]>0.999)): # if u is constant 0 or constant 1 along curve
			segdira = 'v'
			if param_a0[1] < param_a1[1]:
				s0=param_a0[1]
				s1=param_a1[1]
			if param_a0[1] > param_a1[1]:
				s0=param_a1[1]
				s1=param_a0[1]
		if ((param_a0[1]<0.001 and param_a1[1]<0.001) or (param_a0[1]>0.999 and param_a1[1]>0.999)): # if v is constant 0 or constant 1 along curve
			segdira = 'u'
			if param_a0[0] < param_a1[0]:
				s0=param_a0[0]
				s1=param_a1[0]
			if param_a0[0] > param_a1[0]:
				s0=param_a1[0]
				s1=param_a0[0]
		# filter out s0<0 and s1>1 that may occur when the xyz position is projected to uv
		if s0<0:
			s0=0
		if s1>1:
			s1=1

		# determine u or v segmentation and get parameter span fron cutting points for curve b
		param_b0=surface.parameter(b0)
		#print 'param_b0: ', param_b0
		param_b1=surface.parameter(b1)
		#print 'param_b1: ', param_b1
		if ((param_b0[0]<0.001 and param_b1[0]<0.001) or (param_b0[0]>0.999 and param_b1[0]>0.999)): # if u is constant 0 or constant 1 along curve
			segdirb = 'v'
			if param_b0[1] < param_b1[1]:
				t0=param_b0[1]
				t1=param_b1[1]
			if param_b0[1] > param_b1[1]:
				t0=param_b1[1]
				t1=param_b0[1]
		if ((param_b0[1]<0.001 and param_b1[1]<0.001) or (param_b0[1]>0.999 and param_b1[1]>0.999)): # if v is constant 0 or constant 1 along curve
			segdirb = 'u'
			if param_b0[0] < param_b1[0]:
				t0=param_b0[0]
				t1=param_b1[0]
			if param_b0[0] > param_b1[0]:
				t0=param_b1[0]
				t1=param_b0[0]
		# filter out t0<0 and t1>1 that may occur when the xyz position is projected to uv
		if t0<0:
			t0=0
		if t1>1:
			t1=1			
			
			
		# create surface segment. this works very nicely most of the time, but! 
		#sometimes .segment returns [[vector],[vector],[vector],[vector]] instad of a whole grid.
			
		if segdira=='u' and segdirb=='v':
			surface.segment(s0,s1,t0,t1)
		if segdira=='v' and segdirb=='u':
			surface.segment(t0,t1,s0,s1) # 
		# extract the control grid information from the surface segment
		# first version flips the grid along v???? need to run down 3 to 0 on v while looping 0 to 3 on u ?????
		poles_2dArray = surface.getPoles()
		if len(poles_2dArray[0]) == 1:
			print 'collapsed surface segment'
			print 'segdira: ', segdira
			print 'segdirb: ', segdirb
			print 's0 ', s0
			print 's1 ', s1		
			print 't0 ', t0
			print 't1 ', t1
			print 'poles_2dArray', poles_2dArray
			
			
		fp.Poles = [poles_2dArray[3][0],
					poles_2dArray[3][1],
					poles_2dArray[3][2],
					poles_2dArray[3][3],
					poles_2dArray[2][0],
					poles_2dArray[2][1],
					poles_2dArray[2][2],
					poles_2dArray[2][3],
					poles_2dArray[1][0],
					poles_2dArray[1][1],
					poles_2dArray[1][2],
					poles_2dArray[1][3],
					poles_2dArray[0][0],
					poles_2dArray[0][1],
					poles_2dArray[0][2],
					poles_2dArray[0][3]]
					
		weights_2dArray = surface.getWeights()
		fp.Weights = [weights_2dArray[3][0],
					weights_2dArray[3][1],
					weights_2dArray[3][2],
					weights_2dArray[3][3],
					weights_2dArray[2][0],
					weights_2dArray[2][1],
					weights_2dArray[2][2],
					weights_2dArray[2][3],
					weights_2dArray[1][0],
					weights_2dArray[1][1],
					weights_2dArray[1][2],
					weights_2dArray[1][3],
					weights_2dArray[0][0],
					weights_2dArray[0][1],
					weights_2dArray[0][2],
					weights_2dArray[0][3]]



		Legs=[0]*24
		for i in range(0,3):
			Legs[i]=Part.LineSegment(fp.Poles[i],fp.Poles[i+1])
		for i in range(3,6):
			Legs[i]=Part.LineSegment(fp.Poles[i+1],fp.Poles[i+2])
		for i in range(6,9):
			Legs[i]=Part.LineSegment(fp.Poles[i+2],fp.Poles[i+3])
		for i in range(9,12):
			Legs[i]=Part.LineSegment(fp.Poles[i+3],fp.Poles[i+4])
		for i in range(12,16):
			Legs[i]=Part.LineSegment(fp.Poles[i-12],fp.Poles[i-8])
		for i in range(16,20):
			Legs[i]=Part.LineSegment(fp.Poles[i-12],fp.Poles[i-8])
		for i in range(20,24):
			Legs[i]=Part.LineSegment(fp.Poles[i-12],fp.Poles[i-8])
		fp.Legs=Legs
		fp.Shape = Part.Shape(fp.Legs)
		
class ControlGrid64_2Grid44:  # surfaces not strictly used as input, but this is the logical position
	def __init__(self, obj , Grid_0, Grid_1):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nControlGrid64_2Grid44 class Init\n")
		obj.addProperty("App::PropertyLink","Grid_0","ControlGrid64_2Grid44","first reference 4X4 grid").Grid_0 = Grid_0
		obj.addProperty("App::PropertyLink","Grid_1","ControlGrid64_2Grid44","second reference 4X4 grid").Grid_1 = Grid_1
		obj.addProperty("App::PropertyFloat","scale_tangent_0","ControlGrid64_2Grid44","first grid tangent scale").scale_tangent_0 = 2
		obj.addProperty("App::PropertyFloat","scale_tangent_1","ControlGrid64_2Grid44","second grid tangent scale").scale_tangent_1 = 2
		obj.addProperty("App::PropertyFloatList","scale_inner_0","ControlGrid64_2Grid44","first side inner scale").scale_inner_0 = [3, 3, 3, 3]
		obj.addProperty("App::PropertyFloatList","scale_inner_1","ControlGrid64_2Grid44","second side inner scale").scale_inner_1 = [3, 3, 3, 3]
		obj.addProperty("Part::PropertyGeometryList","Legs","ControlGrid64_2Grid44","control segments").Legs
		obj.addProperty("App::PropertyVectorList","Poles","ControlGrid64_2Grid44","Poles").Poles
		obj.addProperty("App::PropertyFloatList","Weights","ControlGrid64_2Grid44","Weights").Weights
		obj.Proxy = self

	def execute(self, fp):
		'''Do something when doing a recomputation, this method is mandatory'''
		# this is the monolithic version. This deserves a future breakdown:
		# -find seam points
		# -rotate grids to match uv flow
		# -extract and line up grid rows in pairs
		# -blend: upgrade, stitch, scale
		# -stack each blend poly back into a grid
		
		# extract corner points
		corners_0=[fp.Grid_0.Poles[0],fp.Grid_0.Poles[3],fp.Grid_0.Poles[15],fp.Grid_0.Poles[12]]
		corners_1=[fp.Grid_1.Poles[0],fp.Grid_1.Poles[3],fp.Grid_1.Poles[15],fp.Grid_1.Poles[12]]
		# find the seam
		seam_index = [0]*2
		found = 0
		for i in range(0,4):
			for j in range(0,4):
				if equalVectors(corners_0[i],corners_1[j],0.000001):
					seam_index[found]=[i,j]
					found=found+1
					
		# rotate the grids so that the seam is on the right side for Grid_0 and the left side for Grid_1
		# in the ideal case, no rotation is required:
		# seam_index[0]=[1,0], and
		# seam_index[1]=[2,3]
		# to rotate each grid individually, split seam_index data into one set for each grid
		seam_0 = [seam_index[0][0],seam_index[1][0]]
		seam_1 = [seam_index[0][1],seam_index[1][1]]
		
		# left grid correction rotation
		if seam_0 == [1,2]:
			rotate_0 = 0
		if seam_0 == [2,3]:
			rotate_0 = 1 
		if seam_0 == [0,3]:
			rotate_0 = 2 
		if seam_0 == [0,1]:
			rotate_0 = 3 
		
		print 'seam_0 ', seam_0
		print 'seam_1 ', seam_1
		
		# right grid correction rotation		
		if seam_1 == [0,3] or seam_1 == [3,0]:
			rotate_1 = 0 # times 90 degrees clockwise
		if seam_1 == [0,1] or seam_1 == [1,0]:
			rotate_1 = 1 
		if seam_1 == [1,2] or seam_1 == [2,1]:
			rotate_1 = 2 
		if seam_1 == [3,2] or seam_1 == [2,3]:
			rotate_1 = 3 
						
		print 'rotate left: ', rotate_0
		print 'rotate right: ', rotate_1
		
		# get grid data back into array
		lin_poles_0 = fp.Grid_0.Poles
		lin_weights_0 = fp.Grid_0.Weights
		
		lin_poles_1 = fp.Grid_1.Poles
		lin_weights_1 = fp.Grid_1.Weights

		# first shot: simple partition.this is an array of rows
		poles_0 = [[lin_poles_0[0], lin_poles_0[1], lin_poles_0[2], lin_poles_0[3]],
					[lin_poles_0[4], lin_poles_0[5], lin_poles_0[6], lin_poles_0[7]],
					[lin_poles_0[8], lin_poles_0[9], lin_poles_0[10], lin_poles_0[11]],
					[lin_poles_0[12], lin_poles_0[13], lin_poles_0[14], lin_poles_0[15]]]
		
		weights_0 = [[lin_weights_0[0], lin_weights_0[1], lin_weights_0[2], lin_weights_0[3]],
					[lin_weights_0[4], lin_weights_0[5], lin_weights_0[6], lin_weights_0[7]],
					[lin_weights_0[8], lin_weights_0[9], lin_weights_0[10], lin_weights_0[11]],
					[lin_weights_0[12], lin_weights_0[13], lin_weights_0[14], lin_weights_0[15]]]		
		
		poles_1 = [[lin_poles_1[0], lin_poles_1[1], lin_poles_1[2], lin_poles_1[3]],
					[lin_poles_1[4], lin_poles_1[5], lin_poles_1[6], lin_poles_1[7]],
					[lin_poles_1[8], lin_poles_1[9], lin_poles_1[10], lin_poles_1[11]],
					[lin_poles_1[12], lin_poles_1[13], lin_poles_1[14], lin_poles_1[15]]]
		
		weights_1 = [[lin_weights_1[0], lin_weights_1[1], lin_weights_1[2], lin_weights_1[3]],
					[lin_weights_1[4], lin_weights_1[5], lin_weights_1[6], lin_weights_1[7]],
					[lin_weights_1[8], lin_weights_1[9], lin_weights_1[10], lin_weights_1[11]],
					[lin_weights_1[12], lin_weights_1[13], lin_weights_1[14], lin_weights_1[15]]]
		
		#print 'poles_0', poles_0
		#print 'poles_1', poles_1
		
		# apply rotation correction. vector type gets stripped in numpy
		uv_poles_0_temp = np.rot90(poles_0,rotate_0).tolist()
		uv_weights_0 = np.rot90(weights_0,rotate_0).tolist()
		
		uv_poles_1_temp = np.rot90(poles_1,rotate_1).tolist()
		uv_weights_1 = np.rot90(weights_1,rotate_1).tolist()
		
		#print 'uv_poles_0_temp', uv_poles_0_temp
		#print 'uv_poles_1_temp', uv_poles_1_temp
		#print 'uv_poles_0_temp[0][0] ', uv_poles_0_temp[0][0]
		#print 'uv_poles_0_temp[3][3] ', uv_poles_0_temp[3][3]
		
		# get ready to recast to vector
		uv_poles_0 = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
		uv_poles_1 = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
		
		for i in range(0,4):
			for j in range(0,4):
				uv_poles_0[i][j]= Base.Vector(uv_poles_0_temp[i][j][0],uv_poles_0_temp[i][j][1],uv_poles_0_temp[i][j][2])
			#print uv_poles_0
			
		for i in range(0,4):
			for j in range(0,4):
				uv_poles_1[i][j]= Base.Vector(uv_poles_1_temp[i][j][0],uv_poles_1_temp[i][j][1],uv_poles_1_temp[i][j][2])
			#print uv_poles_1
			
		
		#print 'uv_poles_0', uv_poles_0
		#print 'uv_poles_1', uv_poles_1		
		
		#b=Base.Vector(a[0],a[1],a[2])
		
		# run ControlPoly6_FilletBezier or equivalent internal function on each pair runnning across the seam
		row_0 = blend_poly_2x4_1x6(uv_poles_0[0], uv_weights_0[0], uv_poles_1[0], uv_weights_1[0], fp.scale_tangent_0, fp.scale_inner_0[0], fp.scale_inner_1[0], fp.scale_tangent_1)
		blend_poles_0 = row_0[0]
		blend_weights_0 = row_0[1]
		
		row_1 = blend_poly_2x4_1x6(uv_poles_0[1], uv_weights_0[1], uv_poles_1[1], uv_weights_1[1], fp.scale_tangent_0, fp.scale_inner_0[1], fp.scale_inner_1[1], fp.scale_tangent_1)
		blend_poles_1 = row_1[0]
		blend_weights_1 = row_1[1]
		
		row_2 = blend_poly_2x4_1x6(uv_poles_0[2], uv_weights_0[2], uv_poles_1[2], uv_weights_1[2], fp.scale_tangent_0, fp.scale_inner_0[2], fp.scale_inner_1[2], fp.scale_tangent_1)
		blend_poles_2 = row_2[0]
		blend_weights_2 = row_2[1]

		row_3 = blend_poly_2x4_1x6(uv_poles_0[3], uv_weights_0[3], uv_poles_1[3], uv_weights_1[3], fp.scale_tangent_0, fp.scale_inner_0[3], fp.scale_inner_1[3], fp.scale_tangent_1)
		blend_poles_3 = row_3[0]
		blend_weights_3 = row_3[1]
		
		# stack the ControlPoly6s into a 64 grid - poles and weights
		fp.Poles=[blend_poles_0[0],
				blend_poles_0[1],
				blend_poles_0[2],
				blend_poles_0[3],
				blend_poles_0[4],
				blend_poles_0[5],
				blend_poles_1[0],
				blend_poles_1[1],
				blend_poles_1[2],
				blend_poles_1[3],
				blend_poles_1[4],
				blend_poles_1[5],
				blend_poles_2[0],
				blend_poles_2[1],
				blend_poles_2[2],
				blend_poles_2[3],
				blend_poles_2[4],
				blend_poles_2[5],
				blend_poles_3[0],
				blend_poles_3[1],
				blend_poles_3[2],
				blend_poles_3[3],
				blend_poles_3[4],
				blend_poles_3[5]]	

		fp.Weights=[blend_weights_0[0],
				blend_weights_0[1],
				blend_weights_0[2],
				blend_weights_0[3],
				blend_weights_0[4],
				blend_weights_0[5],
				blend_weights_1[0],
				blend_weights_1[1],
				blend_weights_1[2],
				blend_weights_1[3],
				blend_weights_1[4],
				blend_weights_1[5],
				blend_weights_2[0],
				blend_weights_2[1],
				blend_weights_2[2],
				blend_weights_2[3],
				blend_weights_2[4],
				blend_weights_2[5],
				blend_weights_3[0],
				blend_weights_3[1],
				blend_weights_3[2],
				blend_weights_3[3],
				blend_weights_3[4],
				blend_weights_3[5]]	
	
		# build the leg list for viz		
		Legs=[0]*38
		for i in range(0,5):
			Legs[i]=Part.LineSegment(fp.Poles[i],fp.Poles[i+1])
		for i in range(5,10):
			Legs[i]=Part.LineSegment(fp.Poles[i+1],fp.Poles[i+2])
		for i in range(10,15):
			Legs[i]=Part.LineSegment(fp.Poles[i+2],fp.Poles[i+3])
		for i in range(15,20):
			Legs[i]=Part.LineSegment(fp.Poles[i+3],fp.Poles[i+4])

		for i in range(20,26):
			Legs[i]=Part.LineSegment(fp.Poles[i-20],fp.Poles[i-14])
		for i in range(26,32):
			Legs[i]=Part.LineSegment(fp.Poles[i-20],fp.Poles[i-14])
		for i in range(32,38):
			Legs[i]=Part.LineSegment(fp.Poles[i-20],fp.Poles[i-14])
		fp.Legs=Legs
		fp.Shape = Part.Shape(fp.Legs)

class SubGrid33_2Grid64s_old:
	def __init__(self, obj , Grid_0, Grid_1):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nSubGrid33_2Grid64s class Init\n")
		obj.addProperty("App::PropertyLink","Grid_0","SubGrid33_2Grid64s","first reference 6X4 grid").Grid_0 = Grid_0
		obj.addProperty("App::PropertyLink","Grid_1","SubGrid33_2Grid64s","second reference 6X4 grid").Grid_1 = Grid_1
		obj.addProperty("Part::PropertyGeometryList","Legs","SubGrid33_2Grid64s","control segments").Legs
		obj.addProperty("App::PropertyVectorList","u_row0_poles","SubGrid33_2Grid64s","u_row0_poles").u_row0_poles
		obj.addProperty("App::PropertyVectorList","u_row1_poles","SubGrid33_2Grid64s","u_row1_poles").u_row1_poles		
		obj.addProperty("App::PropertyVectorList","v_col0_poles","SubGrid33_2Grid64s","v_col0_poles").v_col0_poles
		obj.addProperty("App::PropertyVectorList","v_col1_poles","SubGrid33_2Grid64s","v_col1_poles").v_col1_poles		
		obj.addProperty("App::PropertyFloatList","u_row0_weights","SubGrid33_2Grid64s","u_row0_weights").u_row0_weights
		obj.addProperty("App::PropertyFloatList","u_row1_weights","SubGrid33_2Grid64s","u_row1_weights").u_row1_weights		
		obj.addProperty("App::PropertyFloatList","v_col0_weights","SubGrid33_2Grid64s","v_col0_weights").v_col0_weights
		obj.addProperty("App::PropertyFloatList","v_col1_weights","SubGrid33_2Grid64s","v_col1_weights").v_col1_weights		
		obj.Proxy = self


	def execute(self, fp):
		'''Do something when doing a recomputation, this method is mandatory'''
		# outline:
		# -find shared corner
		# -set 'u' row - imagine the future surface as uvn (n is normal). 
		# -set 'v' row - imagine the future surface as uvn (n is normal).
		# -build a corner focused 33 grid using the same logic as the corner focused 66 grid. 
		# the $10 question here is whether this even maintains G1? maybe...it has been many steps since the bezier surface was segmented.
		
		# extract corner points
		corners_0=[fp.Grid_0.Poles[0],fp.Grid_0.Poles[5],fp.Grid_0.Poles[18],fp.Grid_0.Poles[23]]
		corners_1=[fp.Grid_1.Poles[0],fp.Grid_1.Poles[5],fp.Grid_1.Poles[18],fp.Grid_1.Poles[23]]
		# find the common point
		common = 'not_found_yet'
		for i in range(0,4):
			for j in range(0,4):
				if corners_0[i] == corners_1[j]:
					common=[i,j]

		if common == 'not_found_yet':
			print 'common point of grids not found. If this object was working, this is an evaluation error'
		#print 'common ', common
		# tested-runs-
		
		# the two '6s' fo each grid should form a V when looking at the future grid
		# a is the left leg of the V, i.e. common[0] = 0 or 3
		# b is the right leg of the V i.e. common[1] = 2 or 1
		
		# check input grid order, swap grids if necessary
		if (common[0] == 1 or common[0] == 2) and (common[1] == 0 or common[1] == 3):
			print 'swapping grid order'
			temp=fp.Grid_0
			fp.Grid_0=fp.Grid_1
			fp.Grid_1=temp
			# get the corners again
			corners_0=[fp.Grid_0.Poles[0],fp.Grid_0.Poles[5],fp.Grid_0.Poles[18],fp.Grid_0.Poles[23]]
			corners_1=[fp.Grid_1.Poles[0],fp.Grid_1.Poles[5],fp.Grid_1.Poles[18],fp.Grid_1.Poles[23]]
			# find common again
			for i in range(0,4):
				for j in range(0,4):
					if corners_0[i] == corners_1[j]:
						common=[i,j]
			print 'common ', common
		
		if common[0] == 0:
			fp.u_row0_poles = [fp.Grid_0.Poles[0],fp.Grid_0.Poles[1],fp.Grid_0.Poles[2]]
			fp.u_row0_weights = [fp.Grid_0.Weights[0],fp.Grid_0.Weights[1],fp.Grid_0.Weights[2]]
			fp.u_row1_poles = [fp.Grid_0.Poles[6],fp.Grid_0.Poles[7],fp.Grid_0.Poles[8]]
			fp.u_row1_weights = [fp.Grid_0.Weights[6],fp.Grid_0.Weights[7],fp.Grid_0.Weights[8]]			
		
		if common[0] == 3:
			fp.u_row0_poles = [fp.Grid_0.Poles[23],fp.Grid_0.Poles[22],fp.Grid_0.Poles[21]]
			fp.u_row0_weights = [fp.Grid_0.Weights[23],fp.Grid_0.Weights[22],fp.Grid_0.Weights[21]]
			fp.u_row1_poles = [fp.Grid_0.Poles[17],fp.Grid_0.Poles[16],fp.Grid_0.Poles[15]]
			fp.u_row1_weights = [fp.Grid_0.Weights[17],fp.Grid_0.Weights[16],fp.Grid_0.Weights[15]]					
		
		if common[1] == 1:
			fp.v_col0_poles = [fp.Grid_1.Poles[5],fp.Grid_1.Poles[4],fp.Grid_1.Poles[3]]
			fp.v_col0_weights = [fp.Grid_1.Weights[5],fp.Grid_1.Weights[4],fp.Grid_1.Weights[3]]
			fp.v_col1_poles = [fp.Grid_1.Poles[11],fp.Grid_1.Poles[10],fp.Grid_1.Poles[9]]
			fp.v_col1_weights = [fp.Grid_1.Weights[11],fp.Grid_1.Weights[10],fp.Grid_1.Weights[9]]					
			
		if common[1] == 2:
			fp.v_col0_poles = [fp.Grid_1.Poles[18],fp.Grid_1.Poles[19],fp.Grid_1.Poles[20]]
			fp.v_col0_weights = [fp.Grid_1.Weights[18],fp.Grid_1.Weights[19],fp.Grid_1.Weights[20]]
			fp.v_col1_poles = [fp.Grid_1.Poles[12],fp.Grid_1.Poles[13],fp.Grid_1.Poles[14]]
			fp.v_col1_weights = [fp.Grid_1.Weights[12],fp.Grid_1.Weights[13],fp.Grid_1.Weights[14]]					
			
		
		Legs=[0]*10

		Legs[0]=Part.LineSegment(fp.u_row0_poles[0], fp.u_row0_poles[1])
		Legs[1]=Part.LineSegment(fp.u_row0_poles[1], fp.u_row0_poles[2])
		
		Legs[2]=Part.LineSegment(fp.u_row0_poles[0], fp.u_row1_poles[0])
		Legs[3]=Part.LineSegment(fp.u_row0_poles[1], fp.u_row1_poles[1])
		Legs[4]=Part.LineSegment(fp.u_row0_poles[2], fp.u_row1_poles[2])
		
		Legs[5]=Part.LineSegment(fp.v_col0_poles[0], fp.v_col0_poles[1])
		Legs[6]=Part.LineSegment(fp.v_col0_poles[1], fp.v_col0_poles[2])

		Legs[7]=Part.LineSegment(fp.v_col0_poles[0], fp.v_col1_poles[0])
		Legs[8]=Part.LineSegment(fp.v_col0_poles[1], fp.v_col1_poles[1])
		Legs[9]=Part.LineSegment(fp.v_col0_poles[2], fp.v_col1_poles[2])

		fp.Legs=Legs
		fp.Shape = Part.Shape(fp.Legs)

class SubGrid33_2Grid64s:
	def __init__(self, obj , Grid_0, Grid_1):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nSubGrid33_2Grid64s class Init\n")
		obj.addProperty("App::PropertyLink","Grid_0","SubGrid33_2Grid64s","first reference 6X4 grid").Grid_0 = Grid_0
		obj.addProperty("App::PropertyLink","Grid_1","SubGrid33_2Grid64s","second reference 6X4 grid").Grid_1 = Grid_1
		obj.addProperty("App::PropertyFloat","adjust_0","SubGrid33_2Grid64s","adjust along Grid_0").adjust_0 = 0
		obj.addProperty("App::PropertyFloat","adjust_1","SubGrid33_2Grid64s","adjust along Grid_1").adjust_1 = 0
		obj.addProperty("Part::PropertyGeometryList","Legs","SubGrid33_2Grid64s","control segments").Legs
		obj.addProperty("App::PropertyVectorList","Poles","SubGrid33_2Grid64s","Poles").Poles
		obj.addProperty("App::PropertyFloatList","Weights","SubGrid33_2Grid64s","Weights").Weights
	
		obj.Proxy = self

	def execute(self, fp):
		'''Do something when doing a recomputation, this method is mandatory'''
		# outline:
		# -find shared corner
		# -set 'u' row - imagine the future surface as uvn (n is normal). 
		# -set 'v' row - imagine the future surface as uvn (n is normal).
		# -build a corner focused 33 grid using similar logic as the corner focused 66 grid. 
		#the $10 question here is whether this even maintains G1? maybe...it has been many steps since the bezier surface was segmented.
		
		# extract corner points
		corners_0=[fp.Grid_0.Poles[0],fp.Grid_0.Poles[5],fp.Grid_0.Poles[18],fp.Grid_0.Poles[23]]
		corners_1=[fp.Grid_1.Poles[0],fp.Grid_1.Poles[5],fp.Grid_1.Poles[18],fp.Grid_1.Poles[23]]
		# find the common point
		common = 'not_found_yet'
		for i in range(0,4):
			for j in range(0,4):
				if equalVectors(corners_0[i],corners_1[j],0.000001):
					common=[i,j]
		if common == 'not_found_yet':
			print 'common point of grids not found. If this object was working previously, this is an evaluation error'
		print 'common ', common
		# tested-runs-
		
		# the two 6 point sides of each grid should form a V when looking at the future grid
		# a is the left leg of the V, i.e. common[0] = 0 or 3
		# b is the right leg of the V i.e. common[1] = 2 or 1
		
		# check input grid order, swap grids if necessary
		if (common[0] == 1 or common[0] == 2) and (common[1] == 0 or common[1] == 3):
			print 'swapping grid order'
			temp=fp.Grid_0
			fp.Grid_0=fp.Grid_1
			fp.Grid_1=temp
			# get the corners again
			corners_0=[fp.Grid_0.Poles[0],fp.Grid_0.Poles[5],fp.Grid_0.Poles[18],fp.Grid_0.Poles[23]]
			corners_1=[fp.Grid_1.Poles[0],fp.Grid_1.Poles[5],fp.Grid_1.Poles[18],fp.Grid_1.Poles[23]]
			# find common again
			for i in range(0,4):
				for j in range(0,4):
					if equalVectors(corners_0[i],corners_1[j],0.000001):
						common=[i,j]
			print 'common ', common
		
		if common[0] == 0:
			v_col0_poles = [fp.Grid_0.Poles[0],fp.Grid_0.Poles[1],fp.Grid_0.Poles[2]]
			v_col0_weights = [fp.Grid_0.Weights[0],fp.Grid_0.Weights[1],fp.Grid_0.Weights[2]]
			v_col1_poles = [fp.Grid_0.Poles[6],fp.Grid_0.Poles[7],fp.Grid_0.Poles[8]]
			v_col1_weights = [fp.Grid_0.Weights[6],fp.Grid_0.Weights[7],fp.Grid_0.Weights[8]]			
		
		if common[0] == 3:
			v_col0_poles = [fp.Grid_0.Poles[23],fp.Grid_0.Poles[22],fp.Grid_0.Poles[21]]
			v_col0_weights = [fp.Grid_0.Weights[23],fp.Grid_0.Weights[22],fp.Grid_0.Weights[21]]
			v_col1_poles = [fp.Grid_0.Poles[17],fp.Grid_0.Poles[16],fp.Grid_0.Poles[15]]
			v_col1_weights = [fp.Grid_0.Weights[17],fp.Grid_0.Weights[16],fp.Grid_0.Weights[15]]					
		
		if common[1] == 1:
			u_row0_poles = [fp.Grid_1.Poles[5],fp.Grid_1.Poles[4],fp.Grid_1.Poles[3]]
			u_row0_weights = [fp.Grid_1.Weights[5],fp.Grid_1.Weights[4],fp.Grid_1.Weights[3]]
			u_row1_poles = [fp.Grid_1.Poles[11],fp.Grid_1.Poles[10],fp.Grid_1.Poles[9]]
			u_row1_weights = [fp.Grid_1.Weights[11],fp.Grid_1.Weights[10],fp.Grid_1.Weights[9]]					
			
		if common[1] == 2:
			u_row0_poles = [fp.Grid_1.Poles[18],fp.Grid_1.Poles[19],fp.Grid_1.Poles[20]]
			u_row0_weights = [fp.Grid_1.Weights[18],fp.Grid_1.Weights[19],fp.Grid_1.Weights[20]]
			u_row1_poles = [fp.Grid_1.Poles[12],fp.Grid_1.Poles[13],fp.Grid_1.Poles[14]]
			u_row1_weights = [fp.Grid_1.Weights[12],fp.Grid_1.Weights[13],fp.Grid_1.Weights[14]]					
			
		u_tan_ratio = (u_row0_poles[1]-u_row0_poles[0]).Length / (v_col1_poles[0]-v_col0_poles[0]).Length
		v_tan_ratio = (v_col0_poles[1]-v_col0_poles[0]).Length / (u_row1_poles[0]-u_row0_poles[0]).Length
		
		p00 = u_row0_poles[0]
		p01 = u_row0_poles[1]
		p02 = u_row0_poles[2]		
		p10 = v_col0_poles[1]
		p20 = v_col0_poles[2]
		p11_u = p01 + (u_row0_poles[1]-u_row1_poles[1])*v_tan_ratio
		p12 = p02 + (u_row0_poles[2]-u_row1_poles[2])*v_tan_ratio
		p11_v = p10 + (v_col0_poles[1]-v_col1_poles[1])*u_tan_ratio
		p21 = p20 + (v_col0_poles[2]-v_col1_poles[2])*u_tan_ratio	
		p11 = (p11_u + p11_v) * 0.5
		p22_u = p12 + (p21-p11)
		p22_v = p21 + (p12-p11)		
		p22_temp = (p22_u + p22_v) * 0.5
		
		p22 = p22_temp + fp.adjust_0 * (p01-p00) + fp.adjust_1 * (p10-p00)
		
		fp.Poles = [p00, p01, p02, p10, p11, p12, p20, p21, p22]
		
		w00 = u_row0_weights[0]
		w01 = u_row0_weights[1]
		w02 = u_row0_weights[2]		
		w10 = v_col0_weights[1]
		w20 = v_col0_weights[2]		
		
		w11 = w01 * w10
		w12 = w02 * w10
		w21 = w01 * w20
		w22 = w02 * w20
		
		fp.Weights = [w00, w01, w02, w10, w11, w12, w20, w21, w22]
		
		Legs=[0]*12
		
		Legs[0]=Part.LineSegment(p00,p01)
		Legs[1]=Part.LineSegment(p01,p02)
		
		Legs[2]=Part.LineSegment(p00,p10)
		Legs[3]=Part.LineSegment(p10,p20)
		
		Legs[4]=Part.LineSegment(p01,p11)
		Legs[5]=Part.LineSegment(p02,p12)
		
		Legs[6]=Part.LineSegment(p10,p11)
		Legs[7]=Part.LineSegment(p20,p21)
		
		Legs[8]=Part.LineSegment(p11,p12)
		Legs[9]=Part.LineSegment(p11,p21)

		Legs[10]=Part.LineSegment(p12,p22)
		Legs[11]=Part.LineSegment(p21,p22)
		
		fp.Legs=Legs
		fp.Shape = Part.Shape(fp.Legs)
		
class ControlGrid66_4Subs_old:
	def __init__(self, obj , SubGrid_0, SubGrid_1, SubGrid_2, SubGrid_3):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nControlGrid66_4Subs class Init\n")
		obj.addProperty("App::PropertyLink","SubGrid_0","ControlGrid66_4Subs","first reference 3X3 sub grid").SubGrid_0 = SubGrid_0
		obj.addProperty("App::PropertyLink","SubGrid_1","ControlGrid66_4Subs","second reference 3X3 sub grid").SubGrid_1 = SubGrid_1
		obj.addProperty("App::PropertyLink","SubGrid_2","ControlGrid66_4Subs","third reference 3X3 sub grid").SubGrid_2 = SubGrid_2	
		obj.addProperty("App::PropertyLink","SubGrid_3","ControlGrid66_4Subs","fourth reference 3X3 sub grid").SubGrid_3 = SubGrid_3		
		obj.addProperty("Part::PropertyGeometryList","Legs","ControlGrid66_4Subs","control segments").Legs
		obj.addProperty("App::PropertyVectorList","Poles","ControlGrid66_4Subs","Poles").Poles
		obj.addProperty("App::PropertyFloatList","Weights","ControlGrid66_4Subs","Weights").Weights
		obj.Proxy = self

	def execute(self, fp):
		'''Do something when doing a recomputation, this method is mandatory'''
		p00 = fp.SubGrid_0.u_row_poles[0]
		p01 = fp.SubGrid_0.u_row_poles[1]
		p02 = fp.SubGrid_0.u_row_poles[2]
		p03 = fp.SubGrid_1.v_col_poles[2]
		p04 = fp.SubGrid_1.v_col_poles[1]
		p05 = fp.SubGrid_1.v_col_poles[0]
		
		p15 = fp.SubGrid_1.u_row_poles[1]
		p25 = fp.SubGrid_1.u_row_poles[2]
		p35 = fp.SubGrid_2.v_col_poles[2]
		p45 = fp.SubGrid_2.v_col_poles[1]
		p55 = fp.SubGrid_2.v_col_poles[0]
		
		p54 = fp.SubGrid_2.u_row_poles[1]
		p53 = fp.SubGrid_2.u_row_poles[2]
		p52 = fp.SubGrid_3.v_col_poles[2]
		p51 = fp.SubGrid_3.v_col_poles[1]
		p50 = fp.SubGrid_3.v_col_poles[0]
		
		p40 = fp.SubGrid_3.u_row_poles[1]
		p30 = fp.SubGrid_3.u_row_poles[2]
		p20 = fp.SubGrid_0.v_col_poles[2]
		p10 = fp.SubGrid_0.v_col_poles[1]
		
		p11 = p01 + (p10 - p00)
		p14 = p04 + (p15 - p05)
		p41 = p51 + (p40 - p50)
		p44 = p45 + (p54 - p55)
		p12 = p02 + (p10 - p00)
		p13 = p03 + (p15 - p05)	
		p24 = p25 + (p04 - p05)
		p34 = p35 + (p54 - p55)	
		p42 = p52 + (p40 - p50)
		p43 = p53 + (p45 - p55)
		p21 = p20 + (p01 - p00)
		p31 = p30 + (p51 - p50)
		p22 = p12 + (p20 - p10)
		p23 = p13 + (p25 - p15)
		p32 = p42 + (p30 - p40)
		p33 = p43 + (p35 - p45)
		fp.Poles = [p00, p01, p02, p03, p04, p05,
					p10, p11, p12, p13, p14, p15,
					p20, p21, p22, p23, p24, p25,
					p30, p31, p32, p33, p34, p35,
					p40, p41, p42, p43, p44, p45,
					p50, p51, p52, p53, p54, p55]
		w00 = fp.SubGrid_0.u_row_weights[0]
		w01 = fp.SubGrid_0.u_row_weights[1]
		w02 = fp.SubGrid_0.u_row_weights[2]
		w03 = fp.SubGrid_1.v_col_weights[2]
		w04 = fp.SubGrid_1.v_col_weights[1]
		w05 = fp.SubGrid_1.v_col_weights[0]
		w15 = fp.SubGrid_1.u_row_weights[1]
		w25 = fp.SubGrid_1.u_row_weights[2]
		w35 = fp.SubGrid_2.v_col_weights[2]
		w45 = fp.SubGrid_2.v_col_weights[1]
		w55 = fp.SubGrid_2.v_col_weights[0]
		w54 = fp.SubGrid_2.u_row_weights[1]
		w53 = fp.SubGrid_2.u_row_weights[2]
		w52 = fp.SubGrid_3.v_col_weights[2]
		w51 = fp.SubGrid_3.v_col_weights[1]
		w50 = fp.SubGrid_3.v_col_weights[0]
		w40 = fp.SubGrid_3.u_row_weights[1]
		w30 = fp.SubGrid_3.u_row_weights[2]
		w20 = fp.SubGrid_0.v_col_weights[2]
		w10 = fp.SubGrid_0.v_col_weights[1]
		# maybe i should average instead of multiply? needs testing.
		# currently based on the idea all wights are between 0 and 1.
		# previous used cumulative neighbor mulitplication. this drives weights too low.
		# current method multiplies the two weights along isos to the closest edge
		w11 = w01*w10
		w12 = w02*w10 
		w21 = w01*w20
		w22 = w02*w20
		w14 = w04*w15
		w13 = w03*w15
		w24 = w04*w25
		w23 = w03*w25
		w44 = w45*w54
		w34 = w35*w54
		w43 = w54*w45
		w33 = w35*w53
		w41 = w40*w51
		w31 = w30*w51
		w42 = w52*w40
		w32 = w30*w52

		fp.Weights = [w00, w01, w02, w03, w04, w05,
					w10, w11, w12, w13, w14, w15,
					w20, w21, w22, w23, w24, w25,
					w30, w31, w32, w33, w34, w35,
					w40, w41, w42, w43, w44, w45,
					w50, w51, w52, w53, w54, w55]
		Legs=[0]*60
		for i in range(0,5):
			Legs[i]=Part.LineSegment(fp.Poles[i],fp.Poles[i+1])
		for i in range(5,10):
			Legs[i]=Part.LineSegment(fp.Poles[i+1],fp.Poles[i+2])
		for i in range(10,15):
			Legs[i]=Part.LineSegment(fp.Poles[i+2],fp.Poles[i+3])
		for i in range(15,20):
			Legs[i]=Part.LineSegment(fp.Poles[i+3],fp.Poles[i+4])
		for i in range(20,25):
			Legs[i]=Part.LineSegment(fp.Poles[i+4],fp.Poles[i+5])
		for i in range(25,30):
			Legs[i]=Part.LineSegment(fp.Poles[i+5],fp.Poles[i+6])	
		for i in range(30,36):
			Legs[i]=Part.LineSegment(fp.Poles[i-30],fp.Poles[i-24])
		for i in range(36,42):
			Legs[i]=Part.LineSegment(fp.Poles[i-30],fp.Poles[i-24])
		for i in range(42,48):
			Legs[i]=Part.LineSegment(fp.Poles[i-30],fp.Poles[i-24])
		for i in range(48,54):
			Legs[i]=Part.LineSegment(fp.Poles[i-30],fp.Poles[i-24])
		for i in range(54,60):
			Legs[i]=Part.LineSegment(fp.Poles[i-30],fp.Poles[i-24])
		
		fp.Legs=Legs
		fp.Shape = Part.Shape(fp.Legs)

class ControlGrid66_4Subs:
	def __init__(self, obj , SubGrid_0, SubGrid_1, SubGrid_2, SubGrid_3):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nControlGrid66_4Subs class Init\n")
		obj.addProperty("App::PropertyLink","SubGrid_0","ControlGrid66_4Subs","first reference 3X3 sub grid").SubGrid_0 = SubGrid_0
		obj.addProperty("App::PropertyLink","SubGrid_1","ControlGrid66_4Subs","second reference 3X3 sub grid").SubGrid_1 = SubGrid_1
		obj.addProperty("App::PropertyLink","SubGrid_2","ControlGrid66_4Subs","third reference 3X3 sub grid").SubGrid_2 = SubGrid_2	
		obj.addProperty("App::PropertyLink","SubGrid_3","ControlGrid66_4Subs","fourth reference 3X3 sub grid").SubGrid_3 = SubGrid_3		
		obj.addProperty("Part::PropertyGeometryList","Legs","ControlGrid66_4Subs","control segments").Legs
		obj.addProperty("App::PropertyVectorList","Poles","ControlGrid66_4Subs","Poles").Poles
		obj.addProperty("App::PropertyFloatList","Weights","ControlGrid66_4Subs","Weights").Weights
		obj.Proxy = self

	def execute(self, fp):
		'''Do something when doing a recomputation, this method is mandatory'''
		p00 = fp.SubGrid_0.Poles[0]
		p01 = fp.SubGrid_0.Poles[1]
		p02 = fp.SubGrid_0.Poles[2]
		p03 = fp.SubGrid_1.Poles[6]
		p04 = fp.SubGrid_1.Poles[3]
		p05 = fp.SubGrid_1.Poles[0]
		
		p15 = fp.SubGrid_1.Poles[1]
		p25 = fp.SubGrid_1.Poles[2]
		p35 = fp.SubGrid_2.Poles[6]
		p45 = fp.SubGrid_2.Poles[3]
		p55 = fp.SubGrid_2.Poles[0]
		
		p54 = fp.SubGrid_2.Poles[1]
		p53 = fp.SubGrid_2.Poles[2]
		p52 = fp.SubGrid_3.Poles[6]
		p51 = fp.SubGrid_3.Poles[3]
		p50 = fp.SubGrid_3.Poles[0]
		
		p40 = fp.SubGrid_3.Poles[1]
		p30 = fp.SubGrid_3.Poles[2]
		p20 = fp.SubGrid_0.Poles[6]
		p10 = fp.SubGrid_0.Poles[3]
		
		p11 = fp.SubGrid_0.Poles[4]
		p12 = fp.SubGrid_0.Poles[5]
		p13 = fp.SubGrid_1.Poles[7]
		p14 = fp.SubGrid_1.Poles[4]

		p24 = fp.SubGrid_1.Poles[5]
		p34 = fp.SubGrid_2.Poles[7]
		p44 = fp.SubGrid_2.Poles[4]
		
		p43 = fp.SubGrid_2.Poles[5]		
		p42 = fp.SubGrid_3.Poles[7]
		p41 = fp.SubGrid_3.Poles[4]

		p31 = fp.SubGrid_3.Poles[5]
		p21 = fp.SubGrid_0.Poles[7]

		p22 = fp.SubGrid_0.Poles[8]
		p23 = fp.SubGrid_1.Poles[8]
		p33 = fp.SubGrid_2.Poles[8]
		p32 = fp.SubGrid_3.Poles[8]

		fp.Poles = [p00, p01, p02, p03, p04, p05,
					p10, p11, p12, p13, p14, p15,
					p20, p21, p22, p23, p24, p25,
					p30, p31, p32, p33, p34, p35,
					p40, p41, p42, p43, p44, p45,
					p50, p51, p52, p53, p54, p55]
					
		w00 = fp.SubGrid_0.Weights[0]
		w01 = fp.SubGrid_0.Weights[1]
		w02 = fp.SubGrid_0.Weights[2]
		w03 = fp.SubGrid_1.Weights[6]
		w04 = fp.SubGrid_1.Weights[3]
		w05 = fp.SubGrid_1.Weights[0]
		
		w15 = fp.SubGrid_1.Weights[1]
		w25 = fp.SubGrid_1.Weights[2]
		w35 = fp.SubGrid_2.Weights[6]
		w45 = fp.SubGrid_2.Weights[3]
		w55 = fp.SubGrid_2.Weights[0]
		
		w54 = fp.SubGrid_2.Weights[1]
		w53 = fp.SubGrid_2.Weights[2]
		w52 = fp.SubGrid_3.Weights[6]
		w51 = fp.SubGrid_3.Weights[3]
		w50 = fp.SubGrid_3.Weights[0]
		
		w40 = fp.SubGrid_3.Weights[1]
		w30 = fp.SubGrid_3.Weights[2]
		w20 = fp.SubGrid_0.Weights[6]
		w10 = fp.SubGrid_0.Weights[3]
		
		w11 = fp.SubGrid_0.Weights[4]
		w12 = fp.SubGrid_0.Weights[5]
		w13 = fp.SubGrid_1.Weights[7]
		w14 = fp.SubGrid_1.Weights[4]

		w24 = fp.SubGrid_1.Weights[5]
		w34 = fp.SubGrid_2.Weights[7]
		w44 = fp.SubGrid_2.Weights[4]
		
		w43 = fp.SubGrid_2.Weights[5]		
		w42 = fp.SubGrid_3.Weights[7]
		w41 = fp.SubGrid_3.Weights[4]

		w31 = fp.SubGrid_3.Weights[5]
		w21 = fp.SubGrid_0.Weights[7]

		w22 = fp.SubGrid_0.Weights[8]
		w23 = fp.SubGrid_1.Weights[8]
		w33 = fp.SubGrid_2.Weights[8]
		w32 = fp.SubGrid_3.Weights[8]

		fp.Weights = [w00, w01, w02, w03, w04, w05,
					w10, w11, w12, w13, w14, w15,
					w20, w21, w22, w23, w24, w25,
					w30, w31, w32, w33, w34, w35,
					w40, w41, w42, w43, w44, w45,
					w50, w51, w52, w53, w54, w55]
		Legs=[0]*60
		for i in range(0,5):
			Legs[i]=Part.LineSegment(fp.Poles[i],fp.Poles[i+1])
		for i in range(5,10):
			Legs[i]=Part.LineSegment(fp.Poles[i+1],fp.Poles[i+2])
		for i in range(10,15):
			Legs[i]=Part.LineSegment(fp.Poles[i+2],fp.Poles[i+3])
		for i in range(15,20):
			Legs[i]=Part.LineSegment(fp.Poles[i+3],fp.Poles[i+4])
		for i in range(20,25):
			Legs[i]=Part.LineSegment(fp.Poles[i+4],fp.Poles[i+5])
		for i in range(25,30):
			Legs[i]=Part.LineSegment(fp.Poles[i+5],fp.Poles[i+6])	
		for i in range(30,36):
			Legs[i]=Part.LineSegment(fp.Poles[i-30],fp.Poles[i-24])
		for i in range(36,42):
			Legs[i]=Part.LineSegment(fp.Poles[i-30],fp.Poles[i-24])
		for i in range(42,48):
			Legs[i]=Part.LineSegment(fp.Poles[i-30],fp.Poles[i-24])
		for i in range(48,54):
			Legs[i]=Part.LineSegment(fp.Poles[i-30],fp.Poles[i-24])
		for i in range(54,60):
			Legs[i]=Part.LineSegment(fp.Poles[i-30],fp.Poles[i-24])
		
		fp.Legs=Legs
		fp.Shape = Part.Shape(fp.Legs)

class SubGrid62Tri_2Surf64s:
	def __init__(self, obj , NL_Surf_0, NL_Surf_1):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nSubGrid62Tri_2Surf64s class Init\n")
		obj.addProperty("App::PropertyLink","NL_Surf_0","SubGrid62Tri_2Surf64s","first reference 6X4 surface").NL_Surf_0 = NL_Surf_0
		obj.addProperty("App::PropertyLink","NL_Surf_1","SubGrid62Tri_2Surf64s","second reference 6X4 surface").NL_Surf_1 = NL_Surf_1
		obj.addProperty("Part::PropertyGeometryList","Legs","SubGrid62Tri_2Surf64s","control segments").Legs
		obj.addProperty("App::PropertyVectorList","Poles","SubGrid62Tri_2Surf64s","Poles").Poles
		obj.addProperty("App::PropertyFloatList","Weights","SubGrid62Tri_2Surf64s","Weights").Weights
	
		obj.Proxy = self

	def execute(self, fp):
		'''Do something when doing a recomputation, this method is mandatory'''
		# outline:
		# -find shared corner
		# -set 'u' row - imagine the future surface as uvn (n is normal). 
		# -set 'v' row - imagine the future surface as uvn (n is normal).
		# -build a corner focused 33 grid using similar logic as the corner focused 66 grid.
		#the $10 question here is whether this even maintains G1? maybe...it has been many steps since the bezier surface was segmented.
		
		# get grids form the surfaces
		Grid_0=fp.NL_Surf_0.Grid
		Grid_1=fp.NL_Surf_1.Grid
		
		#get the FreeCAD surface form the NL surface object
		
		Surf_0 = fp.NL_Surf_0.Shape.Surface
		Surf_1 = fp.NL_Surf_1.Shape.Surface
		
		
		# extract corner points
		corners_0=[fp.Grid_0.Poles[0],fp.Grid_0.Poles[5],fp.Grid_0.Poles[18],fp.Grid_0.Poles[23]]
		corners_1=[fp.Grid_1.Poles[0],fp.Grid_1.Poles[5],fp.Grid_1.Poles[18],fp.Grid_1.Poles[23]]
		# find the common point
		common = 'not_found_yet'
		for i in range(0,4):
			for j in range(0,4):
				if corners_0[i] == corners_1[j]:
					common=[i,j]
		if common == 'not_found_yet':
			print 'common point of grids not found. If this object was working previously, this is an evaluation error'
		print 'common ', common
		# tested-runs-
		
		# the two 6 point sides of each grid should form a V when looking at the future grid
		# a is the left leg of the V, i.e. common[0] = 0 or 3
		# b is the right leg of the V i.e. common[1] = 2 or 1
		
		# check input grid order, swap grids if necessary
		if (common[0] == 1 or common[0] == 2) and (common[1] == 0 or common[1] == 3):
			print 'swapping grid order'
			temp=fp.Grid_0
			fp.Grid_0=fp.Grid_1
			fp.Grid_1=temp
			# get the corners again
			corners_0=[fp.Grid_0.Poles[0],fp.Grid_0.Poles[5],fp.Grid_0.Poles[18],fp.Grid_0.Poles[23]]
			corners_1=[fp.Grid_1.Poles[0],fp.Grid_1.Poles[5],fp.Grid_1.Poles[18],fp.Grid_1.Poles[23]]
			# find common again
			for i in range(0,4):
				for j in range(0,4):
					if corners_0[i] == corners_1[j]:
						common=[i,j]
			print 'common ', common
		
		if common[0] == 0:
			v_col0_poles = [fp.Grid_0.Poles[0],fp.Grid_0.Poles[1],fp.Grid_0.Poles[2]]
			v_col0_weights = [fp.Grid_0.Weights[0],fp.Grid_0.Weights[1],fp.Grid_0.Weights[2]]
			v_col1_poles = [fp.Grid_0.Poles[6],fp.Grid_0.Poles[7],fp.Grid_0.Poles[8]]
			v_col1_weights = [fp.Grid_0.Weights[6],fp.Grid_0.Weights[7],fp.Grid_0.Weights[8]]			
		
		if common[0] == 3:
			v_col0_poles = [fp.Grid_0.Poles[23],fp.Grid_0.Poles[22],fp.Grid_0.Poles[21]]
			v_col0_weights = [fp.Grid_0.Weights[23],fp.Grid_0.Weights[22],fp.Grid_0.Weights[21]]
			v_col1_poles = [fp.Grid_0.Poles[17],fp.Grid_0.Poles[16],fp.Grid_0.Poles[15]]
			v_col1_weights = [fp.Grid_0.Weights[17],fp.Grid_0.Weights[16],fp.Grid_0.Weights[15]]					
		
		if common[1] == 1:
			u_row0_poles = [fp.Grid_1.Poles[5],fp.Grid_1.Poles[4],fp.Grid_1.Poles[3]]
			u_row0_weights = [fp.Grid_1.Weights[5],fp.Grid_1.Weights[4],fp.Grid_1.Weights[3]]
			u_row1_poles = [fp.Grid_1.Poles[11],fp.Grid_1.Poles[10],fp.Grid_1.Poles[9]]
			u_row1_weights = [fp.Grid_1.Weights[11],fp.Grid_1.Weights[10],fp.Grid_1.Weights[9]]					
			
		if common[1] == 2:
			u_row0_poles = [fp.Grid_1.Poles[18],fp.Grid_1.Poles[19],fp.Grid_1.Poles[20]]
			u_row0_weights = [fp.Grid_1.Weights[18],fp.Grid_1.Weights[19],fp.Grid_1.Weights[20]]
			u_row1_poles = [fp.Grid_1.Poles[12],fp.Grid_1.Poles[13],fp.Grid_1.Poles[14]]
			u_row1_weights = [fp.Grid_1.Weights[12],fp.Grid_1.Weights[13],fp.Grid_1.Weights[14]]					
			
		u_tan_ratio = (u_row0_poles[1]-u_row0_poles[0]).Length / (v_col1_poles[0]-v_col0_poles[0]).Length
		v_tan_ratio = (v_col0_poles[1]-v_col0_poles[0]).Length / (u_row1_poles[0]-u_row0_poles[0]).Length
		
		p00 = u_row0_poles[0]
		p01 = u_row0_poles[1]
		p02 = u_row0_poles[2]		
		p10 = v_col0_poles[1]
		p20 = v_col0_poles[2]
		p11_u = p01 + (u_row0_poles[1]-u_row1_poles[1])*v_tan_ratio
		p12 = p02 + (u_row0_poles[2]-u_row1_poles[2])*v_tan_ratio
		p11_v = p10 + (v_col0_poles[1]-v_col1_poles[1])*u_tan_ratio
		p21 = p20 + (v_col0_poles[2]-v_col1_poles[2])*u_tan_ratio	
		p11 = (p11_u + p11_v) * 0.5
		p22_u = p12 + (p21-p11)
		p22_v = p21 + (p12-p11)		
		p22_temp = (p22_u + p22_v) * 0.5
		
		p22 = p22_temp + fp.adjust_0 * (p01-p00) + fp.adjust_1 * (p10-p00)
		
		fp.Poles = [p00, p01, p02, p10, p11, p12, p20, p21, p22]
		
		w00 = u_row0_weights[0]
		w01 = u_row0_weights[1]
		w02 = u_row0_weights[2]		
		w10 = v_col0_weights[1]
		w20 = v_col0_weights[2]		
		
		w11 = w01 * w10
		w12 = w02 * w10
		w21 = w01 * w20
		w22 = w02 * w20
		
		fp.Weights = [w00, w01, w02, w10, w11, w12, w20, w21, w22]
		
		Legs=[0]*12
		
		Legs[0]=Part.LineSegment(p00,p01)
		Legs[1]=Part.LineSegment(p01,p02)
		
		Legs[2]=Part.LineSegment(p00,p10)
		Legs[3]=Part.LineSegment(p10,p20)
		
		Legs[4]=Part.LineSegment(p01,p11)
		Legs[5]=Part.LineSegment(p02,p12)
		
		Legs[6]=Part.LineSegment(p10,p11)
		Legs[7]=Part.LineSegment(p20,p21)
		
		Legs[8]=Part.LineSegment(p11,p12)
		Legs[9]=Part.LineSegment(p11,p21)

		Legs[10]=Part.LineSegment(p12,p22)
		Legs[11]=Part.LineSegment(p21,p22)
		
		fp.Legs=Legs
		fp.Shape = Part.Shape(fp.Legs)
			
class ControlGrid64_3_Grid44:
	def __init__(self, obj , ControlGrid44, Corner):
		''' Add the properties '''
		FreeCAD.Console.PrintMessage("\nControlGrid64_3_Grid44 class Init\n")
		obj.addProperty("App::PropertyLink","ControlGrid44","ControlGrid64_3_Grid44","Reference Bezier Surface").ControlGrid44 = ControlGrid44
		obj.addProperty("App::PropertyFloat","Corner","ControlGrid64_3_Grid44","Corner blending curve").Corner = Corner
		obj.addProperty("Part::PropertyGeometryList","Legs","ControlGrid64_3_Grid44","control segments").Legs
		obj.addProperty("App::PropertyVectorList","Poles","ControlGrid64_3_Grid44","Poles").Poles
		obj.addProperty("App::PropertyFloatList","Weights","ControlGrid64_3_Grid44","Weights").Weights
		obj.Proxy = self

	def execute(self, fp):
		'''Do something when doing a recomputation, this method is mandatory'''
		# get the control poly of the bezier
		grid_44 = fp.ControlGrid44
		# get the target corner
		corner = fp.Corner
		
		if corner == 0:
			rotate = 0
		elif corner == 1:
			rotate = 1
		elif corner == 2:
			rotate = 2			
		elif corner == 3:
			rotate = 3
			
		# rotate the grid so that the corner is in the 00 position
				# get grid data back into array
		lin_poles = grid_44.Poles
		lin_weights = grid_44.Weights
		
		# first shot: simple partition.this is an array of rows
		Apoles = [[lin_poles[0], lin_poles[1], lin_poles[2], lin_poles[3]],
					[lin_poles[4], lin_poles[5], lin_poles[6], lin_poles[7]],
					[lin_poles[8], lin_poles[9], lin_poles[10], lin_poles[11]],
					[lin_poles[12], lin_poles[13], lin_poles[14], lin_poles[15]]]
		
		Aweights = [[lin_weights[0], lin_weights[1], lin_weights[2], lin_weights[3]],
					[lin_weights[4], lin_weights[5], lin_weights[6], lin_weights[7]],
					[lin_weights[8], lin_weights[9], lin_weights[10], lin_weights[11]],
					[lin_weights[12], lin_weights[13], lin_weights[14], lin_weights[15]]]		
		
		#print 'Apoles', Apoles
		
		# apply rotation correction. vector type gets stripped in numpy
		uv_poles_temp = np.rot90(Apoles,rotate).tolist()
		uv_weights = np.rot90(Aweights,rotate).tolist()

		#print 'uv_poles_temp', uv_poles_temp
		#print 'uv_poles_temp[0][0] ', uv_poles_temp[0][0]
		#print 'uv_poles_temp[3][3] ', uv_poles_temp[3][3]
		
		# get ready to recast to vector
		uv_poles = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
		
		for i in range(0,4):
			for j in range(0,4):
				uv_poles[i][j]= Base.Vector(uv_poles_temp[i][j][0],uv_poles_temp[i][j][1],uv_poles_temp[i][j][2])
			#print uv_poles
		
		#print 'uv_poles', uv_poles
		
		set_poles = [ uv_poles[0][0],
		uv_poles[0][1],
		uv_poles[0][2],
		uv_poles[0][3],
		uv_poles[1][0],
		uv_poles[1][1],
		uv_poles[1][2],
		uv_poles[1][3],
		uv_poles[2][0],
		uv_poles[2][1],
		uv_poles[2][2],
		uv_poles[2][3],
		uv_poles[3][0],
		uv_poles[3][1],
		uv_poles[3][2],
		uv_poles[3][3]]
		
		set_weights = [ uv_weights[0][0],
		uv_weights[0][1],
		uv_weights[0][2],
		uv_weights[0][3],
		uv_weights[1][0],
		uv_weights[1][1],
		uv_weights[1][2],
		uv_weights[1][3],
		uv_weights[2][0],
		uv_weights[2][1],
		uv_weights[2][2],
		uv_weights[2][3],
		uv_weights[3][0],
		uv_weights[3][1],
		uv_weights[3][2],
		uv_weights[3][3]]
		
		
		#first degenerate topology try. naive Grid44 to Grid64 triangle mapping with some midpoints. p22=p23=p24=p25=set_poles[10]. this causes folding.
		#second iteration: add tiny spacing around p22, p23, p24, p25. this will break G1 slightly. The goal is to balance G1 loss versus folding over.
		#as these point 'un-degenerate' it is tempting to reintroduce curvature matching. On the other hand, aligning them for 0 curvature may help get G1 back.
		#maybe some weighted average of these various avenues will be best.
		p00=set_poles[12]
		p01=set_poles[8]
		p02=set_poles[4]
		p03=set_poles[1]
		p04=set_poles[2]
		p05=set_poles[3]
		
		p10=set_poles[13]
		p11=set_poles[9]
		
		p14=set_poles[6]
		p15=set_poles[7]
		

		p20=set_poles[14]
		''' # 1st strategy		
		p21=set_poles[10]
		p22=set_poles[10]
		p23=set_poles[10]
		p24=set_poles[10]
		'''
		p25=set_poles[11]
		
		
		# 2nd strategy
		''' this was better, sure, but it stills folds. going to set the whole corner planar, but non collapsed for third try.
		degen_tan_factor=0.5 #initial was 0.75
		degen_curv_factor=1.0/6.0 #initial was 0.1
		#trim tangent
		p21=p20+(set_poles[10]-p20)*degen_tan_factor
		# add a segment control line snippet towards the third control point of the underlying 44 grid
		p22=p21+(p14-p21)*degen_curv_factor
		#trim tangent
		p24=p25+(set_poles[10]-p25)*degen_tan_factor
		# add a segment control line snippet towards the third control point of the underlying 44 grid		
		p23=p24+(p11-p24)*degen_curv_factor
		'''
		
		#third strategy
		p21=p20+(set_poles[10]-p20)*.5 # trim tangent
		p22=p21+(set_poles[10]-p21)*.5 # 0 curvature along tangent trim
		
		p24=p25+(set_poles[10]-p25)*.5 # trim tangent
		p23=p24+(set_poles[10]-p24)*.5 # 0 curvature along tangent trim
		
				
		p30=set_poles[15]
		p31=set_poles[15]
		p32=set_poles[15]
		p33=set_poles[15]
		p34=set_poles[15]
		p35=set_poles[15]
		
		p12=(set_poles[5]+p11).multiply(0.5)
		p13=(set_poles[5]+p14).multiply(0.5)
					
		
		fp.Poles = [p00, p01, p02, p03, p04, p05,
					p10, p11, p12, p13, p14, p15,
					p20, p21, p22, p23, p24, p25,
					p30, p31, p32, p33, p34, p35]

		w00=set_weights[12]
		w01=set_weights[8]
		w02=set_weights[4]
		w03=set_weights[1]
		w04=set_weights[2]
		w05=set_weights[3]
		
		w10=set_weights[13]
		w11=set_weights[9]
		
		w14=set_weights[6]
		w15=set_weights[7]
		
		w20=set_weights[14]
		w21=set_weights[10]
		w22=set_weights[10]
		w23=set_weights[10]
		w24=set_weights[10]
		w25=set_weights[11]
		
		w30=set_weights[15]
		w31=set_weights[15]
		w32=set_weights[15]
		w33=set_weights[15]
		w34=set_weights[15]
		w35=set_weights[15]
		
		w12=(w02+w21)/2
		w13=(w03+w24)/2
					
		fp.Weights = [w00, w01, w02, w03, w04, w05,
					w10, w11, w12, w13, w14, w15,
					w20, w21, w22, w23, w24, w25,
					w30, w31, w32, w33, w34, w35]
		Legs=[0]*33 # last used Legs index below + 1
		
		#rows
		for i in range(0,5):
			Legs[i]=Part.LineSegment(fp.Poles[i],fp.Poles[i+1])
		#Legs[0,1,2,3,4] used	
		for i in range(6,11):
			Legs[i-1]=Part.LineSegment(fp.Poles[i],fp.Poles[i+1])
		#Legs[5,6,7,8,9] used
		for i in range(12,17):
			Legs[i-2]=Part.LineSegment(fp.Poles[i],fp.Poles[i+1])
		#Legs[10,11,12,13,14] used
		#skip top row
		
		#columns
		for i in range(0,6):
			Legs[i+15]=Part.LineSegment(fp.Poles[i],fp.Poles[i+6])
		#Legs[15,16,17,18,19,20] used	
		for i in range(6,12):
			Legs[i+15]=Part.LineSegment(fp.Poles[i],fp.Poles[i+6])
		#Legs[21,22,23,24,25,26] used
		for i in range(12,18):
			Legs[i+15]=Part.LineSegment(fp.Poles[i],fp.Poles[i+6])
		#Legs[27,28,29,30,31,32] used
		
		
		
		
		fp.Legs=Legs
		fp.Shape = Part.Shape(fp.Legs)
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
