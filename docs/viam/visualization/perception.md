# Perception in the 3D scene

View and compare live perception data in the 3D scene: depth-camera point clouds, vision-service entities, and a sensor's own point of view.
> Source: https://docs.viam.com/visualization/perception/


The 3D scene renders live perception data alongside your frame system, so you see what your
machine senses in the same space as the components that sense it. Cameras are what it draws
today, and a camera contributes in more than one way: its frame positions it in space, a
depth camera's point cloud renders at that frame, a vision service can add entities of its
own, and the camera's live feed and
[point of view](/visualization/3d-scene/3d-scene-widgets/) are available as widgets.

When perception data lands in the wrong place in the scene, the sensing component's frame
configuration is the usual cause, not the component. For configuring and tuning the vision
services themselves, see [Computer vision](/vision/).

<div class="card-container">
  <div class="row-no-margin">
<div class="col hover-card "><a href="/visualization/perception/point-clouds/"><div ><div>Point clouds</div><p>How depth-camera point clouds render in the 3D scene, how to adjust their display, and how to load and compare external point clouds.</p></div>
    </a></div>

<div class="col hover-card "><a href="/visualization/perception/vision-services/"><div ><div>Vision services</div><p>Render a vision service&#39;s segmented objects in the 3D scene and tune detection parameters against the live view.</p></div>
    </a></div>

<div class="col hover-card "><a href="/visualization/perception/verify-point-cloud-alignment/"><div ><div>Verify point cloud alignment</div><p>Display a depth camera&#39;s point cloud in the 3D scene to verify that the data aligns with your frame system and workspace geometry.</p></div>
    </a></div>

</div>
</div>

