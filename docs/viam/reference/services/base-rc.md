# Base remote control service

The base remote control service allows you to remotely control a base with an input controller like a gamepad.
> Source: https://docs.viam.com/reference/services/base-rc/


## Used with

<div class="card-container">
  <div class="row-no-margin">








  
    <div class="relatedcard ">
      <a href="/reference/components/base/" target="_blank" title="Base">
          
            




    
    
    
<picture>

  
    
<img src="/icons/components/base.svg" alt="Base" class="" id="" style="" loading="lazy">
  

</picture>


          
          <p>
            
              Base*
            
          </p>
      </a>
    </div>
  










  
    <div class="relatedcard ">
      <a href="/reference/components/input-controller/" target="_blank" title="Input controller">
          
            




    
    
    
<picture>

  
    
<img src="/icons/components/controller.svg" alt="Input controller" class="" id="" style="" loading="lazy">
  

</picture>


          
          <p>
            
              Input controller*
            
          </p>
      </a>
    </div>
  










  
    <div class="relatedcard ">
      <a href="/reference/components/movement-sensor/" target="_blank" title="Movement sensor">
          
            




    
    
    
<picture>

  
    
<img src="/icons/components/imu.svg" alt="Movement sensor" class="" id="" style="" loading="lazy">
  

</picture>


          
          <p>
            
              Movement sensor
            
          </p>
      </a>
    </div>
  


</div>
</div>

\* Required for use

\*\* Input controller is required hardware + related Viam component

The base remote control service implements an [input controller](/reference/components/input-controller/) as a remote control for a [base](/reference/components/base/).
This uses the [`input` API](/reference/apis/components/input-controller/) to make it easy to add remote drive controls for your rover or other mobile robot with a controller like a gamepad.

Add the base remote control service after configuring your machine with a base and input controller to control the linear and angular velocity of the base with the controller's button or joystick controls.

Control mode is determined by the configuration attribute `"control_mode"`, for which there are five options:

1. `"arrowControl"`: Arrow buttons control speed and angle
2. `"triggerSpeedControl"`: Trigger button controls speed and joystick controls angle
3. `"buttonControl"`: Four buttons (usually X, Y, A, B) control speed and angle
4. `"joystickControl"`: One joystick controls speed and angle
5. `"droneControl"`: Two joysticks control speed and angle

You can monitor the input from these controls in the **CONTROL** tab.

## Configuration

You must configure a [base](/reference/components/base/) with a [movement sensor](/reference/components/movement-sensor/) as part of your machine to be able to use a base remote control service.

First, make sure your base is physically assembled and powered on.
Then, configure the service:




### Builder

Navigate to the **CONFIGURE** tab of your machine’s page.
Click the **+** icon next to your machine part in the left-hand menu and select **Blocks**.
Select the `base remote control` type.
Enter a name or use the suggested name for your service and click **Add to machine**.

In your base remote control service’s configuration panel, copy and paste the following JSON object into the attributes field:

```json
{
  "base": "<your-base-name>",
  "input_controller": "<your-controller-name>"
}
```
Edit the attributes as applicable to your machine, according to the table below.

For example:

    
    
    

    
    

    
        
        
        
        
        
        
        
<picture>
    <source
        srcset="/services/base-rc/base-rc-ui-config_hu_7b5d750713c9df2e.webp 480w, /services/base-rc/base-rc-ui-config_hu_a282df203d1f862e.webp 768w, /services/base-rc/base-rc-ui-config_hu_5c6c78651b5fb722.webp 1200w"
        sizes="(min-width: 60rem) 80vw, (min-width: 40rem) 90vw, 100vw"
    />
    <img
        sizes="(min-width: 60rem) 80vw, (min-width: 40rem) 90vw, 100vw"
        srcset="/services/base-rc/base-rc-ui-config_hu_af6b8f2351060ac7.png 480w, /services/base-rc/base-rc-ui-config_hu_a6dd767f4b533d3f.png 768w, /services/base-rc/base-rc-ui-config_hu_ae887f30e678e86c.png 1024w"
        src="/services/base-rc/base-rc-ui-config.png"
        width="1528"
        height="1602"
        alt="An example configuration for a base remote control service."
        loading="lazy"
        style="width:1000px"
    >
</picture>

### JSON Template

```json
{
  "name": "<your-base-remote-control-service>",
  "api": "rdk:service:base_remote_control",
  "model": "rdk:builtin:builtin",
  "attributes": {
    "base": "<your-base-name>",
    "input_controller": "<your-controller-name>"
  }
}
```

### JSON Example

```json
{
  "name": "gamepad_service",
  "api": "rdk:service:base_remote_control",
  "model": "rdk:builtin:builtin",
  "attributes": {
    "base": "my-base",
    "input_controller": "my-input-controller",
    "control_mode": "arrowControl"
  }
}
```



Edit and fill in the attributes as applicable.
The following attributes are available for base remote control services:

<!-- prettier-ignore -->
| Name | Type | Required? | Description |
| ---- | ---- | --------- | ----------- |
| `base` | string | **Required** | The `name` of the [base](/reference/components/base/) you have configured for the base you are operating with this service. |
| `input_controller` | string | **Required** | The `name` of the [input controller](/reference/components/input-controller/) you have configured for the base you are operating with this service. |
| `control_mode` | string | Optional | The mode of remote control you want to use. <br> Options: <ul><li>`"arrowControl"`</li><li>`"triggerSpeedControl"`</li><li>`"buttonControl"`</li><li>`"joystickControl"`</li> <li>`"droneControl"`</li></ul> <br> Default: `"arrowControl"` |
| `max_angular_degs_per_sec` | float | Optional | The max angular velocity for the [base](/reference/components/base/) in degrees per second. |
| `max_linear_mm_per_sec` | float | Optional | The max linear velocity for the [base](/reference/components/base/) in meters per second. |

## API

The base remote control service supports the following methods:

<!-- prettier-ignore -->
| Method Name | Description |
| ----------- | ----------- |
| [`ControllerInputs`](/reference/apis/services/base-rc/#controllerinputs) | Get a list of inputs from the controller that are being monitored for that control mode. |
| [`Reconfigure`](/reference/apis/services/base-rc/#reconfigure) | Reconfigure this resource. |
| [`DoCommand`](/reference/apis/services/base-rc/#docommand) | Execute model-specific commands that are not otherwise defined by the service API. |
| [`GetResourceName`](/reference/apis/services/base-rc/#getresourcename) | Get the `ResourceName` for this instance of the generic service with the given name. |
| [`Close`](/reference/apis/services/base-rc/#close) | Close out of all remote control related systems. |


> **Tip:**
> 
> The following code examples assume that you have a machine configured with a [base](/reference/components/base/) named `"my_base"`, [input controller](/reference/components/input-controller/) named `"my_controller"`, and base remote control service named `"my_base_rc_service"`.
> Make sure to add the required code to connect to your machine and import any required packages at the top of your code file.
> Go to your machine’s **CONNECT** tab and select **API keys** to get your credentials, then use the code sample to connect to your machine.

### ControllerInputs

Get a list of inputs from the controller that are being monitored for that control mode.

{{< tabs >}}
{{% tab name="Go" %}}

**Parameters:**

- None.

**Returns:**

- [([]input.Control)](https://pkg.go.dev/go.viam.com/rdk/components/input#Control): A list of inputs from the controller that are being monitored for that control mode.

**Example:**

```go {class="line-numbers linkable-line-numbers"}
// Get the list of inputs from the controller that are being monitored for that control mode.
inputs := baseRCService.ControllerInputs()
```

For more information, see the [Go SDK Docs](https://pkg.go.dev/go.viam.com/rdk/services/baseremotecontrol#Service).

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

Execute model-specific commands that are not otherwise defined by the service API.
Most models do not implement `DoCommand`.
Any available model-specific commands should be covered in the model's documentation.
If you are implementing your own base remote control service and want to add features that have no corresponding built-in API method, you can implement them with [`DoCommand`](/reference/sdks/docommand/).

{{< tabs >}}
{{% tab name="Go" %}}

**Parameters:**

- `ctx` [(Context)](https://pkg.go.dev/context#Context): A Context carries a deadline, a cancellation signal, and other values across API boundaries.
- `cmd` [(map[string]interface{})](https://go.dev/blog/maps): The command to execute.

**Returns:**

- [(map[string]interface{})](https://pkg.go.dev/builtin#string): The command response.
- [(error)](https://pkg.go.dev/builtin#error): An error, if one occurred.

**Example:**

```go {class="line-numbers linkable-line-numbers"}
myBaseRemoteControlSvc, err := baseremotecontrol.FromProvider(machine, "my_base_remote_control_svc")

command := map[string]interface{}{"cmd": "test", "data1": 500}
result, err := myBaseRemoteControlSvc.DoCommand(context.Background(), command)
```

For more information, see the [Go SDK Docs](https://pkg.go.dev/go.viam.com/rdk/resource#Resource).

{{% /tab %}}
{{< /tabs >}}

### GetResourceName

Get the `ResourceName` for this instance of the generic service with the given name.

{{< tabs >}}
{{% tab name="Go" %}}

**Parameters:**

- None.

**Returns:**

- [(Name)](https://pkg.go.dev/go.viam.com/rdk@v0.89.0/resource#Name)

**Example:**

```go {class="line-numbers linkable-line-numbers"}
baseRCService, err := baseremotecontrol.FromProvider(machine, "my_baseRCService_svc")

err := baseRCService.Name()
```

For more information, see the [Go SDK Docs](https://pkg.go.dev/go.viam.com/rdk/resource#Resource).

{{% /tab %}}
{{< /tabs >}}

### Close

Close out of all remote control related systems.

{{< tabs >}}
{{% tab name="Go" %}}

**Parameters:**

- `ctx` [(Context)](https://pkg.go.dev/context#Context): A Context carries a deadline, a cancellation signal, and other values across API boundaries.

**Returns:**

- [(error)](https://pkg.go.dev/builtin#error): An error, if one occurred.

**Example:**

```go {class="line-numbers linkable-line-numbers"}
baseRCService, err := baseremotecontrol.FromProvider(machine, "my_baseRCService_svc")

err := baseRCService.Close(context.Background())
```

For more information, see the [Go SDK Docs](https://pkg.go.dev/go.viam.com/rdk/resource#Resource).

{{% /tab %}}
{{< /tabs >}}


