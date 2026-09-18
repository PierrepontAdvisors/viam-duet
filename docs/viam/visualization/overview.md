# Visualization

Ways to visualize a Viam machine: the 3D scene, the standalone Viam visualizer, custom apps you build, and time-series dashboards.
> Source: https://docs.viam.com/visualization/overview/


A machine produces two kinds of data you can watch: spatial state (frames, geometries,
collisions, point clouds, motion plans) and time series readings (temperatures, speeds,
counts). For spatial state, use the 3D scene view in
the Viam app, or Viam Visualization, a standalone visualizer you run yourself. You can also
read this data from components with a Viam SDK and present it in a custom user interface you
build, which runs in a browser, on a phone, or on a server. For time series data, services
and modules push readings to the cloud, where the Viam app's Teleop workspaces and dashboards
show live information across a machine or fleet.

## The 3D scene

The **3D SCENE** tab on your machine's page renders an interactive 3D view of your
machine and the spatial data around it. For what it draws and where each element comes
from, see [Visualizing with the 3D scene](/visualization/3d-scene/).

- Use it while configuring or debugging a machine, to see frames, geometry, and live poses
  with no code.
- Best for catching frame and obstacle misconfigurations and inspecting a motion plan in
  context. It runs right in the Viam app, ready to use.

<div class="card-container">
  <div class="row-no-margin">
<div class="col hover-card "><a href="/visualization/3d-scene/"><div ><div>3D scene</div><p>What the 3D scene renders, where each element comes from, and how built-in configuration content differs from custom visuals a module publishes at runtime.</p></div>
    </a></div>

<div class="col hover-card "><a href="/visualization/visuals-and-collisions/"><div ><div>Visuals and collisions</div><p>How a Transform defines a custom visual, and which geometry the motion planner actually collision-checks.</p></div>
    </a></div>

<div class="col hover-card "><a href="/visualization/publish-visuals-from-a-module/"><div ><div>Publish visuals from a module</div><p>Implement a world state store service that pulls data from other resources, builds transforms with the draw library, and streams them to the 3D scene.</p></div>
    </a></div>

<div class="col hover-card "><a href="/motion-planning/visualize-a-motion-plan/"><div ><div>Visualize a motion plan</div><p>Publish a motion plan&#39;s trajectory and goals as custom visuals so the 3D scene renders the path against obstacles and reach.</p></div>
    </a></div>

<div class="col hover-card "><a href="/visualization/troubleshoot-the-3d-scene/"><div ><div>Troubleshoot the 3D scene</div><p>Trace a wrong or missing element in the 3D scene to its source: the machine configuration, a module, or the connection.</p></div>
    </a></div>

</div>
</div>

## Viam Visualization

Viam Visualization is a standalone 3D visualizer you run yourself to preview and debug
spatial data from a Go client. It shares the same `draw` library as the in-app 3D scene, so
the visuals you build work either way.

- Use it while developing, to preview spatial data such as a point cloud, detections, or a
  planned path straight from a script or test.
- Best when you want to iterate from Go quickly, without deploying a module or opening the
  Viam app.

<div class="card-container">
  <div class="row-no-margin">
<div class="col hover-card "><a href="/visualization/viam-visualization/"><div ><div>Viam Visualization</div><p>Run the standalone Viam Visualization app locally and push geometries, point clouds, and frame systems to it from a Go client.</p></div>
    </a></div>

</div>
</div>

## Custom apps

A custom app uses a Viam SDK to read your machine's data and present it however you design.
It runs outside the machine, in a browser, on a phone, or on a server, so you can build a
custom dashboard, an operator console, or a fleet view. A Svelte app can also
[embed the 3D scene's own renderer](https://viamrobotics.github.io/visualization/guides/embedding/)
as a component, so a custom UI gets the full 3D view alongside your own controls.

- Use it when operators or stakeholders need a tailored UI beyond the built-in scene.
- Best when you want to choose exactly which data to show and how, for one machine or a
  whole fleet.

<div class="card-container">
  <div class="row-no-margin">
<div class="col hover-card "><a href="/build-apps/overview/"><div ><div>Overview</div><p>Build software that uses a Viam SDK to talk to your machines and the Viam cloud, from web dashboards to long-running backend services.</p></div>
    </a></div>

<div class="col hover-card "><a href="/build-apps/app-tutorials/tutorial-dashboard/"><div ><div>Tutorial: single-machine dashboard</div><p>Build a TypeScript web dashboard for a single Viam machine. Displays a camera feed, a live sensor reading, and a motor control button, with a connection status indicator.</p></div>
    </a></div>

<div class="col hover-card "><a href="/build-apps/app-tutorials/tutorial-fleet/"><div ><div>Tutorial: multi-machine fleet dashboard</div><p>Build a TypeScript web dashboard that connects to the Viam cloud, enumerates machines across an organization, and displays aggregated sensor data from a fleet.</p></div>
    </a></div>

<div class="col hover-card "><a href="/build-apps/app-tutorials/tutorial-flutter-app/"><div ><div>Tutorial: Flutter app with widgets</div><p>Build a cross-platform Flutter app for a single Viam machine. Uses prebuilt widgets for the camera feed, sensor display, and motor control.</p></div>
    </a></div>

<div class="col hover-card "><a href="/build-apps/app-tutorials/tutorial-monitoring-service/"><div ><div>Tutorial: Python monitoring service</div><p>Build a Python service that connects to a Viam machine, monitors a sensor, controls a motor based on sensor readings, and shuts down cleanly.</p></div>
    </a></div>

</div>
</div>

## Time series data

Services and modules push readings to the cloud, where you watch them live with Viam's
Teleop workspaces and dashboards.

- Use it for values that change over time: temperatures, speeds, counts, and sensor
  readings.
- Best for live monitoring and historical trends across a single machine or a whole fleet.

<div class="card-container">
  <div class="row-no-margin">
<div class="col hover-card "><a href="/monitor/teleop-workspaces/"><div ><div>Teleop workspaces</div><p>Build custom operator interfaces with camera feeds, sensor readouts, and component controls.</p></div>
    </a></div>

<div class="col hover-card "><a href="/monitor/dashboards/overview/"><div ><div>Overview</div><p>Understand dashboard widget types, the windowing and aggregation query model, and how dashboards differ from teleop workspaces.</p></div>
    </a></div>

</div>
</div>

