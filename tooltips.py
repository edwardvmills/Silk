'''
This file compiles all the tooltips for the respective command files as string variables. By displaying 
the tooltips in command progression order, The goal is to allow building background knowledge, in 
addition to command usage mechanics.

For each command, a 'tooltip' and 'More Info' string variable is prepared.


STRING FORMAT
\n for line returns
" reserved as string delimeter (begin/end each line)
' allowed freely within strings

this line of underscore characters seems to succeed in setting window width, and preventing the popup window from wrapping text unexpectedly.
	"______________________________________________________________________________________________________________________________________ \n"
text cannot reach the end of this line, or it will wrap. see below for reasonable setbacks. Any edit must be tested by opening FreeCAD,
checking the tooltip, and clicking the icon to verify popup formatting, and no unintentional line wraps.
    
'''

standardTipFooter = (
	"\n     Click this icon with nothing selected to see more information \n"
)


ControlPoly4_baseTip = (
	"Creates a ControlPoly4 from a variety of alternative inputs: \n"
	"______________________________________________________________________________________________________________________________________ \n"
	"Usage \n"
	"ALL SKETCHES USED MUST BE FROM THE SKETCHER WORKBENCH \n"
	"\n"
	"Preselect one of the following: \n"
	"\n"
	" • One sketch of three lines connected end to end \n"
	" • Two sketches containing a circle and a line each, where one of the line endpoints matches the center of the circle. \n"
	"   These 'Node Sketches' use the circle center to indicate an endpoint, and the line to indicate the desired tangent \n"
	"   direction from that endpoint. \n"
	" • If a single sketch is selected that does not contain three elements, the first element is converted. This works for \n"
	"   line, arc of circle, and arc of ellipse elements. Arcs should be quarter circle or less. \n"
    "\n"
	"Apply the function \n"
	"\n"
	"This control polygon (poly) of 4 points is intended to control a cubic bezier curve, or to control a cubic bezier surface. \n"
	"After creating the poly, you'll probably want to hide the sketches used to create it, so that you can see it. Creating \n"
    "these objects often feels like an 'extra' step, but they need to be fully understood in order to progress in NURBS."
	"\n"
	"Used as input for: \n"
	" • CubicCurve_4 (which is a smooth Bezier curve)\n"
	" • ControlGrid44 (which then produces a smooth Bezier surface)\n"
	" • ControlGrid44_Rotate (which then produces a smooth Bezier surface) \n"
	" • ControlGrid64 (which then produces a less smooth mixed Bezier/NURBS surface)\n"
	)

ControlPoly4_moreInfo = (
	"______________________________________________________________________________________________________________________________________ \n"
	"More Info \n"
	"\n"
	"This is THE most important tool, and everything else depends on it. Give it a quick try, use the result as input for the \n"
	"next tool (CubicCurve_4) and then come back to read more about it. \n"
	"Editing the source sketches will automatically update the poly. Curves and surfaces attached to the poly will update as \n"
	"well. In your sketches, make sure to set the view property 'hide dependents' to 'false'. This will give you live updates of \n"
	"polys (and curves, and surfaces) while you edit the sketches. \n"
	"Since polys are used to create surfaces as well as curves, and surfaces are what we are really after, the poly creation is \n"
	"kept as a independent step. It is important to develop a feel for how a poly controls a curve. After you have created a curve/ \n"
	"surface, edit the sketches you used to create the poly and observe how the curve/surface changes. \n"
	"Node sketches are intended to be placed in different planes, so that the resulting resulting polys, curves, and surface \n"
	"edges are fully 3D. they are great to connect to endpoints of 3 line sketches that are on different planes. Node sketches are \n"
	"typically created witht circle at the origin, and the sketch mapped to a new location and orientation using FreeCAD's Mapping \n"
	"tools (found under the data tab of the property view). In this manner, the circle is never edited, and the free endpoint of \n"
	"the line can be freely adjusted. \n"
	"A poly that is used in a grid/surface can relinked to a different sketch(es), so all the work of making the grid/surface does \n"
	"not need to be redone. Just swap the link to another sketch and recompute (sketch links are also found under the data tab of \n"
	"the property view).\n"
	)



CubicCurve_4_baseTip = (
	"Creates a CubicCurve_4 from a ControlPoly4. \n"
	"______________________________________________________________________________________________________________________________________ \n"
	"Usage \n"
    "\n"
	"Preselect one of the following: \n"
	"\n"
    " • one ControlPoly4 \n"
    " • one ControlPoly4_segment. \n"
    "\n"
	"Apply the function \n"
	"\n"
    "This a Bezier cubic curve. All editing is done by editing the ControlPoly4 \n"
	"The main purpose of creating curves is to preview what the edges of our surface will look like if we use the input poly in a \n"
    "control grid (curves themselves are not used directly to make surfaces, but they can share polys with them). Curves are also used\n"
    "by cutting them into segments, which in turn define how to cut surfaces for blending \n"
	"\n"
	"Used as input for: \n"
	"• Point_onCurve (which can be a marker to subdivide the curve with ControlPoly4_Segment) \n"
	"• Two CubicCurve_4 that touch at one end can be used to generate a blend poly with the ControlPoly6 tool (not a beginner topic). \n"
)

CubicCurve_4_moreInfo = (
    "______________________________________________________________________________________________________________________________________ \n"
    "More Info \n"
    "\n"
    "This a Bezier cubic curve. A NURBS is Bezier when the number of control points is equal to the degree + 1. So a cubic (degree \n"
    " 3), has 4 control points. Beziers are the smoothest, highest quality NURBS. However, it is very difficult to connect several of \n"
    "them in a satisfying manner. It is relatively easy to obtain tangency (G1) by aligning certain control points, but difficult to \n"
    "obtain curvature matching (G2) as this involves adjusting multiple control points at the same time. G3 is very difficult, but \n"
    "even worse, it is pointless. In the attempt to smooth out the join of two beziers to G3, we have to move the control points \n"
    "around, to the point where one or both of the curves/surfaces become completely unrecognizable. \n"
    "\n"
    "So why use beziers? Well, they are still the best for individual curves/surfaces. Sometimes G1 is fine, so they can be used \n"
    "directly. Forhigher quality stuff, Silk's design strategy is to use multiple Beziers for the broad strokes of the design, let \n"
    "them meet at sharp angles on a shared edge, and finally trim back and blend. This is not a new crazy idea, the most expensive \n"
    "surfacing software for industrial design uses the same strategy: Bezier as far as they'll take you, and then careful blending\n"
    " of the edges/joints (Silk does not attempt to emulate those programs entirely, this just one common point). \n"
    "\n"
    "Silk currently only works with cubics, but the plan is to move to degree 4 (5 control points), 5 (6 control points), etc in \n"
    "the course of development. Silk still needs a few more functions before we can say 'cubics are done!' and move on the higher \n"
    "degrees. When the higher degrees are introduced, the cubics will still remain the 'bread and potatoes' of design. The higher \n"
    "degrees will only be used when absolutely necessary, as they are harder to use anyways (someone has to define all these extra \n"
    "control points...)"
)

Point_onCurve_baseTip = (
    "Create a point on a Cubic_Curve4 or Cubic_Curve6 (also works on some curves outside of Silk).\n"
    "______________________________________________________________________________________________________________________________________ \n"
	"Usage \n"
    "\n"
	"Preselect the following: \n"
    "\n"
	" • Choose a location on the curve in the 3D view by clicking on it. \n"
	"\n"
	"Apply the function \n"
	"\n"
    "A pointOnCurve object is placed on the curve. \n"
    "\n"
	"Used as input for: \n"
	"• Start point and end point of ControlPoly4_Segment (used to cut CubicCurve4s into pieces) \n"
	"• Can be a convenient way to mark a location along a curve, and then place (map) a Node sketch (or whatever you want) at that \n"
	"  location using the Mapping tool under property data tab \n"
	)
            
Point_onCurve_moreInfo = (
    "______________________________________________________________________________________________________________________________________ \n"
    "More Info \n"
    "\n"
    "This works on curves outside of Silk, as long as they are parametrized as '0 to 1'. Allowing any number works in principle, but \n"
    "Silk would then suffer every time a user types in '100' by greatly distoring the model. So Silk is prioritized over other curves."
    "\n"
    "The position of the point can be adjusted along the curve (0.0 to 1.0) by adjusting the 'u'parameter found under the data tab\n"
    " of the property view. This allows precise positioning anywhere along the curve. It is often not obvious which side is 0, and \n"
    "which side is 1. Try to pick clearly towards one end or the other of the curve, it will then be obvious if the point is closer\n"
	" to 0 or 1. To match the endpoints, type in 0 or 1. Try to keep u values generally consistent (.25, .5, .75, etc, or 0.1, 0.2, \n"
    "0.3, 0.4, etc). This is because we will often have to match cut values in different curves/surfaces to line things up. Discipline \n"
    "up front and recognizing your typical values will pay off. \n"
    "Often, two curves we wish to split 'in the same manner' have their orientation reversed to each other. In those cases, set u of \n"
    "the 'next' curve to 1-u (eg. .90 and .10) of the 'previous' curve in to cut them in the 'same place'\n"
    "\n"
    "FreeCAD's expression engine allows us to easily connect one cut value to another existing cut value. The you only need to edit \n"
    "one, and all others follow it automatically.\n"
    "\n"
    "Given curve1, curve2, with point1, point 2 on them, set \n"
    " • u of point2 = point1.u (typing '=' in a data field of the property data view creates an expression)\n"
    "now any changes to point1.u will be automatically propagated to point2.u\n"
    "If the points appear on the wrong side of the curve, set \n"
    " • u of point2 = 1 - point1.u (in the expression) \n"
    "\n"
    "Automatic matching is not really optional on large models, but you don't need to worry about it until you have a large model. \n"
    "You don't have to type much: select the source point in the tree, hit F2 (edit label mode), hit control-C (copy the label), go \n"
    "to the property data view of the point you want to apply the match to, in the 'u' field, hit '=' (expression opens), then \n"
    "control-V (paste), then type '.u', confirm by clicking 'u' in the drop down, hit 'enter'. This works all over FreeCAD. \n"
	)
			
ControlPoly4_segment_baseTip = (
	"Create a ControlPoly4 on a segment of a Cubic_Curve, between two points on the curve. \n"
    "______________________________________________________________________________________________________________________________________ \n"
	"Usage \n"
    "\n"
    "Preselect the following sequence: \n"
    " • the curve first \n"
    " • a point on the curve. \n"
    " • another point on the curve \n"
    "(the points must be pointOnCurve objects) \n"
    "(this selection is best done in the model tree, as selecting points in 3D is extremely difficult and unreliable). \n"
    "\n"
	"Apply the function \n"
	"\n"
    "A simple interpretation of the selection is: 'this curve, but only from this point, to this other point'. \n"
    "\n"
	"Input for: \n"
	" • CubicCurve_4 (makes a new curve, which is a  segment of the original curve), which can in turn be used as input for \n"
	"  ControlGrid44_EdgeSegment, ControlGrid44_2EdgeSegments, and/or ControlPoly6 \n"
	" • ControlGrid44 (atypical use, but it functions just as any poly 4) \n"
	" • ControlGrid64 (atypical use, but it functions just as any poly 4) \n"
	)
            
ControlPoly4_segment_moreInfo = (
	"______________________________________________________________________________________________________________________________________ \n"
    "More Info \n"
    "\n"
    "Segmenting/sectioning/cutting is a core Silk modeling technique. It is essential for blending. The current workflow uses curve \n"
    "segments as references to cut surfaces. There are plans to cut surfaces by drawing points directly on them, but since the same \n"
    "result is already possible using curve segments, implementation is not high on priorities (unfortunately).\n"
    "\n"
	"Why so much segmenting in Silk? segments of curves, then segment of surfaces...so much time segmenting and aligning  \n"
    "segmentation points! So many points. Why? Because if you build off of segments/pieces of a single Bezier curve or surface, \n"
    "the things you build retain 'relatedness' to each other. They blend well. Sections separated by gaps nevertheless feel as \n"
    "part of the same surface. This instant feeling of connectedness is almost impossible to achieve by tring to 'harmonize' \n"
    "two curves or surfaces constructed separately and then mushed together. The key to Silk blending is sharing edges between \n"
    "base surfaces (which are not otherwise aligned), and then blending strips of the surfaces near that shared edge. The shared \n"
    "edges and strips make blends that come out decent even before tuning. \n"
	)


ControlGrid44_baseTip = (
	"Create a ControlGrid44 from four connected ControlPoly4 edges. \n"
    "______________________________________________________________________________________________________________________________________ \n"
	"Usage \n"
    "\n"	
    "Prepare the following selection: \n"
    " • four ControlPoly4 objects that form a loop \n"
    " • the ControlPoly4s should only touch at their endpoints, and form a distinct angle where they meet \n"
	" • Select each edge in the loop sequentially, counter clock-wise looking from the 'outer side' of the surface we want to create. \n"
	"\n"
	"Apply the function \n"
    "\n"
	"Input for: \n"
	"• CubicSurface_44 (makes a smooth cubic Bezier surface)\n"
	"• ControlGrid64_2Grid44 (makes a blend grid to join surfaces)\n"
    )
    
ControlGrid44_moreInfo = (
	"______________________________________________________________________________________________________________________________________ \n"
    "More Info \n"
    "\n"
    "Silk does it's first useful task beyond using existing FreeCAD functions and forcing us to use a strange format: it generates \n"
    "inner control points of the grid based on the polys. This is not the only way to generate the inner control points, but it is \n"
    "a great default starting point. The user provides 12 points through the polys, and Silk provides 4 more. It doesn't seem much, \n"
    "but it snowballs from here, and the rest of the tools will generate dozens and hundreds of useful control points with less and \n"
    "less input fron the user at each step. \n"
	"\n"
    "TANGENCY RULES \n"
	"If you don't intend to segment and blend adjacent CubicSurface_4s, then their ControlGrid44s must follow strict \n"
	"rules to get tangency (G1) across the shared edge: \n"
	" • There must be a shared edge (G0). The entire edge. This is done by selecting the same poly for that edge in both \n"
	"   grids. Do not trace the poly. Do not approximate it, do not copy, do not link. Use the same object during both \n"
	"   grid creations. \n"
	" • The legs of the polys that meet on the shared edge must be COLINEAR (/aligned/parallel). \n"
	" • The RATIO of the length of the poly legs that meet on the shared edge must be EQUAL. So if the top poly on the left \n"
	"   has a last leg of length 3, and meets a leg of length 1 of top of the right grid, the tangency ratio is 3:1 from left \n"
    "   grid to right grid. Now if the bottom poly on the left grid has a last leg of length 6, the connecting poly on the right \n"
    "   grid must have a first leg of length 2 (keeping it 3:1). This ratio rule goes away if all poly legs are parallel across the \n"
    "   shared edge.\n"
	" • Users do not need to do anything except prepare the polys. if the polys follow these rules, the generated adjacent \n"
	"   grids will always be G1, as Silk calculates all the internal control points of the surface (the ones not on edges). \n"
	"\n"
    "Following tangency rules forces us to modify our polys, which changes our entire surfaces. when we don't want to modify a \n"
    "surface, we blend it instead of aligning it. Aligning is useful to patch small holes, or to connect to planes, cylinders \n"
    "and spheres \n"
    "\n"
	"OPTIONAL - FLAWED -  use with caution \n"
	"select 3 connected ControlPoly4 edges to produce a 'triangle' grid, which will yield a surface of low quality. \n"
	"\n"
	"The 'triangle' will have a degenerate (collapsed) edge between the first and third selected polys, because internally this grid \n"
    "has just as many points and lines as a four sided grid. The lines and points which are collapsed cause visible defects in the \n"
    "surface. This also makes further operations with this grid, or surfaces that use this grid, difficult or even impossible. This \n"
    "'triangle' does respect tangency rules, and will connect cleanly to other grids, despite its inner flaw point. In fact, the \n"
    "feature that it conforms to G1 on the edges makes it particularly flawed and ugly on the inside. Removing it is being \n"
    "considered, but some users seem to want it despite the warnings, so it remains.\n"
	)


ControlGrid44_Rotate_baseTip = (
	"Creates a ControlGrid44 from three ControlPoly4 edges. \n"
	"______________________________________________________________________________________________________________________________________ \n"
    "Usage \n"
    "\n"	
    "Prepare the following selection: \n"
    " • three ControlPoly4 objects that form a loop \n"
    " • the ControlPoly4s should only touch at their endpoints, and form a distinct angle where they meet \n"
	" • Select each edge in the loop sequentially, counter clock-wise looking from the 'outer side' of the surface we want to create. \n"
	"\n"
	"Apply the function \n"
    "\n"
	"Used to produce a 'triangle' surface which 'rotates' from the first edge selected to the third edge following along the second \n"
    "edge. Order is 'left, bottom, right' with the rotational pivot at the 'top' corner.\n"
	"\n"
	"Typical use is to merge a set of surfaces to a point (like closing a tube). Also used to interface with spheres and ellipsoids. \n"
	"\n"
	"Input for: \n"
	"-CubicSurface_44 \n"
	"-ControlGrid64_2Grid44 \n"
	"\n"
    )
ControlGrid44_Rotate_moreInfo = (
	"______________________________________________________________________________________________________________________________________ \n"
    "More Info \n"
    "\n"
	"This is a degenerate grid (one edge collapsed to a point) that results in a 'revolve' like surface. Will produce true spheres \n"
    "from arc polys, true ellipsoids from ellipse arc polys, but also accepts non-arc polys. \n"
	"\n"
	"Surface tangency from multiple grids can be produced automatically from well prepared arcs of circles and ellipses, but using \n"
    "general curves as input does not have an easily predictable outcome. Additional blending may be required.\n"
	"\n"
	"Although degenerate, this grid is the correct way to interface with spheres, where it does not introduce additional collapsed \n"
    "edges. \n"
    "\n"
    "A four sided version which would create true tori (and sphere strips) is planned, but not ready \n"
    )



ControlGrid44_flow_baseTip = (
	"IN DEVELOPMENT - NO FUNCTIONAL/USEFUL RESULT YET \n"
	"Create a ControlGrid44_flow from a ControlGrid44. \n"
	"______________________________________________________________________________________________________________________________________ \n"
    "Usage \n"
    "\n"
    "Select one ControlGrid44 and apply the function \n"
	"\n"
	"The output grid will have more gradual internal changes, at the cost of less predictable tangency across edges\n"
	"\n"
	"this can help untangle and puff up basic grids. Various parameters planned to control the scale of the effect, and to maintain \n"
    "specific tangencies \n"
	"\n"
	"Input for: \n"
	"-CubicSurface_44 \n"
	"-ControlGrid64_2Grid44 \n"
    )

ControlGrid44_flow_moreInfo = (
	"______________________________________________________________________________________________________________________________________ \n"
    "More Info \n"
    "\n"
    "no further information \n"
    )



CubicSurface_44_baseTip = (
	"Create a CubicSurface from a ControlGrid44. \n"
	"______________________________________________________________________________________________________________________________________ \n"
    "Usage \n"
        "\n"	
    "Prepare the following selection: \n"
    " • one ControlGrid44 of any type (made from polys, or made by segmenting)\n"
    "\n"
	"Apply the function \n"
    "\n"
    "This a Bezier cubic surface, and is intended to be the basic 'building block' surface that complex models are based on. All \n"
    "editing is done by editing the ControlGrid44. Refer to ControlGrid44 tooltip and 'More Info' section for design rules \n"
    "\n"
	"Can be used for hard edge surfacing, or manually aligned for tangency (G1). Can also be blended along hard edges with  other \n"
    "CubicSurface_44 objects (by way of CubicSurface64 objects), for high continuity (G2). \n"
    "\n"
    "Input for: \n"
	"-ControlGrid44_EdgeSegment (a 44 grid which corresponds to a 'full strip' segment of the surface)\n" 
	"-ControlGrid44_2EdgeSegments (a 44 grid which corresponds to a 'rectangular' segment of the surface) \n"
    )
    
CubicSurface_44_moreInfo = (
	"______________________________________________________________________________________________________________________________________ \n"
    "More Info \n"
    "\n"
    "This does for the ControlGrid44 object what the CubicCurve_4 does for the ControlPoly4. Refer to the extensive description \n"
    "given for CubicCurve_4. Those comments apply here to the surface, instead of just a curve. \n"
    "\n"
    "ControlGrid44s that are manually built from poly4s are almost exclusively intended to be used by surfaces, but many automatically \n"
    "created ControlGrid44s are intended to be consumed by blend grids. Becsue of these different possible paths, the creation of \n"
    "grids is kept separate from the creation of surfaces. That way, a useful grid is not locked inside a surface, and harder to \n"
    "access by other operations. \n"
    )

'''

ControlGrid44_EdgeSegment_baseTip = (

	"______________________________________________________________________________________________________________________________________ \n"
    "Usage \n"
    "\n"   
    )
    
_moreInfo = (
	"______________________________________________________________________________________________________________________________________ \n"
    "More Info \n"
    "\n"
    
    )
ControlGrid44_2EdgeSegments_baseTip = (

	"______________________________________________________________________________________________________________________________________ \n"
    "Usage \n"
    "\n"
    
    )
    
_moreInfo = (
	"______________________________________________________________________________________________________________________________________ \n"
    "More Info \n"
    "\n"
    
    )
ControlPoly6_baseTip = (

	"______________________________________________________________________________________________________________________________________ \n"
    "Usage \n"
    "\n"    
    )
    
_moreInfo = (
	"______________________________________________________________________________________________________________________________________ \n"
    "More Info \n"
    "\n"
    
    )
CubicCurve_6_baseTip = (

	"______________________________________________________________________________________________________________________________________ \n"
    "Usage \n"
    "\n"
        
    )
    
_moreInfo = (
	"______________________________________________________________________________________________________________________________________ \n"
    "More Info \n"
    "\n"
    
    )
ControlGrid66_baseTip = (

	"______________________________________________________________________________________________________________________________________ \n"
    "Usage \n"
    "\n"
        
    )
    
_moreInfo = (
	"______________________________________________________________________________________________________________________________________ \n"
    "More Info \n"
    "\n"
    
    )
CubicSurface_66_baseTip = (

	"______________________________________________________________________________________________________________________________________ \n"
    "Usage \n"
    "\n"
        
    )
    
_moreInfo = (
	"______________________________________________________________________________________________________________________________________ \n"
    "More Info \n"
    "\n"
    
    )
ControlGrid64_baseTip = (

	"______________________________________________________________________________________________________________________________________ \n"
    "Usage \n"
    "\n"
        
    )
    
_moreInfo = (
	"______________________________________________________________________________________________________________________________________ \n"
    "More Info \n"
    "\n"
    
    )
CubicSurface_64_baseTip = (

	"______________________________________________________________________________________________________________________________________ \n"
    "Usage \n"
    "\n"
        
    )
    
_moreInfo = (
	"______________________________________________________________________________________________________________________________________ \n"
    "More Info \n"
    "\n"
    
    )
ControlGrid64_2Grid44_baseTip = (

	"______________________________________________________________________________________________________________________________________ \n"
    "Usage \n"
    "\n"
        
    )
    
_moreInfo = (
	"______________________________________________________________________________________________________________________________________ \n"
    "More Info \n"
    "\n"
    
    )
ControlGrid64_3_1Grid44_baseTip = (

	"______________________________________________________________________________________________________________________________________ \n"
    "Usage \n"
    "\n"
        
    )
    
_moreInfo = (
	"______________________________________________________________________________________________________________________________________ \n"
    "More Info \n"
    "\n"
    
    )
SubGrid33_2Grid64_baseTip = (

	"______________________________________________________________________________________________________________________________________ \n"
    "Usage \n"
    "\n"
        
    )
    
_moreInfo = (
	"______________________________________________________________________________________________________________________________________ \n"
    "More Info \n"
    "\n"
    
    )
ControlGrid66_4Sub_baseTip = (

	"______________________________________________________________________________________________________________________________________ \n"
    "Usage \n"
    "\n"
        
    )
    
_moreInfo = (
	"______________________________________________________________________________________________________________________________________ \n"
    "More Info \n"
    "\n"
    
    )
SubGrid63_2Surf64_baseTip = (

	"______________________________________________________________________________________________________________________________________ \n"
    "Usage \n"
    "\n"
        
    )
    
_moreInfo = (
	"______________________________________________________________________________________________________________________________________ \n"
    "More Info \n"
    "\n"
    
    )
ControlGridNStar66_baseTip = (

	"______________________________________________________________________________________________________________________________________ \n"
    "Usage \n"
    "\n"
        
    )
    
_moreInfo = (
	"______________________________________________________________________________________________________________________________________ \n"
    "More Info \n"
    "\n"
    
    )
CubicNStarSurface_NStar66_baseTip = (

	"______________________________________________________________________________________________________________________________________ \n"
    "Usage \n"
    "\n"
        
    )
    
_moreInfo = (
	"______________________________________________________________________________________________________________________________________ \n"
    "More Info \n"
    "\n"
    
    )
StarTrim_CubicNStar_baseTip = (

	"______________________________________________________________________________________________________________________________________ \n"
    "Usage \n"
    "\n"
        
    )
    
_moreInfo = (
	"______________________________________________________________________________________________________________________________________ \n"
    "More Info \n"
    "\n"
    
    )
Reload_Silk_baseTip = (

	"______________________________________________________________________________________________________________________________________ \n"
    "Usage \n"
    "\n"
        
    )
    
_moreInfo = (
	"______________________________________________________________________________________________________________________________________ \n"
    "More Info \n"
    "\n"
    
    )
'''