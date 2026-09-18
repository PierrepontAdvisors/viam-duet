# Input controller API

Give commands to register callbacks for events, allowing you to use input devices to control your machines.
> Source: https://docs.viam.com/reference/apis/components/input-controller/


The input controller API allows you to give commands to your [input controller components](/hardware/common-components/add-an-input-controller/) for configuring callbacks for events, allowing you to configure input devices to control your machines.

The input controller component supports the following methods:

<!-- prettier-ignore -->
| Method Name | Description |
| ----------- | ----------- |
| [`GetControls`](/reference/apis/components/input-controller/#getcontrols) | Get a list of the Controls that your controller provides. |
| [`GetEvents`](/reference/apis/components/input-controller/#getevents) | This method returns the current state of the controller as a map of Event Objects, representing the most recent event that has occurred on each available Control. |
| [`TriggerEvent`](/reference/apis/components/input-controller/#triggerevent) | Directly send an Event Object from external code. |
| [`GetGeometries`](/reference/apis/components/input-controller/#getgeometries) | Get all the geometries associated with the input controller in its current configuration, in the frame of the input controller. |
| [`RegisterControlCallback`](/reference/apis/components/input-controller/#registercontrolcallback) | Defines a callback function to execute whenever one of the EventTypes selected occurs on the given Control. |
| [`Reconfigure`](/reference/apis/components/input-controller/#reconfigure) | Reconfigure this resource. |
| [`DoCommand`](/reference/apis/components/input-controller/#docommand) | Execute model-specific commands that are not otherwise defined by the component API. |
| [`GetStatus`](/reference/apis/components/input-controller/#getstatus) | Get the current status of the input controller as a map of key-value pairs describing its state. |
| [`GetResourceName`](/reference/apis/components/input-controller/#getresourcename) | Get the `ResourceName` for this input controller. |
| [`Close`](/reference/apis/components/input-controller/#close) | Safely shut down the resource and prevent further use. |


## API

### GetControls

Get a list of the [Controls](/reference/apis/components/input-controller/#control-field) that your controller provides.

{{< tabs >}}
{{% tab name="Python" %}}

**Parameters:**

- `extra` (Mapping[[str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str), Any]) (optional): Extra options to pass to the underlying RPC call.
- `timeout` ([float](https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex)) (optional): An option to set how long to wait (in seconds) before calling a time-out and closing the underlying RPC call.

**Returns:**

- ([List[viam.components.input.input.Control]](https://python.viam.dev/autoapi/viam/components/input/input/index.html#viam.components.input.input.Control)): :   List of controls provided by the Controller.

**Example:**

```python {class="line-numbers linkable-line-numbers"}
# Get the controller from the machine.
my_controller = Controller.from_robot(
    robot=machine, "my_controller")

# Get the list of Controls provided by the controller.
controls = await my_controller.get_controls()

# Print the list of Controls provided by the controller.
print(f"Controls: {controls}")
```

For more information, see the [Python SDK Docs](https://python.viam.dev/autoapi/viam/components/input/client/index.html#viam.components.input.client.ControllerClient.get_controls).

{{% /tab %}}
{{% tab name="Go" %}}

**Parameters:**

- `ctx` [(Context)](https://pkg.go.dev/context#Context): A Context carries a deadline, a cancellation signal, and other values across API boundaries.
- `extra` [(map[string]interface{})](https://go.dev/blog/maps): Extra options to pass to the underlying RPC call.

**Returns:**

- [([]Control)](https://pkg.go.dev/go.viam.com/rdk/components/input#Control): List of Controls provided by the controller.
- [(error)](https://pkg.go.dev/builtin#error): An error, if one occurred.

**Example:**

```go {class="line-numbers linkable-line-numbers"}
myController, err := input.FromProvider(machine, "my_input_controller")

// Get the list of Controls provided by the controller.
controls, err := myController.Controls(context.Background(), nil)
```

For more information, see the [Go SDK Docs](https://pkg.go.dev/go.viam.com/rdk/components/input#Controller).

{{% /tab %}}
{{< /tabs >}}

### GetEvents

This method returns the current state of the controller as a map of [Event Objects](#event-object), representing the most recent event that has occurred on each available [Control](#control-field).

{{< tabs >}}
{{% tab name="Python" %}}

**Parameters:**

- `extra` (Mapping[[str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str), Any]) (optional): Extra options to pass to the underlying RPC call.
- `timeout` ([float](https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex)) (optional): An option to set how long to wait (in seconds) before calling a time-out and closing the underlying RPC call.

**Returns:**

- ([Dict[viam.components.input.input.Control, viam.components.input.input.Event]](https://python.viam.dev/autoapi/viam/components/input/input/index.html#viam.components.input.input.Control)): :   The most recent event for each input.

**Example:**

```python {class="line-numbers linkable-line-numbers"}
# Get the controller from the machine.
my_controller = Controller.from_robot(
    robot=machine, "my_controller")

# Get the most recent Event for each Control.
recent_events = await my_controller.get_events()

# Print out the most recent Event for each Control.
print(f"Recent Events: {recent_events}")
```

For more information, see the [Python SDK Docs](https://python.viam.dev/autoapi/viam/components/input/client/index.html#viam.components.input.client.ControllerClient.get_events).

{{% /tab %}}
{{% tab name="Go" %}}

**Parameters:**

- `ctx` [(Context)](https://pkg.go.dev/context#Context): A Context carries a deadline, a cancellation signal, and other values across API boundaries.
- `extra` [(map[string]interface{})](https://go.dev/blog/maps): Extra options to pass to the underlying RPC call.

**Returns:**

- [(map[Control]Event)](https://pkg.go.dev/go.viam.com/rdk/components/input#Event): A map mapping the most recent Event for each Control.
- [(error)](https://pkg.go.dev/builtin#error): An error, if one occurred.

**Example:**

```go {class="line-numbers linkable-line-numbers"}
myController, err := input.FromProvider(machine, "my_input_controller")

// Get the most recent Event for each Control.
recent_events, err := myController.Events(context.Background(), nil)
```

For more information, see the [Go SDK Docs](https://pkg.go.dev/go.viam.com/rdk/components/input#Controller).

{{% /tab %}}
{{% tab name="TypeScript" %}}

**Parameters:**

- `extra` (None) (optional)
- `callOptions` (CallOptions) (optional)

**Returns:**

- (Promise<[Event](https://ts.viam.dev/classes/inputControllerApi.Event.html)[]>)

**Example:**

```ts {class="line-numbers linkable-line-numbers"}
const controller = new VIAM.InputControllerClient(machine, 'my_controller');

// Get the most recent Event for each Control
const recentEvents = await controller.getEvents();
console.log('Recent events:', recentEvents);
```

For more information, see the [TypeScript SDK Docs](https://ts.viam.dev/classes/InputControllerClient.html#getevents).

{{% /tab %}}
{{< /tabs >}}

### TriggerEvent

Directly send an [Event Object](#event-object) from external code.

{{% alert title="Support Notice" color="note" %}}
This method is currently only supported for input controllers of model `webgamepad`.
{{% /alert %}}

{{< tabs >}}
{{% tab name="Python" %}}

**Parameters:**

- `event` ([viam.components.input.input.Event](https://python.viam.dev/autoapi/viam/components/input/index.html#viam.components.input.Event)) (required): The event to trigger.
- `extra` (Mapping[[str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str), Any]) (optional): Extra options to pass to the underlying RPC call.
- `timeout` ([float](https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex)) (optional): An option to set how long to wait (in seconds) before calling a time-out and closing the underlying RPC call.

**Returns:**

- None.

**Example:**

```python {class="line-numbers linkable-line-numbers"}
# Get your controller from the machine.
my_controller = Controller.from_robot(
    robot=machine, "my_controller")

# Define a "Button is Pressed" event for the control BUTTON_START.
button_is_pressed_event = Event(
    time(), EventType.BUTTON_PRESS, Control.BUTTON_START, 1.0)

# Trigger the event on your controller. Set this trigger to timeout if it has
# not completed in 7 seconds.
await my_controller.trigger_event(event=button_is_pressed_event, timeout=7.0)
```

For more information, see the [Python SDK Docs](https://python.viam.dev/autoapi/viam/components/input/client/index.html#viam.components.input.client.ControllerClient.trigger_event).

{{% /tab %}}
{{% tab name="Go" %}}

**Parameters:**

- `ctx` [(Context)](https://pkg.go.dev/context#Context): A Context carries a deadline, a cancellation signal, and other values across API boundaries.
- `event` [(Event)](https://pkg.go.dev/go.viam.com/rdk/components/input#Event): The `Event` to trigger on the controller.
- `extra` [(map[string]interface{})](https://go.dev/blog/maps): Extra options to pass to the underlying RPC call.

**Returns:**

- [(error)](https://pkg.go.dev/builtin#error): An error, if one occurred.

For more information, see the [Go SDK Docs](https://pkg.go.dev/go.viam.com/rdk/components/input#Triggerable).

{{% /tab %}}
{{% tab name="TypeScript" %}}

**Parameters:**

- `event` ([InputControllerEvent](https://ts.viam.dev/types/InputControllerEvent.html)) (required)
- `extra` (None) (optional)
- `callOptions` (CallOptions) (optional)

**Returns:**

- (Promise<void>)

**Example:**

```ts {class="line-numbers linkable-line-numbers"}
const controller = new VIAM.InputControllerClient(machine, 'my_controller');

// Create a "Button is Pressed" event for the control BUTTON_START
const buttonPressEvent = new VIAM.InputControllerEvent({
  time: { seconds: BigInt(Math.floor(Date.now() / 1000)) },
  event: 'ButtonPress',
  control: 'ButtonStart',
  value: 1.0,
});
// Trigger the event
await controller.triggerEvent(buttonPressEvent);
```

For more information, see the [TypeScript SDK Docs](https://ts.viam.dev/classes/InputControllerClient.html#triggerevent).

{{% /tab %}}
{{< /tabs >}}

### GetGeometries

Get all the geometries associated with the input controller in its current configuration, in the [frame](/reference/services/frame-system/) of the input controller.
The [motion](/reference/services/motion/) and [navigation](/reference/services/navigation/) services use the relative position of inherent geometries to configured geometries representing obstacles for collision detection and obstacle avoidance while motion planning.

{{< tabs >}}
{{% tab name="Python" %}}

**Parameters:**

- `extra` (Mapping[[str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str), Any]) (optional): Extra options to pass to the underlying RPC call.
- `timeout` ([float](https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex)) (optional): An option to set how long to wait (in seconds) before calling a time-out and closing the underlying RPC call.

**Returns:**

- ([List[viam.proto.common.Geometry]](https://python.viam.dev/autoapi/viam/proto/common/index.html#viam.proto.common.Geometry)): :   The geometries associated with the Component.

**Example:**

```python {class="line-numbers linkable-line-numbers"}
my_controller = Controller.from_robot(robot=machine, name="my_controller")
geometries = await my_controller.get_geometries()

if geometries:
    # Get the center of the first geometry
    print(f"Pose of the first geometry's centerpoint: {geometries[0].center}")
```

For more information, see the [Python SDK Docs](https://python.viam.dev/autoapi/viam/components/input/client/index.html#viam.components.input.client.ControllerClient.get_geometries).

{{% /tab %}}
{{< /tabs >}}

### RegisterControlCallback

Defines a callback function to execute whenever one of the [EventTypes](#eventtype-field) selected occurs on the given [Control](#control-field).

You can only register one callback function per [Event](#event-object) for each [Control](#control-field).
A second call to register a callback function for a [EventType](#eventtype-field) on a [Control](#control-field) replaces any function that was already registered.

You can pass a `nil` function here to "deregister" a callback.

{{% alert title="Tip" color="tip" %}}
Registering a callback for the `ButtonChange` [EventType](#eventtype-field) is merely a convenience for filtering.
Doing so registers the same callback to both `ButtonPress` and `ButtonRelease`, but `ButtonChange` is not reported in an actual [Event Object](#event-object).
{{% /alert %}}

{{< tabs >}}
{{% tab name="Python" %}}

**Parameters:**

- `control` ([viam.components.input.input.Control](https://python.viam.dev/autoapi/viam/components/input/index.html#viam.components.input.Control)) (required): The control to register the function for.
- `triggers` ([List[viam.components.input.input.EventType]](https://python.viam.dev/autoapi/viam/components/input/index.html#viam.components.input.EventType)) (required): The events that will trigger the function.
- `function` ([viam.components.input.input.ControlFunction](https://python.viam.dev/autoapi/viam/components/input/index.html#viam.components.input.ControlFunction)) (optional): The function to run on specific triggers.
- `extra` (Mapping[[str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str), Any]) (optional): Extra options to pass to the underlying RPC call.

**Returns:**

- None.

**Example:**

```python {class="line-numbers linkable-line-numbers"}
from viam.components.input import Control, EventType

# Define a function to handle pressing the Start Menu Button "BUTTON_START" on
# your controller, printing out the start time.
def print_start_time(event):
    print(f"Start Menu Button was pressed at this time: {event.time}")


# Define a function that handles the controller.
async def handle_controller(controller):
    # Get the list of Controls on the controller.
    controls = await controller.get_controls()

    # If the "BUTTON_START" Control is found, register the function
    # print_start_time to fire when "BUTTON_START" has the event "ButtonPress"
    # occur.
    if Control.BUTTON_START in controls:
        controller.register_control_callback(
            Control.BUTTON_START, [EventType.BUTTON_PRESS], print_start_time)
    else:
        print("Oops! Couldn't find the start button control! Is your "
            "controller connected?")
        exit()

    while True:
        await asyncio.sleep(1.0)


async def main():
    # ... < INSERT CONNECTION CODE FROM MACHINE'S CONNECT TAB >

    # Get your controller from the machine.
    my_controller = Controller.from_robot(
        robot=machine, "my_controller")

    # Run the handleController function.
    await handle_controller(my_controller)

    # ... < INSERT ANY OTHER CODE FOR MAIN FUNCTION >
```

For more information, see the [Python SDK Docs](https://python.viam.dev/autoapi/viam/components/input/client/index.html#viam.components.input.client.ControllerClient.register_control_callback).

{{% /tab %}}
{{% tab name="Go" %}}

**Parameters:**

- `ctx` [(Context)](https://pkg.go.dev/context#Context): A Context carries a deadline, a cancellation signal, and other values across API boundaries.
- `control` [(Control)](https://pkg.go.dev/go.viam.com/rdk/components/input#Control): The [Control](/reference/apis/components/input-controller/#control-field) to register the function for.
- `triggers` [([]EventType)](https://pkg.go.dev/go.viam.com/rdk/components/input#EventType): The [EventTypes](#eventtype-field) that trigger the function.
- `ctrlFunc` [(ControlFunction)](https://pkg.go.dev/go.viam.com/rdk/components/input#ControlFunction): The function to run when the specified triggers are invoked.
- `extra` [(map[string]interface{})](https://go.dev/blog/maps): Extra options to pass to the underlying RPC call.

**Returns:**

- [(error)](https://pkg.go.dev/builtin#error): An error, if one occurred.

**Example:**

```go {class="line-numbers linkable-line-numbers"}
// Define a function to handle pressing the Start Menu button, "ButtonStart", on your controller and logging the start time
printStartTime := func(ctx context.Context, event input.Event) {
    logger.Info("Start Menu Button was pressed at this time: %v", event.Time)
}

myController, err := input.FromProvider(machine, "my_input_controller")

// Define the EventType "ButtonPress" to serve as the trigger for printStartTime.
triggers := []input.EventType{input.ButtonPress}

// Get the controller's Controls.
controls, err := myController.Controls(context.Background(), nil)

// If the "ButtonStart" Control is found, trigger printStartTime when on "ButtonStart" the event "ButtonPress" occurs.
if !slices.Contains(controls, input.ButtonStart) {
    logger.Error("button 'ButtonStart' not found; controller may be disconnected")
    return
}

myController.RegisterControlCallback(context.Background(), input.ButtonStart, triggers, printStartTime, nil)
```

For more information, see the [Go SDK Docs](https://pkg.go.dev/go.viam.com/rdk/components/input#Controller).

{{% /tab %}}
{{< /tabs >}}

### Reconfigure

Reconfigure this resource.
Reconfigure must reconfigure the resource atomically and in place.

{{< tabs >}}
{{% tab name="Go" %}}

**Parameters:**

- `ctx` [(Context)](https://pkg.go.dev/context#Context): A Context carries a deadline, a cancellation signal, and other values across API boundaries.
- `deps` [(Dependencies)](https://pkg.go.dev/go.viam.com/rdk/resource#Dependencies): The resource dependencies.
- `conf` [(Config)](https://pkg.go.dev/go.viam.com/rdk/resource#Config): The resource configuration.

**Returns:**

- [(error)](https://pkg.go.dev/builtin#error): An error, if one occurred.

For more information, see the [Go SDK Docs](https://pkg.go.dev/go.viam.com/rdk/resource#Resource).

{{% /tab %}}
{{< /tabs >}}

### DoCommand

Execute model-specific commands that are not otherwise defined by the component API.
Most models do not implement `DoCommand`.
Any available model-specific commands should be covered in the model's documentation.
If you are implementing your own input controller and want to add features that have no corresponding built-in API method, you can implement them with [`DoCommand`](/reference/sdks/docommand/).

{{< tabs >}}
{{% tab name="Python" %}}

**Parameters:**

- `command` (Mapping[[str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str), ValueTypes]) (required): The command to execute.
- `timeout` ([float](https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex)) (optional): An option to set how long to wait (in seconds) before calling a time-out and closing the underlying RPC call.

**Returns:**

- (Mapping[[str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str), viam.utils.ValueTypes]): :   Result of the executed command.

**Raises:**

- (NotImplementedError): Raised if the Resource does not support arbitrary commands.

**Example:**

```python {class="line-numbers linkable-line-numbers"}
my_input_controller = InputController.from_robot(robot=machine, name="my_input_controller")
command = {"cmd": "test", "data1": 500}
result = await my_input_controller.do_command(command)
```

For more information, see the [Python SDK Docs](https://python.viam.dev/autoapi/viam/components/input/client/index.html#viam.components.input.client.ControllerClient.do_command).

{{% /tab %}}
{{% tab name="Go" %}}

**Parameters:**

- `ctx` [(Context)](https://pkg.go.dev/context#Context): A Context carries a deadline, a cancellation signal, and other values across API boundaries.
- `cmd` [(map[string]interface{})](https://go.dev/blog/maps): The command to execute.

**Returns:**

- [(map[string]interface{})](https://pkg.go.dev/builtin#string): The command response.
- [(error)](https://pkg.go.dev/builtin#error): An error, if one occurred.

**Example:**

```go {class="line-numbers linkable-line-numbers"}
myInputController, err := input_controller.FromProvider(machine, "my_input_controller")

command := map[string]interface{}{"cmd": "test", "data1": 500}
result, err := myInputController.DoCommand(context.Background(), command)
```

For more information, see the [Go SDK Docs](https://pkg.go.dev/go.viam.com/rdk/resource#Resource).

{{% /tab %}}
{{< /tabs >}}

### GetStatus

Get the current status of the input controller as a map of key-value pairs describing its state.

{{< tabs >}}
{{% tab name="Python" %}}

**Parameters:**

- `timeout` ([float](https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex)) (optional): An option to set how long to wait (in seconds) before calling a time-out and closing the underlying RPC call.

**Returns:**

- (Mapping[[str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str), viam.utils.ValueTypes]): :   The status of the component.

**Example:**

```python {class="line-numbers linkable-line-numbers"}
status = await component.get_status()
```

For more information, see the [Python SDK Docs](https://python.viam.dev/autoapi/viam/components/input/client/index.html#viam.components.input.client.ControllerClient.get_status).

{{% /tab %}}
{{% tab name="Go" %}}

**Parameters:**

- `ctx` [(Context)](https://pkg.go.dev/context#Context): A Context carries a deadline, a cancellation signal, and other values across API boundaries.

**Returns:**

- [(map[string]interface{})](https://pkg.go.dev/builtin#string)
- [(error)](https://pkg.go.dev/builtin#error): An error, if one occurred.

**Example:**

```go {class="line-numbers linkable-line-numbers"}
myInputController, err := input.FromProvider(machine, "my_input_controller")

status, err := myInputController.Status(context.Background())
```

For more information, see the [Go SDK Docs](https://pkg.go.dev/go.viam.com/rdk/resource#Resource).

{{% /tab %}}
{{% tab name="TypeScript" %}}

**Parameters:**

- `callOptions` (CallOptions) (optional)

**Returns:**

- (Promise<[JsonValue](https://ts.viam.dev/types/JsonValue.html)>)

For more information, see the [TypeScript SDK Docs](https://ts.viam.dev/classes/InputControllerClient.html#getstatus).

{{% /tab %}}
{{< /tabs >}}

### GetResourceName

Get the `ResourceName` for this input controller.

{{< tabs >}}
{{% tab name="Python" %}}

**Parameters:**

- `name` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (required): The name of the Resource.

**Returns:**

- ([viam.proto.common.ResourceName](https://python.viam.dev/autoapi/viam/proto/common/index.html#viam.proto.common.ResourceName)): :   The ResourceName of this Resource.

**Example:**

```python {class="line-numbers linkable-line-numbers"}
my_input_controller_name = Controller.get_resource_name("my_input_controller")
```

For more information, see the [Python SDK Docs](https://python.viam.dev/autoapi/viam/components/input/client/index.html#viam.components.input.client.ControllerClient.get_resource_name).

{{% /tab %}}
{{% tab name="Go" %}}

**Parameters:**

- None.

**Returns:**

- [(Name)](https://pkg.go.dev/go.viam.com/rdk@v0.89.0/resource#Name)

**Example:**

```go {class="line-numbers linkable-line-numbers"}
myInputController, err := input.FromProvider(machine, "my_input_controller")

err = myInputController.Name()
```

For more information, see the [Go SDK Docs](https://pkg.go.dev/go.viam.com/rdk/resource#Resource).

{{% /tab %}}
{{% tab name="TypeScript" %}}

**Parameters:**

- None.

**Returns:**

- (string): The name of the resource.

**Example:**

```ts {class="line-numbers linkable-line-numbers"}
input_controller.name
```

For more information, see the [TypeScript SDK Docs](https://ts.viam.dev/classes/InputControllerClient.html#name).

{{% /tab %}}
{{< /tabs >}}

### Close

Safely shut down the resource and prevent further use.

{{< tabs >}}
{{% tab name="Python" %}}

**Parameters:**

- None.

**Returns:**

- None.

**Example:**

```python {class="line-numbers linkable-line-numbers"}
my_controller = Controller.from_robot(robot=machine, name="my_controller")
await my_controller.close()
```

For more information, see the [Python SDK Docs](https://python.viam.dev/autoapi/viam/components/input/client/index.html#viam.components.input.client.ControllerClient.close).

{{% /tab %}}
{{% tab name="Go" %}}

**Parameters:**

- `ctx` [(Context)](https://pkg.go.dev/context#Context): A Context carries a deadline, a cancellation signal, and other values across API boundaries.

**Returns:**

- [(error)](https://pkg.go.dev/builtin#error): An error, if one occurred.

**Example:**

```go {class="line-numbers linkable-line-numbers"}
myInputController, err := input.FromProvider(machine, "my_input_controller")

err = myInputController.Close(context.Background())
```

For more information, see the [Go SDK Docs](https://pkg.go.dev/go.viam.com/rdk/resource#Resource).

{{% /tab %}}
{{< /tabs >}}


## API types

The `input` API defines the following types:

### Event object

Each `Event` object represents a singular event from the input device, and has four fields:

1. `Time`: `time.Time` the event occurred.
2. `Event`: `EventType` indicating the type of event (for example, a specific button press or axis movement).
3. `Control`: `Control` indicating which [Axis](#axis-controls), [Button](/reference/apis/components/input-controller/#button-controls), or Pedal on the controller has been changed.
4. `Value`: `float64` indicating the position of an [Axis](/reference/apis/components/input-controller/#axis-controls) or the state of a [Button](/reference/apis/components/input-controller/#button-controls) on the specified control.

#### EventType field

A string-like type indicating the specific type of input event, such as a button press or axis movement.

- To select for events of all type when registering callback function with [RegisterControlCallback](/reference/apis/components/input-controller/#registercontrolcallback), you can use `AllEvents` as your `EventType`.
- The registered function is then called in addition to any other callback functions you've registered, every time an `Event` happens on your controller.
  This is useful for debugging without interrupting normal controls, or for capturing extra or unknown events.

Registered `EventTypes` definitions:




### Python

```python
ALL_EVENTS = "AllEvents"
"""
Callbacks registered for this event will be called in ADDITION to other
registered event callbacks.
"""

CONNECT = "Connect"
"""
Sent at controller initialization, and on reconnects.
"""

DISCONNECT = "Disconnect"
"""
If unplugged, or wireless/network times out.
"""

BUTTON_PRESS = "ButtonPress"
"""
Typical key press.
"""

BUTTON_RELEASE = "ButtonRelease"
"""
Key release.
"""

BUTTON_HOLD = "ButtonHold"
"""
Key is held down. This will likely be a repeated event.
"""

BUTTON_CHANGE = "ButtonChange"
"""
Both up and down for convenience during registration, not typically emitted.
"""

POSITION_CHANGE_ABSOLUTE = "PositionChangeAbs"
"""
Absolute position is reported via Value, a la joysticks.
"""

POSITION_CHANGE_RELATIVE = "PositionChangeRel"
"""
Relative position is reported via Value, a la mice, or simulating axes with
up/down buttons.
"""
```
See [the Python SDK Docs](https://python.viam.dev/autoapi/viam/components/input/input/index.html#viam.components.input.EventType) for the most current version of supported `EventTypes`.

### Go

```go
// Callbacks registered for this event will be called in ADDITION to other registered event callbacks.
AllEvents EventType = "AllEvents"

// Sent at controller initialization, and on reconnects.
Connect EventType = "Connect"

// If unplugged, or wireless/network times out.
Disconnect EventType = "Disconnect"

// Typical key press.
ButtonPress EventType = "ButtonPress"

// Key release.
ButtonRelease EventType = "ButtonRelease"

// Key is held down. This will likely be a repeated event.
ButtonHold EventType = "ButtonHold"

// Both up and down for convenience during registration, not typically emitted.
ButtonChange EventType = "ButtonChange"

// Absolute position is reported via Value, a la joysticks.
PositionChangeAbs EventType = "PositionChangeAbs"

// Relative position is reported via Value, a la mice, or simulating axes with up/down buttons.
PositionChangeRel EventType = "PositionChangeRel"
```
See [the Viam RDK](https://github.com/viamrobotics/rdk/blob/main/components/input/input.go) for the most current version of supported `EventTypes`.



#### Control field

A string representing the physical input location, like a specific axis or button, of your `Controller` that the [Event Object](#event-object) is coming from.

Registered `Control` types are defined as follows:




### Python

```python
# Axes
ABSOLUTE_X = "AbsoluteX"
ABSOLUTE_Y = "AbsoluteY"
ABSOLUTE_Z = "AbsoluteZ"
ABSOLUTE_RX = "AbsoluteRX"
ABSOLUTE_RY = "AbsoluteRY"
ABSOLUTE_RZ = "AbsoluteRZ"
ABSOLUTE_HAT0_X = "AbsoluteHat0X"
ABSOLUTE_HAT0_Y = "AbsoluteHat0Y"

# Buttons
BUTTON_SOUTH = "ButtonSouth"
BUTTON_EAST = "ButtonEast"
BUTTON_WEST = "ButtonWest"
BUTTON_NORTH = "ButtonNorth"
BUTTON_LT = "ButtonLT"
BUTTON_RT = "ButtonRT"
BUTTON_LT2 = "ButtonLT2"
BUTTON_RT2 = "ButtonRT2"
BUTTON_L_THUMB = "ButtonLThumb"
BUTTON_R_THUMB = "ButtonRThumb"
BUTTON_SELECT = "ButtonSelect"
BUTTON_START = "ButtonStart"
BUTTON_MENU = "ButtonMenu"
BUTTON_RECORD = "ButtonRecord"
BUTTON_E_STOP = "ButtonEStop"

# Pedals
ABSOLUTE_PEDAL_ACCELERATOR = "AbsolutePedalAccelerator"
ABSOLUTE_PEDAL_BRAKE = "AbsolutePedalBrake"
ABSOLUTE_PEDAL_CLUTCH = "AbsolutePedalClutch"
```
See [the Python SDK Docs](https://python.viam.dev/autoapi/viam/components/input/input/index.html#viam.components.input.Control) for the most current version of supported `Control` types.

### Go

```go
// Axes.
AbsoluteX     Control = "AbsoluteX"
AbsoluteY     Control = "AbsoluteY"
AbsoluteZ     Control = "AbsoluteZ"
AbsoluteRX    Control = "AbsoluteRX"
AbsoluteRY    Control = "AbsoluteRY"
AbsoluteRZ    Control = "AbsoluteRZ"
AbsoluteHat0X Control = "AbsoluteHat0X"
AbsoluteHat0Y Control = "AbsoluteHat0Y"

// Buttons.
ButtonSouth  Control = "ButtonSouth"
ButtonEast   Control = "ButtonEast"
ButtonWest   Control = "ButtonWest"
ButtonNorth  Control = "ButtonNorth"
ButtonLT     Control = "ButtonLT"
ButtonRT     Control = "ButtonRT"
ButtonLT2    Control = "ButtonLT2"
ButtonRT2    Control = "ButtonRT2"
ButtonLThumb Control = "ButtonLThumb"
ButtonRThumb Control = "ButtonRThumb"
ButtonSelect Control = "ButtonSelect"
ButtonStart  Control = "ButtonStart"
ButtonMenu   Control = "ButtonMenu"
ButtonRecord Control = "ButtonRecord"
ButtonEStop  Control = "ButtonEStop"

// Pedals.
AbsolutePedalAccelerator Control = "AbsolutePedalAccelerator"
AbsolutePedalBrake       Control = "AbsolutePedalBrake"
AbsolutePedalClutch      Control = "AbsolutePedalClutch"
```
See [GitHub](https://github.com/viamrobotics/rdk/blob/main/components/input/input.go) for the most current version of supported `Control` types.



### Axis controls

> **Support Notice:**
> 
> Currently, only `Absolute` axes are supported.
> 
> `Relative` axes, reporting a relative change in distance, used by devices like mice and trackpads, will be supported in the future.

Analog devices like joysticks and thumbsticks which return to center/neutral on their own use `Absolute` axis control types.

These controls report a `PositionChangeAbs` [EventType](#eventtype-field).

**Value:** A `float64` between `-1.0` and `+1.0`.

- `1.0`: Maximum position in the positive direction.
- `0.0`: Center, neutral position.
- `-1.0`: Maximum position in the negative direction.

#### AbsoluteXY axes

If your input controller has an analog stick, this is what the stick's controls report as.

Alternatively, if your input controller has _two_ analog sticks, this is what the left joystick's controls report as.

| Name        | `-1.0`        | `0.0`   | `1.0`           |
| ----------- | ------------- | ------- | --------------- |
| `AbsoluteX` | Stick Left    | Neutral | Stick Right     |
| `AbsoluteY` | Stick Forward | Neutral | Stick Backwards |

#### AbsoluteR-XY axes

If your input controller has _two_ analog sticks, this is what the right joystick's controls report as.

| Name         | `-1.0`        | `0.0`   | `1.0`           |
| ------------ | ------------- | ------- | --------------- |
| `AbsoluteRX` | Stick Left    | Neutral | Stick Right     |
| `AbsoluteRY` | Stick Forward | Neutral | Stick Backwards |

- For `Y` axes, the positive direction is "nose up," and indicates _pulling_ back on the joystick.

#### Hat/D-Pad axes

If your input controller has a directional pad with analog buttons on the pad, this is what those controls report as.

<!-- prettier-ignore -->
| Name | `-1.0` | `0.0` | `1.0` |
| ---- | ------ | ----- | ----- |
| `AbsoluteHat0X` | Left DPAD Button Press | Neutral | Right DPAD Button Press |
| `AbsoluteHat0Y` | Up DPAD Button Press | Neutral | Down DPAD Button Press |

#### Z axes (analog trigger sticks)

> **Info:**
> 
> Devices like analog triggers and gas or brake pedals use `Absolute` axes, but they only report position change in the positive direction.
> The neutral point of the axes is still `0.0`.

| Name         | `-1.0` | `0.0`   | `1.0`        |
| ------------ | ------ | ------- | ------------ |
| `AbsoluteZ`  |        | Neutral | Stick Pulled |
| `AbsoluteRZ` |        | Neutral | Stick Pulled |

`Z` axes are usually not present on most controller joysticks.

If present, they are typically analog trigger sticks, and unidirectional, scaling only from `0` to `1.0` as they are pulled, as shown above.

`AbsoluteZ` is reported if there is one trigger stick, and `AbsoluteZ` (left) and `AbsoluteRZ` (right) is reported if there are two trigger sticks.

Z axes can be present on flight-style joysticks, reporting _yaw_, or left/right rotation, as shown below.
This is not common.

| Name         | `-1.0`         | `0.0`   | `1.0`           |
| ------------ | -------------- | ------- | --------------- |
| `AbsoluteZ`  | Stick Left Yaw | Neutral | Stick Right Yaw |
| `AbsoluteRZ` | Stick Left Yaw | Neutral | Stick Right Yaw |

### Button controls

Button Controls report either `ButtonPress` or `ButtonRelease` as their [EventType](#eventtype-field).

**Value:**

- `0`: released
- `1`: pressed

#### Action buttons (ABXY)

If your input controller is a gamepad with digital action buttons, this is what the controls for these buttons report as.

> **Tip:**
> 
> As different systems label the actual buttons differently, we use compass directions for consistency.
> 
> <ul>
> <li>`ButtonSouth` corresponds to “B” on Nintendo, “A” on XBox, and “X” on Playstation.</li>
> <li>`ButtonNorth` corresponds to “X” on Nintendo, “Y” on XBox, and “Triangle” on Playstation.</li>
> </ul>

<!-- prettier-ignore -->
| Diamond 4-Action Button Pad | Rectangle 4-Action Button Pad |
| - | - |
| <table> <tr><th>Name</th><th>Description</th></tr><tr><td>`ButtonNorth`</td><td>Top</td></tr><tr><td>`ButtonSouth`</td><td>Bottom</td></tr><tr><td>`ButtonEast`</td><td>Right</td></tr><tr><td>`ButtonWest`</td><td>Left</td></tr> </table> | <table> <tr><th>Name</th><th>Description</th></tr><tr><td>`ButtonNorth`</td><td>Top-left</td></tr><tr><td>`ButtonSouth`</td><td>Bottom-right</td></tr><tr><td>`ButtonEast`</td><td>Top-right</td></tr><tr><td>`ButtonWest`</td><td>Bottom-left</td></tr> </table> |

<!-- prettier-ignore -->
| Horizontal 3-Action Button Pad | Vertical 3-Action Button Pad |
| - | - |
| <table> <tr><th>Name</th><th>Description</th></tr><tr><td>`ButtonWest`</td><td>Left</td></tr><tr><td>`ButtonSouth`</td><td>Center</td></tr><tr><td>`ButtonEast`</td><td>Right</td></tr> </table> | <table> <tr><th>Name</th><th>Description</th></tr><tr><td>`ButtonWest`</td><td>Top</td></tr><tr><td>`ButtonSouth`</td><td>Center</td></tr><tr><td>`ButtonEast`</td><td>Bottom</td></tr> </table> |

<!-- prettier-ignore -->
| Horizontal 2-Action Button Pad | Vertical 2-Action Button Pad |
| - | - |
| <table> <tr><th>Name</th><th>Description</th></tr><tr><td>`ButtonEast`</td><td>Right</td></tr><tr><td>`ButtonSouth`</td><td>Left</td></tr><tr> </table> | <table> <tr><th>Name</th><th>Description</th></tr><tr><td>`ButtonEast`</td><td>Top</td></tr><tr><td>`ButtonSouth`</td><td>Bottom</td></tr> </table> |

#### Trigger buttons (bumpers)

If your input controller is a gamepad with digital trigger buttons, this is what the controls for those buttons report as.

<!-- prettier-ignore -->
| 2-Trigger Button Pad | 4-Trigger Button Pad |
| - | - |
| <table> <tr><th>Name</th><th>Description</th></tr><tr><td>`ButtonLT`</td><td>Left</td></tr><tr><td>`ButtonRT`</td><td>Right</td></tr> </table> | <table> <tr><th>Name</th><th>Description</th></tr><tr><td>`ButtonLT`</td><td>Top-left</td></tr><tr><td>`ButtonRT`</td><td>Top-right</td></tr><tr><td>`ButtonLT2`</td><td>Bottom-left</td></tr><tr><td>`ButtonRT2`</td><td>Bottom-right</td></tr> </table> |

#### Digital buttons for sticks

If your input controller is a gamepad with "clickable" thumbsticks, this is what thumbstick presses report as.

| Name           | Description                     |
| -------------- | ------------------------------- |
| `ButtonLThumb` | Left or upper button for stick  |
| `ButtonRThumb` | Right or lower button for stick |

#### Miscellaneous buttons

Many devices have additional buttons.
If your input controller is a gamepad with these common buttons, this is what the controls for those buttons report as.

| Name           | Description                                         |
| -------------- | --------------------------------------------------- |
| `ButtonSelect` | Select or -                                         |
| `ButtonStart`  | Start or +                                          |
| `ButtonMenu`   | Usually the central "Home" or Xbox/PS "Logo" button |
| `ButtonRecord` | Recording                                           |
| `ButtonEStop`  | Emergency Stop (on some industrial controllers)     |

## Usage examples

### Control a wheeled base with a Logitech G920 steering wheel controller

The following Python code is an example of controlling a wheeled [base](/components/base/)
 with a Logitech G920 steering wheel controller, configured as a `gamepad` input controller.

```python {id="python-example" class="line-numbers linkable-line-numbers"}
import asyncio

from viam.components.base import Base
from viam.components.input import Control, Controller, EventType
from viam.proto.common import Vector3
from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions

turn_amt = 0
modal = 0
cmd = {}


async def connect_robot(host, api_key, api_key_id):
    opts = RobotClient.Options.with_api_key(
      api_key=api_key,
      api_key_id=api_key_id
    )
    return await RobotClient.at_address(host, opts)


def handle_turning(event):
    global turn_amt
    turn_amt = -event.value
    print("turning:", turn_amt)


def handle_brake(event):
    if event.value != 0:
        print("braking!:", event.value)
        global cmd
        cmd = {"y": 0}
        print("broke")


def handle_accelerator(event):
    print("moving!:", event.value)
    global cmd
    accel = (event.value - 0.1) / 0.9
    if event.value < 0.1:
        accel = 0

    cmd = {"y": accel}


def handle_clutch(event):
    print("moving!:", event.value)
    global cmd
    accel = (event.value - 0.1) / 0.9
    if event.value < 0.1:
        accel = 0

    cmd = {"y": -accel}


async def handleController(controller):
    resp = await controller.get_events()
    # Show the input controller's buttons/axes
    print(f'Controls:\n{resp}')

    if Control.ABSOLUTE_PEDAL_ACCELERATOR in resp:
        controller.register_control_callback(
            Control.ABSOLUTE_PEDAL_ACCELERATOR,
            [EventType.POSITION_CHANGE_ABSOLUTE],
            handle_accelerator)
    else:
        print("Accelerator Pedal not found! Exiting! Are your steering wheel" +
              " and pedals hooked up?")
        exit()

    if Control.ABSOLUTE_PEDAL_BRAKE in resp:
        controller.register_control_callback(
            Control.ABSOLUTE_PEDAL_BRAKE,
            [EventType.POSITION_CHANGE_ABSOLUTE],
            handle_brake)
    else:
        print("Brake Pedal not found! Exiting!")
        exit()

    if Control.ABSOLUTE_PEDAL_CLUTCH in resp:
        controller.register_control_callback(
            Control.ABSOLUTE_PEDAL_CLUTCH,
            [EventType.POSITION_CHANGE_ABSOLUTE],
            handle_clutch)
    else:
        print("Accelerator Pedal not found! Exiting! Are your steering wheel" +
              " and pedals hooked up?")
        exit()

    if Control.ABSOLUTE_X in resp:
        controller.register_control_callback(
            Control.ABSOLUTE_X,
            [EventType.POSITION_CHANGE_ABSOLUTE],
            handle_turning)
    else:
        print("Wheel not found! Exiting!")
        exit()

    while True:
        await asyncio.sleep(0.01)
        global cmd
        if "y" in cmd:
            res = await modal.set_power(
                linear=Vector3(x=0, y=cmd["y"], z=0),
                angular=Vector3(x=0, y=0, z=turn_amt))
            cmd = {}
            print(res)


async def main():
    # TODO: Add your machine address and API key values from the CONNECT tab.
    g920_robot = await connect_robot(
        "<MACHINE-ADDRESS>", "API_KEY", "API_KEY_ID")
    modal_robot = await connect_robot(
        "<MACHINE-ADDRESS>", "API_KEY", "API_KEY_ID")

    g920 = Controller.from_robot(g920_robot, 'wheel')
    global modal
    modal = Base.from_robot(modal_robot, 'modal-base-server:base')

    await handleController(g920)

    await g920_robot.close()
    await modal_robot.close()

if __name__ == '__main__':
    asyncio.run(main())
```

### Drive a robot with four wheels and a skid steer platform

The following Go code is part of an example of using an input controller to drive a robot with four wheels & a skid steer platform.

The `motorCtl` callback function controls 5 motors: left front & back `FL` `BL`, right front & back `FL` `BL`, and a `winder` motor that raises and lowers a front-end like a bulldozer.

The `event.Control` logic is registered as a callback function to determine the case for setting the power of each motor from which button is pressed on the input controller.

```go {id="go-example" class="line-numbers linkable-line-numbers"}
// Define a single callback function
motorCtl := func(ctx context.Context, event input.Event) {
    if event.Event != input.PositionChangeAbs {
        return
    }

    speed := float32(math.Abs(event.Value))

    // Handle input events, commands to set the power of motor components (SetPower method)
    switch event.Control {
        case input.AbsoluteY:
            motorFL.SetPower(ctx, speed, nil)
            motorBL.SetPower(ctx, speed, nil)
        case input.AbsoluteRY:
            motorFR.SetPower(ctx, speed * -1, nil)
            motorBR.SetPower(ctx, speed * -1, nil)
        case input.AbsoluteZ:
            motorWinder.SetPower(ctx, speed, nil)
        case input.AbsoluteRZ:
            motorWinder.SetPower(ctx, speed * -1, nil)
    }
}

// Registers callback from motorCtl for a selected set of axes
for _, control := range []input.Control{input.AbsoluteY, input.AbsoluteRY, input.AbsoluteZ, input.AbsoluteRZ} {
    err = g.RegisterControlCallback(ctx, control, []input.EventType{input.PositionChangeAbs}, motorCtl)
}
```

