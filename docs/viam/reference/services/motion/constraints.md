# Motion constraints reference

Configure constraints to specify certain types of motion.
> Source: https://docs.viam.com/reference/services/motion/constraints/


You can constrain the motion of your machine using the motion service's built-in constraint options.
Constraints are passed as arguments to the [`Move`](/reference/apis/services/motion/#move) method.

The following constraints are available:

- [Linear constraint](#linear-constraint)
- [Orientation constraint](#orientation-constraint)
- [Next steps](#next-steps)

## Linear constraint

The linear constraint (`{"motion_profile": "linear"}`) forces the path taken by `component_name` to follow an exact linear path from the start to the goal.
If the start and goal orientations are different, the orientation along the path will follow the quaternion [Slerp (Spherical Linear Interpolation)](https://en.wikipedia.org/wiki/Slerp) of the orientation from start to goal.
This has the following sub-options:

<!-- prettier-ignore -->
| Parameter Name | Type | Default | Description |
| -------------- | ---- | ------- | ----------- |
| line_tolerance_mm | float | 0.1 | Max linear deviation from straight-line between start and goal, in mm. |
| orientation_tolerance_degs | float | 2.0 | Allowable deviation from Slerp between start/goal orientations, in degrees. |

**Example usage**:




### Python

```python
# Move a gripper with a linear constraint
moved = await motion.move(
    component_name=my_gripper,
    destination=PoseInFrame(
        reference_frame="my_frame",
        pose=goal_pose),
    world_state=worldState,
    constraints={
        Constraints(
            linear_constraint=[LinearConstraint(line_tolerance_mm=0.2)])
    },
    extra={})
```
You can find more information in the [Python SDK Docs](https://python.viam.dev/autoapi/viam/gen/service/motion/v1/motion_pb2/index.html#viam.gen.service.motion.v1.motion_pb2.Constraints).

### Go

```go
// Move a gripper with a linear constraint
myConstraints := &servicepb.Constraints{LinearConstraint: []*servicepb.LinearConstraint{&servicepb.LinearConstraint{}}}

moved := motionService.Move(
    context.Background(),
    myGripperResourceName,
    NewPoseInFrame("myFrame", myGoalPose),
    worldState,
    myConstraints,
    nil
    )
```
You can find more information in the [Go SDK Docs](https://pkg.go.dev/go.viam.com/api/service/motion/v1#Constraints).



## Orientation constraint

The orientation constraint (`{"motion_profile": "orientation"}`) places a restriction on the orientation change during a motion, such that the orientation during the motion does not deviate from the [Slerp](https://en.wikipedia.org/wiki/Slerp) between start and goal by more than a set amount.
This is similar to the "orient_tolerance" option in the linear profile, but without any path restrictions.
If set to zero, a movement with identical starting and ending orientations will hold that orientation throughout the movement.

<!-- prettier-ignore -->
| Parameter Name | Type | Default | Description |
| -------------- | ---- | ------- | ----------- |
| orientation_tolerance_degs | float | 2.0 | Allowable deviation from Slerp between start/goal orientations, in degrees. |

**Example usage**:




### Python

```python
# Move a gripper with an orientation constraint
moved = await motion.move(
    component_name=my_gripper,
    destination=PoseInFrame(
        reference_frame="my_frame",
        pose=goal_pose),
    world_state=worldState,
    constraints=Constraints(orientation_constraint=[OrientationConstraint()]),
    extra={})
```
You can find more information in the [Python SDK Docs](https://python.viam.dev/autoapi/viam/gen/service/motion/v1/motion_pb2/index.html#viam.gen.service.motion.v1.motion_pb2.Constraints).

### Go

```go
// Move a gripper with an orientation constraint
myConstraints := &servicepb.Constraints{OrientationConstraint: []*servicepb.OrientationConstraint{&servicepb.OrientationConstraint{}}}

moved := motionService.Move(
    context.Background(),
    myGripperResourceName,
    NewPoseInFrame("myFrame", myGoalPose),
    worldState,
    myConstraints,
    nil
    )
```
You can find more information in the [Go SDK Docs](https://pkg.go.dev/go.viam.com/api/service/motion/v1#Constraints).



## Next steps

Constraints are used in the following tutorials:

<div class="card-container">
  <div class="row-no-margin">
<div class="col hover-card "><a href="/tutorials/projects/claw-game/"><div class="hover-card-video">
          
          
          
          



  
  
    
    
    
  


  
  
    
    
    
  



<div class="gif">
  <video autoplay loop muted playsinline alt="GIF of the claw game in action at a party." width="100%" style="width: 100%" class=" lozad"><source data-src="/tutorials/claw-game/preview.webm" type="video/webm"><source data-src="/tutorials/claw-game/preview.mp4" type="video/mp4">There should have been a video here but your browser does not seem to support it.
  </video>
  <noscript>
    <video autoplay loop muted playsinline alt="GIF of the claw game in action at a party." width="100%" style="width: 100%" class=""><source data-src="/tutorials/claw-game/preview.webm" type="video/webm"><source data-src="/tutorials/claw-game/preview.mp4" type="video/mp4">There should have been a video here but your browser does not seem to support it.
    </video>
  </noscript>
</div></div><div class="small-hover-card-div"class="small-hover-card-div"><div>Claw Game</div><p>Create your own version of the famous arcade claw machine using a robotic arm and a claw grabber.</p></div>
    </a></div>

<div class="col hover-card "><a href="/tutorials/services/constrain-motion/"><div class="hover-card-video">
          
          
          
          



  
  
    
    
    
  


  
  
    
    
    
  



<div class="gif">
  <video autoplay loop muted playsinline alt="An arm moving a cup from one side of a tissue box to the other, across a table. The cup stays upright." width="100%" style="width: 100%" class=" lozad"><source data-src="/tutorials/videos/motion_constraints.webm" type="video/webm"><source data-src="/tutorials/videos/motion_constraints.mp4" type="video/mp4">There should have been a video here but your browser does not seem to support it.
  </video>
  <noscript>
    <video autoplay loop muted playsinline alt="An arm moving a cup from one side of a tissue box to the other, across a table. The cup stays upright." width="100%" style="width: 100%" class=""><source data-src="/tutorials/videos/motion_constraints.webm" type="video/webm"><source data-src="/tutorials/videos/motion_constraints.mp4" type="video/mp4">There should have been a video here but your browser does not seem to support it.
    </video>
  </noscript>
</div></div><div class="small-hover-card-div"class="small-hover-card-div"><div>Add motion constraints</div><p>Use constraints and transforms with the motion service.</p></div>
    </a></div>

</div>
</div>

