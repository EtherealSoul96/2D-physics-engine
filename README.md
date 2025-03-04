# 2D-physics-engine. Feb 2021 - Dec 2022

Rigid body dynamics, collision detection, collision response, triangulation

This program handles collision detection and rigid body dynamics of objects made out of segments and convex and concave arcs, which allow very complex 2D shapes.
Given a shape, it also triangulates it in order to calculate its mass and moment of inertia and to draw the inside of the object.

The collision detection is done using two sorted lists that store the position of the vertices for each axis, this allows the program to know when the "hitboxes" of two object parts (segments and arcs) collide, when they do it then checks if they are actually colliding by using custom functions depending on the types of parts they are (for example a segment with a convex arc).

But certainly the trickiest part of this program was the collision response. I wanted the engine to be very versatile, so after thinking for multiple days I came up with a formula / algorithm that handles the collision of two objects considering their mass, moment of inertia, velocity, angular momentum, location of impact, angle of the line of collision, static and dynamic friction, and coefficient of restitution.
The strength of this formula is that it's general enough to handle the response of any collision regadless of all those parameters.
