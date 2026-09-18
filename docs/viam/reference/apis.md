# Viam's Client APIs

Access and control your machine or fleet with the SDKs' client libraries for the resource and robot APIs.
> Source: https://docs.viam.com/reference/apis/


Every Viam [resource](/reference/glossary/#term-resource)
 exposes an [application programming interface (API)](https://en.wikipedia.org/wiki/API) described through [protocol buffers](https://developers.google.com/protocol-buffers).

The API methods provided by the SDKs for each of these resource APIs wrap gRPC client requests to the machine when you execute your program, providing you a convenient interface for accessing information about and controlling the [resources](/reference/glossary/#term-resource)
 you have [configured](/hardware/configure-hardware/) on your machine.

## Platform APIs

<div class="card-container">
  <div class="row-no-margin">
**[Fleet Management API](/reference/apis/fleet/)**

Create and manage organizations, locations, and machines, get logs from individual machines, and manage fragments and permissions.

**[Data Client API](/reference/apis/data-client/)**

Upload, download, filter, tag or perform other tasks on data like images or sensor readings.

**[Machine Management API](/reference/apis/robot/)**

Manage your machines: connect to your machine, retrieve status information, and send commands remotely.

**[ML Training Client API](/reference/apis/ml-training-client/)**

Submit and manage ML training jobs running on Viam.

**[Billing Client API](/reference/apis/billing-client/)**

Retrieve billing information from Viam.

**[Session Management API](/reference/apis/sessions/)**

Manage sessions, heartbeats, and safety timeouts for connected clients.


</div>
</div>

## Component APIs

These APIs provide interfaces for controlling and getting information from the [components](/reference/glossary/#term-component)
 of a machine:

<div class="card-container">
  <div class="row-no-margin">
**[Component APIs overview](/reference/apis/components/overview/)**

See every component API and its methods at a glance in one compact grid.

</div>
</div>

<div class="card-container">
  <div class="row-no-margin">
<div class="col hover-card "><a href="/reference/apis/components/arm/"><div class="small-hover-card-div"><div>Arm API</div><p>Give commands to your arm components for linear motion planning.</p></div>
    </a></div>

<div class="col hover-card "><a href="/reference/apis/components/audio-in/"><div ><div>Audio in API</div><p>Give commands to your audio in components.</p></div>
    </a></div>

<div class="col hover-card "><a href="/reference/apis/components/audio-out/"><div ><div>Audio out API</div><p>Give commands to your audio out components.</p></div>
    </a></div>

<div class="col hover-card "><a href="/reference/apis/components/base/"><div class="small-hover-card-div"><div>Base API</div><p>Give commands for moving all configured components attached to a mobile platform as a whole without needing to send commands to individual components.</p></div>
    </a></div>

<div class="col hover-card "><a href="/reference/apis/components/board/"><div class="small-hover-card-div"><div>Board API</div><p>Give commands for setting GPIO pins to high or low, setting PWM, and working with analog and digital interrupts.</p></div>
    </a></div>

<div class="col hover-card "><a href="/reference/apis/components/button/"><div class="small-hover-card-div"><div>Button API</div><p>Give commands for getting presses from a physical button.</p></div>
    </a></div>

<div class="col hover-card "><a href="/reference/apis/components/camera/"><div class="small-hover-card-div"><div>Camera API</div><p>Give commands for getting images or point clouds.</p></div>
    </a></div>

<div class="col hover-card "><a href="/reference/apis/components/encoder/"><div class="small-hover-card-div"><div>Encoder API</div><p>Give commands for getting the position of a motor or a joint in ticks or degrees.</p></div>
    </a></div>

<div class="col hover-card "><a href="/reference/apis/components/gantry/"><div class="small-hover-card-div"><div>Gantry API</div><p>Give commands for coordinated control of one or more linear actuators.</p></div>
    </a></div>

<div class="col hover-card "><a href="/reference/apis/components/generic/"><div class="small-hover-card-div"><div>Generic API</div><p>Give commands for running custom model-specific commands using DoCommand on your generic components.</p></div>
    </a></div>

<div class="col hover-card "><a href="/reference/apis/components/gripper/"><div class="small-hover-card-div"><div>Gripper API</div><p>Give commands for opening and closing a gripper device.</p></div>
    </a></div>

<div class="col hover-card "><a href="/reference/apis/components/input-controller/"><div class="small-hover-card-div"><div>Input controller API</div><p>Give commands to register callbacks for events, allowing you to use input devices to control your machines.</p></div>
    </a></div>

<div class="col hover-card "><a href="/reference/apis/components/motor/"><div class="small-hover-card-div"><div>Motor API</div><p>Give commands to operate a motor or get its current status.</p></div>
    </a></div>

<div class="col hover-card "><a href="/reference/apis/components/movement-sensor/"><div class="small-hover-card-div"><div>Movement sensor API</div><p>Give commands for getting the current GPS location, linear velocity and acceleration, angular velocity and acceleration and heading.</p></div>
    </a></div>

<div class="col hover-card "><a href="/reference/apis/components/power-sensor/"><div class="small-hover-card-div"><div>Power sensor API</div><p>Commands for getting measurements of voltage, current, and power consumption.</p></div>
    </a></div>

<div class="col hover-card "><a href="/reference/apis/components/sensor/"><div class="small-hover-card-div"><div>Sensor API</div><p>Give commands for getting sensor readings.</p></div>
    </a></div>

<div class="col hover-card "><a href="/reference/apis/components/servo/"><div class="small-hover-card-div"><div>Servo API</div><p>Give commands for controlling the angular position of a servo precisely or getting its current status.</p></div>
    </a></div>

<div class="col hover-card "><a href="/reference/apis/components/switch/"><div class="small-hover-card-div"><div>Switch API</div><p>Give commands for getting the state of a physical switch that has two or more discrete positions.</p></div>
    </a></div>

</div>
</div>

## Service APIs

These APIs provide interfaces for controlling and getting information from the services you configured on a machine.

<div class="card-container">
  <div class="row-no-margin">
**[Service APIs overview](/reference/apis/services/overview/)**

See every service API and its methods at a glance in one compact grid.

</div>
</div>

<div class="card-container">
  <div class="row-no-margin">
<div class="col hover-card "><a href="/reference/apis/services/data/"><div class="small-hover-card-div"><div>Data management service API</div><p>Give commands to your data management service to sync data stored on the machine it is deployed on to the cloud.</p></div>
    </a></div>

<div class="col hover-card "><a href="/reference/apis/services/vision/"><div class="small-hover-card-div"><div>Vision service API</div><p>Give commands to get detections, classifications, or point cloud objects, depending on the ML model the vision service is using.</p></div>
    </a></div>

<div class="col hover-card "><a href="/reference/apis/services/ml/"><div class="small-hover-card-div"><div>ML model service API</div><p>Give commands to your ML model service to make inferences based on a provided ML model.</p></div>
    </a></div>

<div class="col hover-card "><a href="/reference/apis/services/motion/"><div class="small-hover-card-div"><div>Motion service API</div><p>Give commands to move a machine&#39;s components from one location or pose to another.</p></div>
    </a></div>

<div class="col hover-card "><a href="/reference/apis/services/generic/"><div class="small-hover-card-div"><div>Generic service API</div><p>Give commands to your generic components for running model-specific commands using DoCommand.</p></div>
    </a></div>

<div class="col hover-card "><a href="/reference/apis/services/base-rc/"><div class="small-hover-card-div"><div>Base Remote Control service API</div><p>Give commands to get a list of inputs from the controller that are being monitored for that control mode.</p></div>
    </a></div>

<div class="col hover-card "><a href="/reference/apis/services/discovery/"><div ><div>Discovery service API</div><p>Reveal which resources are available to configure on a machine based on the hardware that is physically present.</p></div>
    </a></div>

<div class="col hover-card "><a href="/reference/apis/services/world-state-store/"><div class="small-hover-card-div"><div>World state store service API</div><p>List, get, and stream the transforms a world state store service publishes for the 3D scene to draw.</p></div>
    </a></div>

</div>
</div>

