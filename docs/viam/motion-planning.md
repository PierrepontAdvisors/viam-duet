# Motion planning

Plan and execute collision-free movements for robot arms and gantries.
> Source: https://docs.viam.com/motion-planning/


Your robot arm needs to move from one pose to another without colliding with
the table, the walls, or itself. To move safely, the planner must reason about
the arm's kinematic model, the workspace geometry, and the motion constraints
you impose.

Viam's motion service plans a collision-free path and executes it, using a
frame system you describe and obstacles you declare. You tell it where to go;
it handles the search.

This section covers motion planning for arms and gantries.

## Start here

New to Viam's motion service? Work through a short quickstart that uses
fake components so you can run it on any machine:

<div class="card-container">
  <div class="row-no-margin">
<div class="col hover-card "><a href="/motion-planning/quickstarts/first-arm/"><div ><div>Move your first arm</div><p>From zero to an arm moving under motion service control, using a fake arm that runs on any machine.</p></div>
    </a></div>

<div class="col hover-card "><a href="/motion-planning/quickstarts/frame-system/"><div ><div>Configure a frame system</div><p>Set up a table-mounted arm with a gripper and a wrist camera, and verify the frame configuration with TransformPose.</p></div>
    </a></div>

</div>
</div>

## How it works

Each `Move` request to the motion service runs the same pipeline: it reads
the [frame system](/motion-planning/frame-system/) to know where every
component sits, reads the arm's [kinematic model](/motion-planning/reference/kinematics/)
to know what joint configurations are reachable, applies any
[obstacles](/motion-planning/obstacles/) and
[constraints](/motion-planning/move-an-arm/constraints/) you declare, and
returns a collision-free path from the current pose to your target.

## Core topics

<div class="card-container">
  <div class="row-no-margin">
<div class="col hover-card "><a href="/motion-planning/frame-system/"><div ><div>Frame system</div><p>Build a unified coordinate tree so all components agree on where things are in physical space.</p></div>
    </a></div>

<div class="col hover-card "><a href="/motion-planning/obstacles/"><div ><div>Obstacles</div><p>Define collision geometry so the motion planner computes collision-free paths.</p></div>
    </a></div>

<div class="col hover-card "><a href="/visualization/3d-scene/"><div ><div>3D scene</div><p>What the 3D scene renders, where each element comes from, and how built-in configuration content differs from custom visuals a module publishes at runtime.</p></div>
    </a></div>

<div class="col hover-card "><a href="/motion-planning/move-an-arm/"><div ><div>Move an arm</div><p>Command an arm to a target pose, along a constrained path, or directly in joint space. Build pick-and-place flows from those primitives.</p></div>
    </a></div>

</div>
</div>

## Other how-tos

<div class="card-container">
  <div class="row-no-margin">
<div class="col hover-card "><a href="/motion-planning/move-gantry/"><div ><div>Move a gantry</div><p>Control gantry axes directly or plan complex gantry motion.</p></div>
    </a></div>

<div class="col hover-card "><a href="/motion-planning/verify-a-plan/"><div ><div>Verify a plan before running it</div><p>Use armplanning.PlanMotion to compute and inspect a trajectory before the arm moves, and learn how to get the same plan over the motion service API.</p></div>
    </a></div>

<div class="col hover-card "><a href="/motion-planning/debug-motion-plan/"><div ><div>Debug a motion plan</div><p>Find why a motion plan failed or moved unexpectedly by checking frames, obstacles, and reach in the 3D scene or from the Viam CLI.</p></div>
    </a></div>

</div>
</div>

## Concept pages

<div class="card-container">
  <div class="row-no-margin">
<div class="col hover-card "><a href="/motion-planning/how-planning-works/"><div ><div>How planning works</div><p>How Viam plans arm motion: the direct joint-space path it tries first, the cBiRRT fallback, and what to try when planning fails.</p></div>
    </a></div>

</div>
</div>

## Reference

<div class="card-container">
  <div class="row-no-margin">
<div class="col hover-card "><a href="/motion-planning/reference/"><div ><div>Reference</div><p>Configuration, API, and technical reference for the motion service.</p></div>
    </a></div>

</div>
</div>

