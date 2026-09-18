# Plan motion with an arm and gripper

Use the motion service to move a robot arm and gripper.
> Source: https://docs.viam.com/tutorials/services/plan-motion-with-arm-gripper/


With Viam you can move individual components, like [arms](/reference/components/arm/), by issuing commands like `MoveToPosition` or `MoveToJointPosition`.
The [motion service](/reference/services/motion/) enables you to do much more sophisticated movement involving one or many components of your robot.
The service abstracts the lower-level commands away so that instead of passing in a series of joint positions, you can call the `Move()` command with the desired destination and any obstacles, and the service will move your machine to the desired location for you.

> **Learning Goals:**
> 
> 
> After following this tutorial, you will be able to:
> 
> - provide a representation of objects in the world to Viam
> - use the motion service to move machines or components of your machine
> 
> 

Code examples in this tutorial use a [UFACTORY xArm 6](https://www.ufactory.us/product/ufactory-xarm-6), but you can use any [arm model](/reference/components/arm/).

The [full code](#full-code) is available at the end of this page.

> **Caution:**
> 
> 
> Be careful when instructing robot arms to move.
> Before running any code, ensure your robotic arm has enough space and that there are no obstacles.
> Also pay attention to your surroundings, double-check your code for correctness, and make sure anyone nearby is aware and alert before issuing commands to your robot.
> 

## Prerequisites

Before starting this tutorial, make sure you have the [Viam Python SDK](https://python.viam.dev/) or the [Viam Go SDK](https://pkg.go.dev/go.viam.com/rdk/robot/client#section-readme) installed.

If you are connecting to a real robotic arm during this tutorial, make sure your computer can communicate with the controller before continuing.

Make sure you have followed these steps to configure an arm and a gripper.

1. [Move your first arm](/motion-planning/quickstarts/first-arm/)
2. [Configure your frame system](/motion-planning/frame-system/)
3. [Configure an arm with a gripper and wrist camera](/motion-planning/frame-system/arm-gripper-camera/)

## Configure a robot

Use the robot configuration from the [prerequisite guide](/motion-planning/move-an-arm/move-to-pose/) for this tutorial as well.
We will revisit that robot configuration and add new components.

The motion service is one of the "built-in" services, which means that no initial configuration is required to start planning and executing complex motion.
All you need is a robot with a component that can move, such as a robotic arm.

## Access the motion service

Accessing the motion service is very similar to accessing any other component or service within the Viam ecosystem.




### Python

You must import an additional Python library to access the motion service.
Add the following line to your import list:

```py
from viam.services.motion import MotionClient
```
Then add the sample code below to your client script:

```py
motion_service = MotionClient.from_robot(machine_client, "builtin")
```

### Go

You must import an additional Go package to access the motion service.
Add the following line to your import list:

```go
"go.viam.com/rdk/services/motion"
```
Then add the sample code below to your client script:

```go
motionService, err := motion.FromProvider(machine, "builtin")
if err != nil {
	logger.Fatal(err)
}
```



The Motion service has a method that can get the _pose_ of a component relative to a [_reference frame_](/motion-planning/frame-system/overview/).
In the tutorial where we interacted with an arm component, we used the `GetEndPosition` method to determine the pose of the end effector of `myArm`.
The `GetPose` method provided by the motion service serves a similar function to `GetEndPosition`, but allows for querying of pose data with respect to other elements of the robot (such as another component or the robot's fixed "world" frame).




### Python

Note the use of a hardcoded literal “world” in the following code example.
Any components that have frame information (and, as a result, are added to the frame system) are connected to the “world”.

```py
# Get the pose of myArm from the motion service
my_arm_motion_pose = await motion_service.get_pose(ARM_NAME,
                                                   "world")
print(f"Pose of myArm from the motion service: {my_arm_motion_pose}")
```

### Go

Note the use of `referenceframe.World` in the following code example.
This is a constant string value in the RDK’s `referenceframe` library that is maintained for user and programmer convenience.
Any components that have frame information (and, as a result, are added to the frame system) are connected to the “world”.

```go
// Get the pose of myArm from the motion service
myArmMotionPose, err := motionService.GetPose(context.Background(), armName, referenceframe.World, nil, nil)
if err != nil {
	fmt.Println(err)
}
fmt.Println("Position of myArm from the motion service:", myArmMotionPose.Pose().Point())
fmt.Println("Orientation of myArm from the motion service:", myArmMotionPose.Pose().Orientation())
```



In this example, we are asking the motion service where the end of `arm-1` is with respect to the root "world" reference frame.

## Describe the robot's working environment

The motion service can also use information you provide about the environment around a robot.
The world around a robot may be full of objects that you may wish to prevent your robot from running into when it moves.
There could be many reasons for this: there are places or things in the environment you want the robot to avoid, or you may have mounted your robot to a fixed object, such as a table.

You can pass additional information about the environment to various parts of the Viam system through a particular data structure, aptly named `WorldState`.
The code samples below detail how to add geometry to the WorldState to indicate the presence of other objects in your robot's working environment.




### Python

The `WorldState` is available through the `viam.proto.common` library, but additional geometry data must be added in a piecewise fashion.
You must add additional imports to access `Pose`, `PoseInFrame`, `Vector3`, `Geometry`, `GeometriesInFrame`, and `RectangularPrism` from the proto `common` library.

```py
# Add a table obstacle to a WorldState
table_origin = Pose(x=-202.5, y=-546.5, z=-19.0)
table_dims = Vector3(x=635.0, y=1271.0, z=38.0)
table_object = Geometry(center=table_origin,
                        box=RectangularPrism(dims_mm=table_dims))

obstacles_in_frame = GeometriesInFrame(reference_frame="world",
                                       geometries=[table_object])

# Create a WorldState that has the GeometriesInFrame included
world_state = WorldState(obstacles=[obstacles_in_frame])
```

### Go

You must import the r3 package to be able to add an `r3.Vector`, so add `"github.com/golang/geo/r3"` to your import list.
The `WorldState` is available through the `referenceframe` library, but additional geometry data must be added in a piecewise fashion.

```go
// Add a table obstacle to a WorldState
obstacles := make([]spatialmath.Geometry, 0)

tableOrigin := spatialmath.NewPose(
	r3.Vector{X: -202.5, Y: -546.5, Z: -19.0},
	&spatialmath.OrientationVectorDegrees{OX: 0.0, OY: 0.0, OZ: 1.0, Theta: 0.0},
)
tableDims := r3.Vector{X: 635.0, Y: 1271.0, Z: 38.0}
tableObj, err := spatialmath.NewBox(tableOrigin, tableDims, "table")
obstacles = append(obstacles, tableObj)

// Create a WorldState that has the GeometriesInFrame included
obstaclesInFrame := referenceframe.NewGeometriesInFrame(referenceframe.World, obstacles)
worldState, err := referenceframe.NewWorldState([]*referenceframe.GeometriesInFrame{obstaclesInFrame}, nil)
if err != nil {
	logger.Fatal(err)
}
```



This example adds a "table" with the assumption that you mounted your robot arm to an elevated surface.
The 2000 millimeter by 2000 millimeter dimensions ensure that a sufficiently large box is constructed, regardless of the real physical footprint of your mounting surface.
Setting the Z component of the origin to -19 mm (half the table's thickness) conveniently positions the top surface of the table at 0.
Feel free to change these dimensions, including thickness (the Z coordinate in the above code samples), to match your environment more closely.
Additional obstacles can also be _appended_ as desired.

## Command an arm to move with the motion service

In previous examples you controlled motion of individual components.
Now you will use the motion service to control the motion of the robot as a whole.
You will use the motion service's [`Move`](/reference/apis/services/motion/#move) method to execute more general robotic motion.
You can designate specific components for motion planning by passing in the resource name (note the use of the arm resource in the code samples below).
The `worldState` we constructed earlier is also passed in so that the motion service takes that information into account when planning.

The sample pose given below can be adjusted to fit your specific circumstances.
Remember that X, Y, and Z coordinates are specified in millimeters.

Again, a note:

> **Caution:**
> 
> 
> Executing code presented after this point _will_ induce motion in a connected robotic arm!
> Keep the space around the arm clear!
> 
<br><br>



### Python

```py
# Generate a sample "start" pose to demonstrate motion
test_start_pose = Pose(x=510.0,
                       y=0.0,
                       z=526.0,
                       o_x=0.7071,
                       o_y=0.0,
                       o_z=-0.7071,
                       theta=0.0)
test_start_pose_in_frame = PoseInFrame(reference_frame="world",
                                       pose=test_start_pose)

await motion_service.move(component_name=ARM_NAME,
                          destination=test_start_pose_in_frame,
                          world_state=world_state)
```

### Go

```go
// Generate a sample "start" pose to demonstrate motion
testStartPose := spatialmath.NewPose(
	r3.Vector{X: 510.0, Y: 0.0, Z: 526.0},
	&spatialmath.OrientationVectorDegrees{OX: 0.7071, OY: 0.0, OZ: -0.7071, Theta: 0.0},
)
testStartPoseInFrame := referenceframe.NewPoseInFrame(referenceframe.World, testStartPose)

moveReq := motion.MoveReq{
	ComponentName: armName,
	Destination:   testStartPoseInFrame,
	WorldState:    worldState,
}
_, err = motionService.Move(context.Background(), moveReq)
if err != nil {
	logger.Fatal(err)
}
```



<!-- TODO : In the future, we should add some specific information on the importance of the frame chosen as the point of reference for PoseInFrame variables -->
<!-- ## Managing Pose References -->

## Command other components to move with the motion service

In this section you will add a new component to your machine.
One device that is very commonly attached to the end of a robot arm is a [_gripper_](/reference/components/gripper/).
Most robot arms pick up and manipulate objects in the world with a gripper, so learning how to directly move a gripper is very useful.
Though various motion service commands cause the gripper to move, ultimately the arm is doing all of the work in these situations.
This is possible because the motion service considers other components of the robot (through the [frame system](/motion-planning/frame-system/overview/)) when calculating how to achieve the desired motion.

### Add a gripper component

We need to do several things to prepare a new gripper component for motion.

1. Go back to your machine configuration on [Viam](https://app.viam.com).
2. On the **CONFIGURE** tab, click the **+** icon and select **Blocks** to add a new gripper component to your robot:
   - Search for and select the `gripper / fake` model.
   - Name the component `gripper-1` and click **Add to machine**.
3. Add a **Frame** to the gripper component:
   - Set the parent as `arm-1`.
   - Set the translation as something small in the +Z direction, such as `90` millimeters.
   - Leave the orientation as the default.
   - For **Geometry Type** choose **Box**.
   - Enter desired values for the box's **Length**, **Width**, and **Height**, and the box origin's **X**, **Y**, and **Z** values.
4. Include the `arm-1` component in the **Depends On** dropdown for `gripper-1`.
5. Save this new machine configuration.
   - Your `viam-server` instance should update automatically.

<div class="td-max-width-on-larger-screens">





    
    
    
<picture>

  
  
<source srcset="/tutorials/motion/plan_03_gripper_config_hu_e594d99b6f11618c.webp" type="image/webp" width="700" height="631">
<img src="/tutorials/motion/plan_03_gripper_config.png" width="700" height="631" alt="Sample gripper configuration with several fields filled out." class="" id="" style="" loading="lazy">
  

</picture>



</div>

Because the new gripper component is "attached" (with the parent specification in the Frame) to `arm-1`, we can produce motion plans using `gripper-1` instead of `arm-1`.




### Python

Add this code to your `main()`:

```py
# This will move the gripper in the -Z direction with respect to its own
# reference frame
gripper_pose_rev = Pose(x=0.0,
                        y=0.0,
                        z=-50.0,
                        o_x=0.0,
                        o_y=0.0,
                        o_z=1.0,
                        theta=0.0)
# Note the change in frame name
gripper_pose_rev_in_frame = PoseInFrame(
    reference_frame=GRIPPER_NAME,
    pose=gripper_pose_rev)

await motion_service.move(component_name=GRIPPER_NAME,
                          destination=gripper_pose_rev_in_frame,
                          world_state=world_state)
```

### Go

Add this code to your `main()`:

```go
// This will move the gripper in the -Z direction with respect to its own reference frame
gripperPoseRev := spatialmath.NewPose(
	r3.Vector{X: 0.0, Y: 0.0, Z: -50.0},
	&spatialmath.OrientationVectorDegrees{OX: 0.0, OY: 0.0, OZ: 1.0, Theta: 0.0},
)
gripperPoseRevInFrame := referenceframe.NewPoseInFrame(gripperName, gripperPoseRev) // Note the change in frame name

gripperMoveReq := motion.MoveReq{
	ComponentName: gripperName,
	Destination:   gripperPoseRevInFrame,
	WorldState:    worldState,
}
_, err = motionService.Move(context.Background(), gripperMoveReq)
if err != nil {
	logger.Fatal(err)
}
```



For the gripper pose, you can change the reference frame information to consider other objects or user-generated frames that exist in the frame system.
Specifying other reference frames is an easy way to move with respect to those frames.
For example, you can specify a pose that is 100 millimeters above the table obstacle featured earlier in this tutorial.
You do not need to calculate that exact pose with respect to the **arm** or **world**.
You must only provide the object name (instead of the `gripperName` you saw in the code samples above) when making the `PoseInFrame` to pass into the `Move` function.
This has implications for how motion is calculated, and what final configuration your robot will rest in after moving.

## Next steps

If you would like to continue onto working with Viam's motion service, check out one of these tutorials:

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

You can also ask questions in the [Community Discord](https://discord.gg/viam) and we will be happy to help.


## Full code




### Python

```py
import asyncio

from viam.components.arm import Arm
from viam.components.gripper import Gripper
from viam.proto.common import Geometry, GeometriesInFrame, Pose, PoseInFrame, \
    RectangularPrism, Vector3, WorldState
from viam.proto.component.arm import JointPositions
from viam.robot.client import RobotClient
from viam.services.motion import MotionClient

# Configuration constants – replace with your actual values
API_KEY = ""  # API key, find or create in your organization settings
API_KEY_ID = ""  # API key ID, find or create in your organization settings
MACHINE_ADDRESS = ""  # the address of the machine you want to capture images from
ARM_NAME = ""  # the name of the arm you want to plan motion for
GRIPPER_NAME = ""  # the name of the gripper attached to the arm

async def connect_machine() -> RobotClient:
    """Establish a connection to the robot using the robot address."""
    machine_opts = RobotClient.Options.with_api_key(
        api_key=API_KEY,
        api_key_id=API_KEY_ID
    )
    return await RobotClient.at_address(MACHINE_ADDRESS, machine_opts)

async def main() -> int:
    async with await connect_machine() as machine:
        # Access myArm
        my_arm_component = Arm.from_robot(machine, ARM_NAME)

        # End Position of myArm
        my_arm_end_position = await my_arm_component.get_end_position()
        print(f"myArm get_end_position return value: {my_arm_end_position}")

        # Joint Positions of myArm
        my_arm_joint_positions = await my_arm_component.get_joint_positions()
        print(f"myArm get_joint_positions return value: {my_arm_joint_positions}")

        # Command a joint position move: move the forearm of the arm slightly up
        cmd_joint_positions = JointPositions(values=[0, 0, -30.0, 0, 0, 0])
        await my_arm_component.move_to_joint_positions(
            positions=cmd_joint_positions)

        # Generate a simple pose move +100mm in the +Z direction of the arm
        cmd_arm_pose = await my_arm_component.get_end_position()
        cmd_arm_pose.z += 100.0
        await my_arm_component.move_to_position(pose=cmd_arm_pose)

        # Access the motion service
        motion_service = MotionClient.from_robot(machine, "builtin")

        # Get the pose of myArm from the motion service
        my_arm_motion_pose = await motion_service.get_pose(ARM_NAME,
                                                        "world")
        print(f"Pose of myArm from the motion service: {my_arm_motion_pose}")

        # Add a table obstacle to a WorldState
        table_origin = Pose(x=-202.5, y=-546.5, z=-19.0)
        table_dims = Vector3(x=635.0, y=1271.0, z=38.0)
        table_object = Geometry(center=table_origin,
                                box=RectangularPrism(dims_mm=table_dims))

        obstacles_in_frame = GeometriesInFrame(reference_frame="world",
                                            geometries=[table_object])

        # Create a WorldState that has the GeometriesInFrame included
        world_state = WorldState(obstacles=[obstacles_in_frame])

        # Generate a sample "start" pose to demonstrate motion
        test_start_pose = Pose(x=510.0,
                               y=0.0,
                               z=526.0,
                               o_x=0.7071,
                               o_y=0.0,
                               o_z=-0.7071,
                               theta=0.0)
        test_start_pose_in_frame = PoseInFrame(reference_frame="world",
                                               pose=test_start_pose)

        await motion_service.move(component_name=ARM_NAME,
                                  destination=test_start_pose_in_frame,
                                  world_state=world_state)

        # This will move the gripper in the -Z direction with respect to its own
        # reference frame
        gripper_pose_rev = Pose(x=0.0,
                                y=0.0,
                                z=-50.0,
                                o_x=0.0,
                                o_y=0.0,
                                o_z=1.0,
                                theta=0.0)
        # Note the change in frame name
        gripper_pose_rev_in_frame = PoseInFrame(
            reference_frame=GRIPPER_NAME,
            pose=gripper_pose_rev)

        await motion_service.move(component_name=GRIPPER_NAME,
                                  destination=gripper_pose_rev_in_frame,
                                  world_state=world_state)

        return 0

if __name__ == "__main__":
    asyncio.run(main())
```

### Go

```go
package main

import (
  "context"
  "fmt"

  "github.com/golang/geo/r3"
  "go.viam.com/rdk/components/arm"
  "go.viam.com/rdk/logging"
  "go.viam.com/rdk/referenceframe"
  "go.viam.com/rdk/robot/client"
  "go.viam.com/rdk/services/motion"
  "go.viam.com/rdk/spatialmath"
)

func main() {
	apiKey := ""
	apiKeyID := ""
	machineAddress := ""
	armName := ""
	gripperName := ""

	logger := logging.NewLogger("client")
	machine, err := client.New(
		context.Background(),
		machineAddress,
		logger,
		client.WithDialOptions(client.WithEntityCredentials(
			apiKeyID,
			client.Credentials{
				Type:    client.CredentialsTypeAPIKey,
				Payload: apiKey,
			})),
	)
	if err != nil {
		logger.Fatal(err)
	}

	// Access myArm
	myArmComponent, err := arm.FromProvider(machine, armName)
	if err != nil {
		fmt.Println(err)
	}

	// End Position of myArm
	myArmEndPosition, err := myArmComponent.EndPosition(context.Background(), nil)
	if err != nil {
		fmt.Println(err)
	}
	fmt.Println("myArm EndPosition position value:", myArmEndPosition.Point())
	fmt.Println("myArm EndPosition orientation value:", myArmEndPosition.Orientation())

	// Joint Positions of myArm
	myArmJointPositions, err := myArmComponent.JointPositions(context.Background(), nil)
	if err != nil {
		fmt.Println(err)
	}
	fmt.Println("myArm JointPositions return value:", myArmJointPositions)

	// Command a joint position move: move the forearm of the arm slightly up
	cmdJointPositions := []referenceframe.Input{
		0.0, 0.0, -3.0, 0.0, 0.0, 0.0,
	}
	err = myArmComponent.MoveToJointPositions(context.Background(), cmdJointPositions, nil)
	if err != nil {
		fmt.Println(err)
	}

	// Generate a simple pose move +100mm in the +Z direction of the arm
	currentArmPose, err := myArmComponent.EndPosition(context.Background(), nil)
	if err != nil {
		fmt.Println("Error getting end position of myArm:", err)
		fmt.Println(err)
	}
	fmt.Println("Moving to end position +100mm")
	adjustedArmPoint := currentArmPose.Point()
	adjustedArmPoint.Z += 100.0
	cmdArmPose := spatialmath.NewPose(adjustedArmPoint, currentArmPose.Orientation())

	err = myArmComponent.MoveToPosition(context.Background(), cmdArmPose, nil)
	if err != nil {
		fmt.Println(err)
	}

	// Access the motion service
	motionService, err := motion.FromProvider(machine, "builtin")
	if err != nil {
		logger.Fatal(err)
	}

	// Get the pose of myArm from the motion service
	myArmMotionPose, err := motionService.GetPose(context.Background(), armName, referenceframe.World, nil, nil)
	if err != nil {
		fmt.Println(err)
	}
	fmt.Println("Position of myArm from the motion service:", myArmMotionPose.Pose().Point())
	fmt.Println("Orientation of myArm from the motion service:", myArmMotionPose.Pose().Orientation())

	// Add a table obstacle to a WorldState
	obstacles := make([]spatialmath.Geometry, 0)

	tableOrigin := spatialmath.NewPose(
		r3.Vector{X: -202.5, Y: -546.5, Z: -19.0},
		&spatialmath.OrientationVectorDegrees{OX: 0.0, OY: 0.0, OZ: 1.0, Theta: 0.0},
	)
	tableDims := r3.Vector{X: 635.0, Y: 1271.0, Z: 38.0}
	tableObj, err := spatialmath.NewBox(tableOrigin, tableDims, "table")
	obstacles = append(obstacles, tableObj)

	// Create a WorldState that has the GeometriesInFrame included
	obstaclesInFrame := referenceframe.NewGeometriesInFrame(referenceframe.World, obstacles)
	worldState, err := referenceframe.NewWorldState([]*referenceframe.GeometriesInFrame{obstaclesInFrame}, nil)
	if err != nil {
		logger.Fatal(err)
	}

	// Generate a sample "start" pose to demonstrate motion
	testStartPose := spatialmath.NewPose(
		r3.Vector{X: 510.0, Y: 0.0, Z: 526.0},
		&spatialmath.OrientationVectorDegrees{OX: 0.7071, OY: 0.0, OZ: -0.7071, Theta: 0.0},
	)
	testStartPoseInFrame := referenceframe.NewPoseInFrame(referenceframe.World, testStartPose)

	moveReq := motion.MoveReq{
		ComponentName: armName,
		Destination:   testStartPoseInFrame,
		WorldState:    worldState,
	}
	_, err = motionService.Move(context.Background(), moveReq)
	if err != nil {
		logger.Fatal(err)
	}

	// This will move the gripper in the -Z direction with respect to its own reference frame
	gripperPoseRev := spatialmath.NewPose(
		r3.Vector{X: 0.0, Y: 0.0, Z: -50.0},
		&spatialmath.OrientationVectorDegrees{OX: 0.0, OY: 0.0, OZ: 1.0, Theta: 0.0},
	)
	gripperPoseRevInFrame := referenceframe.NewPoseInFrame(gripperName, gripperPoseRev) // Note the change in frame name

	gripperMoveReq := motion.MoveReq{
		ComponentName: gripperName,
		Destination:   gripperPoseRevInFrame,
		WorldState:    worldState,
	}
	_, err = motionService.Move(context.Background(), gripperMoveReq)
	if err != nil {
		logger.Fatal(err)
	}
}
```



