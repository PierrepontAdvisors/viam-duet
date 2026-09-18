# Glossary

A glossary that explains robotics and Viam-specific jargon.
> Source: https://docs.viam.com/reference/glossary/



### API {#term-api}

API stands for application programming interface.
An API defines the methods and data structures that allow different software components or systems to communicate with each other.

In the Viam platform, APIs are used extensively to:

- Control hardware components (motors, cameras, sensors, etc.)
- Access services (vision, motion, navigation, etc.)
- Manage machines and organizations
- Process and analyze data

These APIs are accessible through various [SDKs](/reference/apis/)
 in languages like Python, Go, and TypeScript.

### API Namespace Triplet {#term-api-namespace-triplet}

Every Viam [resource](/reference/glossary/#term-resource)
 implements an [application programming interface (API)](https://en.wikipedia.org/wiki/API) that describes how you can interact with that resource.

These APIs are organized by colon-delimited-triplet identifiers, in the form of `namespace:type:subtype`.

The `namespace` for built-in Viam resources is `rdk`, while the `type` is `component` or `service`.
`subtype` refers to a specific component or service, like a `camera` or `vision`.

One API can have various [models](/reference/glossary/#term-model)
, custom or built-in, but they all must conform to the same API definition.
This requirement ensures that when a resource of that model is deployed, you can [interface with it](/reference/sdks/) using the same [client API methods](/reference/apis/) you would when programming resources of the same API with a different model.

Each resource implements one and only one API.

For example:

- The API of the built-in component [camera](/hardware/common-components/add-a-camera/) is `rdk:component:camera`, which exposes methods such as `GetImages()`.
- The API of the built-in service [vision](/vision/configure/) is `rdk:service:vision`, which exposes methods such as `GetDetectionsFromCamera()`.

### Attribute {#term-attribute}

A configuration parameter of a resource.

### Base {#term-base}

A physical, mobile platform that the other parts of a mobile robot attach to.
For example, a wheeled rover, boat, or flying drone.

For more information see [Base Component](/hardware/common-components/add-a-base/).

### Blob storage {#term-blob-storage}

A cheap but slow storage medium.

### Board {#term-board}

A board is the signal wire hub of a machine that provides access to GPIO pins.

Examples of boards include Jetson, Raspberry Pi, or Numato.

For more information see [Board Component](/hardware/common-components/add-a-board/).

### Captive web portal {#term-captive-web-portal}

A captive portal is a web page that is automatically displayed to users often as a landing or log-in page when connecting to a network.

For more information see [captive portal](https://en.wikipedia.org/wiki/Captive_portal).

### Client Application {#term-client-application}

Client applications run business logic to operate your machine.

You can run a client application on the same [part](/reference/glossary/part/)
 that runs `viam-server`, or on a separate device.
Client applications typically use an [SDK](/reference/apis/)
 to talk to their machine.

### Component {#term-component}

A resource that often represents a physical piece of hardware in a machine which a computer controls; for example, a servo, a camera, or an arm.

Each component is typed by a proto API, such as the [component proto definitions](https://github.com/viamrobotics/api/tree/main/proto/viam/component).

For more information, see [Components](/hardware/configure-hardware/).

### Flash {#term-flashed}

Flashed or flashing refers to the process of writing an operating system, firmware, or other software directly to a device's non-volatile storage medium, such as an SD card, eMMC storage, or flash memory.

In the context of robotics and the Viam platform, flashing is commonly performed when:

- Setting up a new [Raspberry Pi](/reference/glossary/#term-pi)
 with an operating system
- Installing the Viam Micro-RDK on supported microcontrollers

The flashing process typically involves:

1. Downloading an image file (OS or firmware)
2. Using specialized software to write the image to the target device
3. Verifying the write was successful
4. Booting or resetting the device to load the new software

For example, when setting up a Raspberry Pi for use with Viam, you would "flash" Raspberry Pi OS to an SD card using the [Raspberry Pi Imager](/reference/device-setup/rpi-setup/#install-raspberry-pi-os) or similar software.

Flashing is different from regular software installation because it involves writing directly to storage at a low level, often replacing everything on the target storage medium.

### Fragment {#term-fragment}

A reusable configuration block that you can share across multiple machines.

For more information, see [Fragments](/fleet/reuse-configuration/).

### Frame {#term-frame}

A frame represents a coordinate system that describes the position and orientation of an object.
See also [frame system](/operate/reference/services/frame-system/)
.

The location of a frame is described in relation to its parent frame using rigid transformations rather than in absolute terms.

### Frame System {#term-frame-system}

The frame system holds reference frame information for the relative position of components in space.

### Gantry {#term-gantry}

A mechanical system that only uses linear motion to carry out a task; for example, the scaffolding of a 3D printer, which moves the print head around on motorized linear rails.

### gRPC {#term-grpc}

An open source, cross-platform, high performance Remote Procedure Call (RPC) framework initially developed at Google in 2015.
With gRPC, a client application can communicate directly with a server application on a different machine.
This framework can run in any environment and efficiently connect distributed applications and services.

For more information see [grpc.io](https://grpc.io/).

### Jobs {#term-job}

Jobs are automated tasks that run on machines at specified intervals to perform routine operations such as a task based on sensor readings, maintenance operations, and system checks.

The job scheduler is built into `viam-server` and executes configured jobs according to their specified schedules.
Each job targets a specific resource on your machine and calls a designated method at the scheduled intervals.

For more information, see [Schedule automated jobs](/fleet/schedule-jobs/).

### Location {#term-location}

A location is a virtual grouping of machines that allows you to organize machines and manage access to your fleet.

For more information, see [Manage Locations and Sub-Locations](/reference/).

### Machine {#term-machine}

A smart machine is an organizational concept, consisting of either one _[part](/reference/glossary/part/)
_, or multiple _parts_ working closely together to complete tasks.

### Machine Config {#term-machine-config}

The complete configuration of a single machine [part](/reference/glossary/part/)
, including components, services, and scheduled jobs.

For more information, see [Configuration](/hardware/configure-hardware/).

### Machine FQDN {#term-machine-fqdn}

The fully qualified domain name (FQDN) of a [machine](/fleet/machines/)
 in the Viam platform, typically in the format `<machine-name>.<location-id>.viam.cloud`.
Used to uniquely identify and access a machine through Viam cloud infrastructure.

### Machine ID {#term-machine-id}

A **Machine ID** is a unique identifier assigned to each [machine](/fleet/machines/)
 in the Viam platform.
This ID is used to identify and reference a specific machine within the Viam ecosystem.

Machine IDs are automatically generated when a new machine is created on Viam.
You can get it using the web UI and the [Fleet management API](/reference/apis/fleet/).

### ML {#term-ml}

ML stands for machine learning, a field of artificial intelligence that focuses on building systems that can learn from and make decisions based on data.

Viam provides tools for [training ML models](/train/custom-training-scripts/), [deploying them to machines](/vision/configure/), [running inference](/vision/object-detection/detect/), and [interpret visual data from cameras](/vision/object-detection/alert-on-detections/) to enable intelligent behavior in robotic systems.

### Model {#term-model}

A particular implementation of a [resource](/reference/glossary/#term-resource)
 [API](/reference/apis/).

Models allow you to control hardware or software of a similar category, such as motors, with a consistent set of methods as an interface, even if the underlying implementation differs.

For example, some _models_ of DC motors communicate using [GPIO](/hardware/common-components/add-a-board/), while other DC motors use serial protocols like the SPI bus.
Regardless, you can power any motor model that implements the `rdk:component:motor` API with the `SetPower()` method.

Models are either included with `viam-server` or provided through [modules](/reference/glossary/#term-module)
.
All models are uniquely namespaced as colon-delimited-triplets.
Built-in model names have the form `rdk:builtin:name`.
Modular resource model names have the form `namespace:module-name:model-name`.
See [Write your module](/build-modules/write-a-driver-module/#2-implement-the-resource-api) for more information.

### Model Namespace Triplet {#term-model-namespace-triplet}

[Models](/reference/glossary/#term-model)
 are uniquely namespaced as colon-delimited-triplets.
Modular resource model names have the form `namespace:module-name:model-name`, for example `esmeraldaLabs:sensors:moisture`.
Built-in model names have the form `rdk:builtin:name`, for example `rdk:builtin:gpio`.
See [Write your module](/build-modules/write-a-driver-module/#2-implement-the-resource-api) for more information.

### Modular Resource {#term-modular-resource}

A modular resource is a [model](/reference/glossary/#term-model)
 of a [component](/reference/glossary/#term-component)
 or [service](/reference/glossary/#term-service)
 provided by a [module](/reference/glossary/#term-module)
.
A modular resource runs in a module process.
This differs from built-in resources, which run as part of `viam-server`.

For more information see the [Create a module](/build-modules/write-a-driver-module/#2-implement-the-resource-api).

### Module {#term-module}

A _module_ is a code package which provides one or more [modular resources](/reference/glossary/#term-modular-resource)
, which add [resource](/reference/glossary/#term-resource)
 [types](/reference/glossary/#term-type)
 or [models](/reference/glossary/#term-model)
, integrations, or control logic for your machines.
Modules run alongside `viam-server` as separate process, communicating with `viam-server` over UNIX sockets.

You can [create your own module](/build-modules/write-a-driver-module/) or [add existing modules from the registry](/hardware/configure-hardware/).

### MQL {#term-mql}

MQL is the [MongoDB query language](https://www.mongodb.com/docs/manual/tutorial/query-documents/), similar to [SQL](/reference/glossary/#term-sql)
 but specific to the MongoDB document model.

You can use MQL to query data that you have synced to Viam using the [data management service](/data/capture-sync/capture-and-sync-data/).

### Organization {#term-organization}

An organization or org is the highest level grouping in the Viam platform, which generally represents a company, or other institution.
Every [location](/manage/reference/organize/)
 is grouped into an organization.
You can also have organizations for departments or other entities, or for personal use.

For more information, see [Organize your machines](/reference/).

### Origin frame {#term-origin-frame}

The origin frame is the frame at the base of an arm, gantry, or other component.
This is typically the point at the center of where the component is mounted to a table or stand.

Every component that has a kinematics chain has an origin frame and an end effector frame, for example `my_arm_origin` and `my_arm`.

If you parent a gripper to the arm's `my_arm` frame, the frame system will know the gripper is at the end of the arm.
If you mistakenly parent the gripper to the arm's `my_arm_origin` frame, the frame system will think the gripper is at the base of the arm, and the gripper will not move when you move the arm.

For more information, see [How the frame system works](/reference/).

### Package {#term-package}

A _package_ is an archive, module, ML model, SLAM map, or other bundle of binary code.

Packages are used to deploy software to machines.

### Part {#term-part}

Smart machines are organized into _parts_, where each part represents a computer (a single-board computer, desktop, laptop, or other computer) running `viam-server`, the hardware [components](/reference/glossary/#term-component)
 attached to it, and any [services](/reference/glossary/#term-service)
 or other resources running on it.

### Pi {#term-pi}

Pi is short for Raspberry Pi, a series of small, affordable single-board computers developed by the Raspberry Pi Foundation.
These credit card-sized computers are widely used in robotics, IoT projects, education, and DIY electronics.

Viam supports many different devices including Raspberry Pis as host computers for running `viam-server`.

To set up a Raspberry Pi, see [the Raspberry Pi setup instructions](/reference/device-setup/rpi-setup/).

### Pin Number {#term-pin-number}

A pin number is the physical index of a pin on a [board](/components/board/)
.

This number is distinct from the GPIO number assigned to general purpose input/output (GPIO) pins.
For example, pin number "11" on a NVIDIA Jetson Nano is GPIO "50", and pin number "11" on a Raspberry Pi 4 is GPIO "17".
When Viam documentation refers to pin number, it will always mean the pin's physical index and not GPIO number.

Pin numbers are found on a board's pinout diagram and datasheet.

### Protocol Buffers (Protobuf) {#term-protobuf}

A free and open-source, language-neutral, cross-platform data format for serializing structured data.

Protocol Buffers are useful in developing programs that communicate with each other over a network or for storing data.

### RDK (Robot Development Kit) {#term-rdk}

Viam’s Robot Development Kit (RDK) is the [open-source](https://github.com/viamrobotics/rdk), on-machine portion of the Viam platform, that provides `viam-server` and the Go SDK.

### Remote part {#term-remote-part}

A machine part which is controlled by another machine part.

### Resource {#term-resource}

Resources are individual, addressable elements of a machine.

[Parts](/reference/glossary/part/)
 can operate multiple types of resources:

- physical [components](/reference/glossary/#term-component)

- software [services](/reference/glossary/#term-service)

- [modular resources](/reference/glossary/#term-modular-resource)
 provided by [modules](/reference/glossary/#term-module)


Each part has local resources and can also have resources from another [remote](/architecture/parts/)
 machine part.
The capabilities of each resource are exposed through the part’s API.

Each resource on your machine implements either one of the [existing Viam APIs](/reference/apis/), or a [custom interface](/reference/).

### SDK (Software Development Kit) {#term-sdk}

Viam provides software development kits (SDKs) to help you write client applications and create support for custom [component](/reference/glossary/#term-component)
 types.

The SDKs wrap the `viam-server` [gRPC](/reference/glossary/#term-grpc)
 [Viam Robot API](/reference/glossary/#term-viam-robot-api)
 and streamline connection, authentication, and encryption.

For more information, see [Interact with Resources with Viam's Client SDKs](/reference/apis/).

### Service {#term-service}

Services are built-in software packages for complex capabilities such as simultaneous localization and mapping (SLAM), computer vision, motion planning, and data collection.

Each service is typed by a proto API, such as the [service proto definitions](https://github.com/viamrobotics/api/tree/main/proto/viam/service).

For more information, see [Service APIs](/reference/apis/#service-apis).

### Smart Machine {#term-smart-machine}

A machine or device that lives in the real world and has some ability to perceive the world (with a sensor, for example) and perform actions like operating a motor.
The machine might also interact with other systems, with the cloud, or with users.

### SQL {#term-sql}

[SQL (structured query language)](https://en.wikipedia.org/wiki/SQL) is the widely-used, industry-standard query language popular with [relational databases](https://en.wikipedia.org/wiki/Relational_database).

You can use SQL to query data that you have synced to Viam using the [data management service](/data/capture-sync/capture-and-sync-data/).

### Subtype {#term-subtype}

A category within a [type](/reference/glossary/#term-type)
 of [resource](/reference/glossary/#term-resource)
.
Resource models belonging to a subtype share the same API.
[Models](/reference/glossary/#term-model)
 implement that subtype's API protocol with different drivers.

For example, an arm is a subtype of the [component](/reference/glossary/#term-component)
 resource type, while the `ur5e` is a [model](/reference/glossary/#term-model)
 of the arm subtype's API.

The [Vision Service](/vision/configure/) is a subtype of the [service](/reference/glossary/#term-service)
 resource type.

The `subtype` string is the third part of the [API namespace triplet](/reference/glossary/#term-api-namespace-triplet)
.

### Trigger {#term-trigger}

A trigger is a mechanism that sends alerts by email, webhook, or push notification when specific events occur in your machine or data.

Triggers can alert you when the following events occur:

- Machine telemetry data syncs from your local device to the Viam cloud
- Data syncs from a machine
- A service detects a specified object or classifies a specified label

For more information, see [Trigger configuration](/reference/triggers/).

### Type {#term-type}

In the [RDK](/reference/glossary/rdk/)
 architecture's [namespace triplet](/reference/glossary/#term-api-namespace-triplet)
 for resource APIs, _type_ refers to the distinction between [component](/reference/glossary/#term-component)
 or [service](/reference/glossary/#term-service)
.

### Viam Agent {#term-viam-agent}

The Viam Agent is a provisioning application for deploying and managing `viam-server` across a fleet of machines.
You can use the Viam Agent to provision a machine as it first comes online with a pre-defined configuration, including WiFi networks or additional build or provision steps.

See [Provision Machines](/fleet/provision-devices/) for more information.

### Viam Robot API {#term-viam-robot-api}

The specification for communication with resources.

- The SDKs implement the Viam Robot API server-side.
- The SDKs use the Viam Robot API to act as clients.

Currently, the Viam Robot API is defined in a collection of Protocol Buffer files.

All SDKs written by Viam use [gRPC](/reference/glossary/#term-grpc)
 but the Viam Robot API itself does not mandate gRPC as the transport mechanism.

### viam-micro-server {#term-viam-micro-server}

The lightweight version of `viam-server`, built for microcontrollers.
`viam-micro-server` is a set of open-source utilities which run on your microcontroller and provides Viam functionality to your machine.
`viam-micro-server` is built from the Micro-RDK.

For more information see [Set up an ESP32](/reference/device-setup/setup-micro/).

### viam-server {#term-viam-server}

The open-source executable binary that runs on your machine's computer (such as a single-board computer or a server) and provides most Viam functionality.
`viam-server` is built from the RDK.

### View setup instructions {#term-setup}

Before configuring a machine [part](/reference/glossary/part/)
, you must follow the correct setup instructions for your machine's architecture.
You can view the setup instructions by clicking on the part status dropdown next to your machine's name in the top left corner of the page and clicking **View setup instructions**.

### Vision service {#term-vision-service}

The vision service is a [service](/reference/glossary/#term-service)
 in the Viam platform that enables machines to interpret visual data captured by camera using computer vision and [machine learning](/reference/glossary/#term-ml)
 techniques.
Vision services can use various models, including pre-trained models or custom models trained on your own data using the Viam platform.

For more information, see the [Vision service documentation](/vision/configure/) or [Alert on inferences](/vision/object-detection/alert-on-detections/).

### WebRTC {#term-webrtc}

An open source project which provides applications with real-time communication (RTC) using application programming interfaces (API) allowing powerful voice and video integration.

For more information see [webrtc.org](https://webrtc.org/).

### Websockets {#term-web-sockets}

A computer communications protocol that provides full-duplex communication channels over a single Transmission Control Protocol (TCP) connection.

### World frame {#term-world-frame}

The world reference [frame](/reference/) is the fixed, global coordinate system that serves as the reference point for all other coordinate frames in a robotic system.
It provides a consistent basis for describing the position and orientation of robots, components, and objects in the physical space.
All other coordinate frames (such as machine frames and component frames) are defined relative to this world frame, either directly or through a chain of transformations.

The user chooses the world frame, and defines it implicitly.
For example, if you have a robot arm mounted on a table and you define the arm's origin frame as having no translation or orientation relative to the world frame, then the arm's origin frame is the origin of the world frame.

