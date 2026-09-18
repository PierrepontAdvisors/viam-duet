# Motion service reference

The motion service enables your machine to plan and move its components relative to itself, other machines, and the world.
> Source: https://docs.viam.com/reference/services/motion/


The motion service enables your machine to plan and move itself or its components relative to itself, other machines, and the world.
The motion service:

1. Gathers the current positions of the machine’s components as defined with the [frame system](/motion-planning/frame-system/overview/).
2. Plans the necessary motions to move a component to a given destination while obeying any [constraints you configure](/reference/services/motion/constraints/).

The motion service can:

- use motion [planning algorithms](/motion-planning/reference/algorithms/) locally on your machine to plan coordinated motion across many components.
- pass movement requests through to individual components which have implemented their own motion planning.

## Configuration

You need to configure frames for your machine's components with the [frame system](/motion-planning/frame-system/overview/).
This defines the spatial context within which the motion service operates.

The motion service itself is enabled on the machine by default, so you do not need to add any extra configuration to enable it.

## Access the motion service in your code

Use the motion service in your code by creating a motion service client and then calling its methods.
As with other resource clients, how you get the client depends on whether your code is part of a client application or a module:




### From a client application

To access a motion service, use its name from the machine configuration.
To access the motion service built into `viam-server` from your client application code, use the resource name `builtin` to get a motion service client:

<h3 id="python" class="main-content-heading">
    Python
    
</h3>
```python
# Get a motion service client
motion_service = MotionClient.from_robot(machine, "builtin")

# Then use the motion service, for example:
moved = await motion_service.move(gripper_name, destination, world_state)
```
<h3 id="go" class="main-content-heading">
    Go
    
</h3>
```go
// Get a motion service client
motionService, err := motion.FromProvider(machine, "builtin")
if err != nil {
  logger.Fatal(err)
}

// Then use the motion service, for example:
moved, err := motionService.Move(context.Background(), motion.MoveReq{
  ComponentName: gripperName,
  Destination: destination,
  WorldState: worldState
})
```

### From within a module

To access a motion service, use its name from the machine configuration.
To access the motion service built into `viam-server` from your module code, you need to add the motion service as a [module dependency](/build-modules/dependencies/), using the resource name `builtin`.
For example:

<h3 id="python" class="main-content-heading">
    Python
    
</h3><ol>
<li>
Edit your `validate_config` function to add the `builtin` motion service as a dependency so that it is available to your module.
You do not need to check for it in your config because the built-in motion service is always enabled.

```python
@classmethod
def validate_config(
    cls, config: ComponentConfig
) -> Tuple[Sequence[str], Sequence[str]]:
    req_deps = []
    req_deps.append("builtin")
    return req_deps, []
```
</li>
<li>
Edit your `new` method to add the motion service as an instance variable so that you can use it in your module:

```python
@classmethod
def new(
    cls, config: ComponentConfig, dependencies: Mapping[ResourceName, ResourceBase]
) -> Self:
    instance = cls(config.name)
    motion_resource = dependencies[Motion.get_resource_name("builtin")]
    instance.motion_service = cast(MotionClient, motion_resource)
    return instance
```
</li>
<li>
You can now use the motion service in your module, for example:

```python
def move_around_in_some_way(self):
    moved = await self.motion_service.move(gripper_name, destination, world_state)
    return moved
```
</li>
</ol>
<h3 id="go" class="main-content-heading">
    Go
    
</h3>
```go
// Return the built-in motion service as a required dependency.
func (cfg *Config) Validate(path string) ([]string, []string, error) {
  deps := []string{motion.Named("builtin").String()}
  return deps, nil, nil
}

// Store the motion service on the component in your constructor.
func newComponent(
  ctx context.Context,
  deps resource.Dependencies,
  conf resource.Config,
  logger logging.Logger,
) (resource.Resource, error) {
  motionService, err := motion.FromProvider(deps, "builtin")
  if err != nil {
    return nil, err
  }
  return &Component{
    Named:  conf.ResourceName().AsNamed(),
    logger: logger,
    motion: motionService,
  }, nil
}

// Use the stored motion service, for example:
func (c *Component) MoveAroundInSomeWay(ctx context.Context) (bool, error) {
  return c.motion.Move(ctx, motion.MoveReq{
    ComponentName: gripperName,
    Destination:   destination,
    WorldState:    worldState,
  })
}
```
If you created your own custom motion service, you can access it using the resource name you gave it in your machine’s configuration.
You’ll also need to check for it in your validate function, since it is not built into `viam-server`.



## API

The [motion service API](/reference/apis/services/motion/) supports the following methods:

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


## Test the motion service

You can test motion on your machine from the [**CONTROL** tab](/monitor/).

Enter x and y coordinates to move your machine to, then click the **Move** button to issue a `MoveOnMap()` request.

> **Info:**
> 
> 
> 
> The `plan_deviation_m` for `MoveOnMap()` on calls issued from the **CONTROL** tab is 0.5 m.
> 
> 

