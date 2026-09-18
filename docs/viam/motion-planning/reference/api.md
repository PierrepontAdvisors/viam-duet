# Motion service API

The motion service API for planning and executing component movements.
> Source: https://docs.viam.com/motion-planning/reference/api/


The motion service exposes the methods below for planning and executing component motion. Most methods are implemented only by module-based motion services. The builtin service implements `Move`, `GetPose` (deprecated), `DoCommand`, and `GetStatus`.

`MoveOnMap`, `MoveOnGlobe`, `StopPlan`, `ListPlanStatuses`, and `GetPlan` return a `not supported by builtin` error; module-based motion services may implement them.

<!-- prettier-ignore -->
| Method Name | Description |
| ----------- | ----------- |
| [`Move`](/reference/apis/services/motion/#move) | The `Move` method is the primary way to move multiple components, or to move any object to any other location. |
| [`MoveOnMap`](/reference/apis/services/motion/#moveonmap) | Move a base component to a destination pose on a SLAM map. |
| [`MoveOnGlobe`](/reference/apis/services/motion/#moveonglobe) | Move a base component to a destination GPS point, represented in geographic notation _(latitude, longitude)_. |
| [`GetPose`](/reference/apis/services/motion/#getpose) | `GetPose` gets the location and orientation of a component within the frame system. |
| [`StopPlan`](/reference/apis/services/motion/#stopplan) | Stop a base component being moved by an in progress `MoveOnGlobe` or `MoveOnMap` call. |
| [`ListPlanStatuses`](/reference/apis/services/motion/#listplanstatuses) | Returns the statuses of plans created by `MoveOnGlobe` or `MoveOnMap` calls that meet at least one of the following conditions since the motion service initialized:  - the plan's status is in progress - the plan's status changed state within the last 24 hours  All repeated fields are in chronological order. |
| [`GetPlan`](/reference/apis/services/motion/#getplan) | By default, returns the plan history of the most recent `MoveOnGlobe` or `MoveOnMap` call to move a base component. |
| [`Reconfigure`](/reference/apis/services/motion/#reconfigure) | Reconfigure this resource. |
| [`FromRobot`](/reference/apis/services/motion/#fromrobot) | Get the resource from the provided machine. |
| [`DoCommand`](/reference/apis/services/motion/#docommand) | Execute model-specific commands that are not otherwise defined by the service API. |
| [`GetStatus`](/reference/apis/services/motion/#getstatus) | Get the current status of the motion service as a map of key-value pairs describing its state. |
| [`GetResourceName`](/reference/apis/services/motion/#getresourcename) | Get the `ResourceName` for this instance of the motion service. |
| [`Close`](/reference/apis/services/motion/#close) | Safely shut down the resource and prevent further use. |


For full method signatures, parameters, and code examples, see the
[auto-generated motion API reference](/reference/apis/services/motion/).

## Method overview

### Move

Plans and executes a motion to a destination pose. This is the primary method for arm and gantry planning.

Key parameters:

- `component_name`: the component to move (typically an arm or gantry in this section's examples)
- `destination`: a `PoseInFrame` specifying the target pose and reference frame
- `world_state`: optional obstacles and transforms
- `constraints`: optional linear, orientation, or collision constraints

### MoveOnMap, MoveOnGlobe, StopPlan, ListPlanStatuses, and GetPlan

Navigate mobile bases and manage the resulting plans. The builtin motion service returns a `not supported by builtin` error for each of these methods (for example, `MoveOnMap not supported by builtin`); module-based motion services may implement them.

### GetPose (deprecated)

Returns a component's pose. Deprecated in favor of the robot service's `GetPose`. Python callers still use this motion-service method today; see the [Frame system API reference](/motion-planning/reference/frame-system-api/).

### DoCommand

Sends arbitrary commands. The builtin motion service supports a `"plan"`
command (returns a trajectory without executing it), an `"execute"` command
(runs a trajectory; add the `"executeCheckStart"` key to an execute request
to verify the resource is at the trajectory's start first), and the teleop
commands (`teleop_start`, `teleop_move`, `teleop_stop`, and `teleop_status`),
which stream smoothed, incremental joint commands for interactive arm
teleoperation.

### GetStatus

Returns generic resource status. `GetStatus` is part of the common resource API that every resource implements, including the builtin motion service; the generated table above omits common RPCs. Use it for liveness checks.

