# Phase 2: Configure resources

Add the gripper and camera to the arm from Phase 1, connect the three with frames, then verify each one from the control and 3D scene tabs.
> Source: https://docs.viam.com/tutorials/pick-and-place/configure-resources/


You configured the arm in Phase 1. In this phase you add the two resources that work alongside it, a gripper and a camera, connect all three with frames, and confirm each one works from the Control tab before moving on.

## The target state

By the end of this phase your Configure tab holds all three components: `arm-1` from Phase 1, plus the gripper and camera you add here.

| Name        | API                     | Model                   |
| ----------- | ----------------------- | ----------------------- |
| `arm-1`     | `rdk:component:arm`     | `viam:ufactory:xArm6`   |
| `gripper-1` | `rdk:component:gripper` | `viam:ufactory:gripper` |
| `cam-1`     | `rdk:component:camera`  | `viam:camera:realsense` |

## Configure the gripper

Start with the gripper. On the **Configure** tab, click the **+** icon and select **Blocks**. Search for `gripper` and select the `ufactory/gripper` result. Name it `gripper-1`.

> **One module, two models:**
> 
> 
> The `viam:ufactory` module you downloaded in Phase 1 provides both the arm model and this gripper model, so `viam-server` already has the code it needs. No second download happens here.
> 

Set one attribute:

```json
{
  "arm": "arm-1"
}
```

This attribute is also a dependency: `gripper-1` cannot start until `arm-1` is running, because the gripper is physically mounted on the arm and controlled through the same connection. Save the config and check the **Logs** tab: `gripper-1` comes online immediately, because the `viam:ufactory` module has been running since Phase 1.

<!-- ASSET P2 configure-gripper (UI): gripper-1 config with arm: "arm-1" -->






    
    
    
<picture>

  
  
<source srcset="/tutorials/pick-and-place/configure-gripper_hu_a965da957bd46276.webp" type="image/webp" width="1200" height="492">
<img src="/tutorials/pick-and-place/configure-gripper.png" width="1200" height="492" alt="The gripper-1 config with its arm attribute set to arm-1." class="" id="" style="" loading="lazy">
  

</picture>




## Configure the camera with a discovery service

You could add the camera by hand like the arm and gripper, but the RealSense module ships a **discovery service** that does the tedious part for you: it finds the connected camera and hands you a ready-made config with the correct serial number already filled in. A discovery service reports the hardware attached to a machine and suggests configurations for it, so you configure the right device without hunting for identifiers by hand. See [Discovery service](/reference/services/discovery/) for the general pattern.

### Add the discovery service

Click the **+** icon and select **Blocks**. Search for `realsense` and select the `realsense/discovery` service. Leave its name as the default and save the config.

<!-- ASSET P0 configure-add-discovery (UI+): add-component dialog, "realsense" searched, discovery / realsense:discovery result highlighted -->






    
    
    
<picture>

  
  
<source srcset="/tutorials/pick-and-place/configure-add-discovery_hu_8af731c7c071bcd0.webp" type="image/webp" width="1200" height="400">
<img src="/tutorials/pick-and-place/configure-add-discovery.png" width="1200" height="400" alt="The add-component dialog with realsense searched and the discovery / realsense:discovery service selected." class="" id="" style="" loading="lazy">
  

</picture>




Saving now is the moment `viam-server` fetches the `viam:realsense` module: the discovery service and the camera model both come from it, so the download happens once here, the same way `viam:ufactory` downloaded once for the arm and gripper. Watch the **Logs** tab for the module download and the discovery service starting.

### Discover the camera

Open the discovery service's **Test** panel. It lists every RealSense it detects on the machine, each as a copy-pasteable configuration snippet with that camera's `serial_number` already populated. With one camera connected you see one entry. Select **Add component** next to it to create a camera component from the snippet.

<!-- ASSET P0 discovery-test-panel (UI+): realsense discovery Test panel showing a camera config snippet with serial_number filled in -->






    
    
    
<picture>

  
  
<source srcset="/tutorials/pick-and-place/discovery-test-panel_hu_d4246b8ef4bb7c67.webp" type="image/webp" width="1200" height="649">
<img src="/tutorials/pick-and-place/discovery-test-panel.png" width="1200" height="649" alt="The RealSense discovery service Test panel showing a discovered camera config with its serial number." class="" id="" style="" loading="lazy">
  

</picture>




The discovered component arrives named `realsense-<serial_number>`, with `sensors` set to `["color", "depth"]` and `serial_number` already filled in. Rename the camera to `cam-1` so it matches the rest of this workshop. Add one more attribute that discovery does not set:

```json
"align_color_depth": true
```

Leave the discovered `sensors` and `serial_number` as they are; letting discovery set the serial number is the whole point of using the service. You do not need to set `width_px` or `height_px`; the module uses a supported default resolution, and pinning one that the camera cannot produce would fail the build.

<!-- ASSET P2 configure-camera (UI): cam-1 realsense config, sensors color+depth, align_color_depth true, serial_number populated -->






    
    
    
<picture>

  
  
<source srcset="/tutorials/pick-and-place/configure-camera_hu_9546802b8f7e5f5e.webp" type="image/webp" width="1200" height="511">
<img src="/tutorials/pick-and-place/configure-camera.png" width="1200" height="511" alt="The cam-1 config with color and depth sensors, align_color_depth enabled, and a serial number." class="" id="" style="" loading="lazy">
  

</picture>




When `align_color_depth` is set to `true`, the module aligns each depth frame to the color frame, so a given pixel in the color image and the same pixel in the depth image describe the same physical point. The `vision-segment` service in Phase 5 relies on that alignment to turn a 2D detection into a 3D point cloud segment. Both `color` and `depth` must be in the `sensors` list for it to take effect.

Save the config and confirm in the **Logs** tab that `cam-1` starts. Because `viam-server` already downloaded the `viam:realsense` module when you added the discovery service, the camera comes online with no second download.

> **The discovery service has done its job:**
> 
> 
> The discovery service is not part of the pick-and-place pipeline; it only helped you configure `cam-1`. Leave it in place to re-discover hardware later, or remove it once the camera works. The rest of the workshop does not use it.
> 

## Connect the components with frames

Adding the arm, gripper, and camera tells `viam-server` how to talk to each one, but not where each sits in space. The motion service needs that spatial relationship: it has to know the gripper is mounted on the end of the arm and the camera looks out from the wrist, or it cannot plan a pick. You supply it by adding a **frame** to each component.

The three frames form a tree rooted at `world`:

```text
world
└── arm-1
    ├── gripper-1   (rides on the end effector)
    └── cam-1       (mounted on the wrist)
```

### Frame the arm

Open the `arm-1` card on the **Configure** tab and select **Frame**. The default frame already describes what you want: parent `world`, translation `(0, 0, 0)`, no rotation. That places the arm's base at the origin of the world, and every other frame is measured from there. Leave the defaults and save.

<!-- ASSET P1 configure-arm-frame (UI): arm-1 card Frame editor, parent world, translation 0,0,0 -->






    
    
    
<picture>

  
  
<source srcset="/tutorials/pick-and-place/configure-arm-frame_hu_fffdad101cde1f.webp" type="image/webp" width="1200" height="470">
<img src="/tutorials/pick-and-place/configure-arm-frame.png" width="1200" height="470" alt="The Frame editor for arm-1 with parent world and zero translation." class="" id="" style="" loading="lazy">
  

</picture>




### Frame the gripper

Open the `gripper-1` card and select **Frame**. Switch the editor to JSON and set:

```json
{
  "parent": "arm-1",
  "translation": { "x": 0, "y": 0, "z": 105 },
  "orientation": {
    "type": "ov_degrees",
    "value": { "x": 0, "y": 0, "z": 1, "th": 0 }
  }
}
```

Parent `arm-1` attaches the gripper to the end of the arm, and `z: 105` places the gripper frame 105 mm out from the arm's tool flange, at the gripper's tool center point. This is the point the motion service drives to a target when you call `motion.move` later in the workshop, and the reference the grasp math in Phase 5 builds on. This frame is separate from the `arm` attribute you set earlier: the attribute shares the arm's connection, while the frame tells the planner where the gripper sits. To go deeper on how parent frames and translations place an end effector like this, see [Arm and end effector frames](/motion-planning/frame-system/end-effector-frames/).

### Frame the camera

Open the `cam-1` card and select **Frame**. Switch the editor to JSON and set:

```json
{
  "parent": "arm-1",
  "translation": { "x": -73, "y": 40, "z": 18 },
  "orientation": {
    "type": "ov_degrees",
    "value": { "x": 0, "y": 0, "z": 1, "th": 270 }
  }
}
```

Parent `arm-1` mounts the camera on the wrist so it moves with the arm. The translation places the camera's optical center relative to the end effector, and the 270-degree rotation around z lines the camera's axes up with the arm's. Save the config.

Check that your camera configuration matches the image below: the component name is `cam-1`, the module / model selected is `realsense`/`realsense`, and the frame values match. Note that the attributes may change their order; you only need to verify the values.

<!-- ASSET P0 configure-camera-frame (UI+): cam-1 Frame editor JSON, parent arm-1, translation -73,40,18 -->






    
    
    
<picture>

  
  
<source srcset="/tutorials/pick-and-place/configure-camera-frame_hu_5154a16f550332ce.webp" type="image/webp" width="1200" height="1209">
<img src="/tutorials/pick-and-place/configure-camera-frame.png" width="1200" height="1209" alt="The Frame editor JSON for cam-1 with parent arm-1 and a wrist-mount translation." class="" id="" style="" loading="lazy">
  

</picture>




> **These values match this workshop's hardware:**
> 
> 
> The translation and orientation above describe the specific gripper and camera mount used in this workshop. If your hardware differs, work through the [frame calibration worksheet](https://github.com/viam-devrel/pick-and-place/blob/main/setup/frame-calibration-worksheet.md) to measure your own offsets, and see [Configure frames for an arm, gripper, and wrist camera](/motion-planning/frame-system/arm-gripper-camera/) for the full method.
> 

## Test each resource from the Control tab

Open the **Control** tab. You should now see a test card for each of the three components you just added.

### Test the camera

On the camera card, confirm you get a live feed:

<!-- ASSET P1 control-camera-stream (UI): Control camera card, live color + depth -->






    
    
    
<picture>

  
  
<source srcset="/tutorials/pick-and-place/control-camera-stream_hu_bfe6756aaf05c84c.webp" type="image/webp" width="1200" height="712">
<img src="/tutorials/pick-and-place/control-camera-stream.png" width="1200" height="712" alt="The cam-1 Control card showing a live color stream of the blocks." class="" id="" style="" loading="lazy">
  

</picture>




Below the **GetImages** control, you can toggle **GetPointCloud** on and set the "Camera up vector" to "-y" to see a live stream of the pointcloud data from the camera as a 3D scene. Hovering over any part of the point cloud with your mouse will display the x, y, z coordinates of that point from the perspective of the camera and distance from the camera sensor.

<!-- ASSET P1 control-camera-pointcloud (UI): Control camera card, live point clouds -->






    
    
    
<picture>

  
  
<source srcset="/tutorials/pick-and-place/control-camera-pointcloud_hu_9ac19ffe6ade47ea.webp" type="image/webp" width="1200" height="625">
<img src="/tutorials/pick-and-place/control-camera-pointcloud.png" width="1200" height="625" alt="The GetPointCloud control showing a live point cloud of the blocks, with a hovered point&#39;s x, y, z coordinates and distance to origin." class="" id="" style="" loading="lazy">
  

</picture>




<div class="checkpoint">
  <p class="checkpoint-title"><i class="icon fas fa-check-circle"></i>Checkpoint</p>
  <div class="checkpoint-body">The camera card shows a live color stream from <code>cam-1</code>. Because you configured both the <code>color</code> and <code>depth</code> sensors, switch the <strong>GetImages</strong> stream rate to &ldquo;Refresh every second&rdquo; and the source to depth and confirm that stream updates too. If the card is blank, check the Logs tab for a camera error before moving on.</div>
</div>


### Move the arm

> **The arm is about to move:**
> 
> 
> The next section moves the physical arm using joint control. Before you run a move, confirm the workspace is clear, keep the e-stop within reach, and change one joint a small amount at a time. Large or combined joint moves can drive the arm into the table, the camera, or itself.
> 

The arm card shows the arm's current joint positions, and provides two different control methods to test the arm, Joint Control and Cartesian control. Joint Control lets you manually set a joint's desired position and click execute, while the cartesian control lets you move the arm to a specific pose in space. Before using either, it is always a good idea to press **Current position** to set the desired values to match the arm's current state. Try moving the last two joints, joint 4 and joint 5 (the xArm6's six joints are numbered 0 through 5 in this UI), with the **MoveToJointPositions** sliders and press **Execute** and watch the end of the arm move. Then, under **MoveToPosition**, press **Current position** and confirm the **Pose Values** populate with the arm's current x, y, and z.

<!-- ASSET P1 control-arm-card (UI+): MoveToJointPositions sliders + Execute, and the MoveToPosition "Current position" button boxed -->






    
    
    
<picture>

  
  
<source srcset="/tutorials/pick-and-place/control-arm-card_hu_308aba1af5755232.webp" type="image/webp" width="1200" height="758">
<img src="/tutorials/pick-and-place/control-arm-card.png" width="1200" height="758" alt="The arm Control card with joint sliders, Execute, and the MoveToPosition Current position button." class="" id="" style="" loading="lazy">
  

</picture>




<div class="checkpoint">
  <p class="checkpoint-title"><i class="icon fas fa-check-circle"></i>Checkpoint</p>
  <div class="checkpoint-body">Pressing <strong>Execute</strong> after setting a joint slider moves the physical arm, and pressing <strong>Current position</strong> under <strong>MoveToPosition</strong> fills the Pose Values. If nothing moves or you see an error message, confirm <code>arm-1</code> shows as online in the Configure tab and that the Logs tab has no connection errors for it.</div>
</div>


### Control the gripper

The gripper test card lets you open and close a gripper, check whether the gripper is moving and whether it believes it's holding an object. Place a block between the fingers, and press **Grab** to close the fingers and hold the block. **Open** releases the block. This grab-and-release is the same action your Python code performs later in the workshop when it picks a block and drops it in a bin. If your gripper card also shows a holding status indicator, it now reads true while the block is held and false once the gripper is open and empty.

<!-- ASSET P1 control-gripper-grab (MOTION): gripper closing on a block via Grab, then Open releasing -->






    
    
    
<picture>

  
  
<source srcset="/tutorials/pick-and-place/control-gripper-grab_hu_27a727891aed7b65.webp" type="image/webp" width="1200" height="1600">
<img src="/tutorials/pick-and-place/control-gripper-grab.jpeg" width="1200" height="1600" alt="The two-finger gripper holding a block." class="" id="" style="" loading="lazy">
  

</picture>




<div class="checkpoint">
  <p class="checkpoint-title"><i class="icon fas fa-check-circle"></i>Checkpoint</p>
  <div class="checkpoint-body">With a block between the fingers, <strong>Grab</strong> closes the fingers and the gripper holds the block without dropping it. <strong>Open</strong> releases the block. If nothing moves, confirm <code>gripper-1</code> shows as online in the Configure tab and that the Logs tab has no connection errors for it.</div>
</div>


## The 3D scene tab

<!-- ASSET P0 3dscene-wrist-camera (MOTION): jog joint 1 and watch the cam-1 frame move with the arm (the wrist-camera insight) -->

Open the **3D scene** tab. It uses the resources and frames you configured to build a 3D model of your hardware: you should see the arm with its base at the world origin, plus a coordinate frame for `cam-1` and one for `gripper-1` near the end of the wrist.






    
    
    
<picture>

  
  
<source srcset="/tutorials/pick-and-place/3d-scene-tab_hu_2245923379b72d85.webp" type="image/webp" width="1200" height="681">
<img src="/tutorials/pick-and-place/3d-scene-tab.png" width="1200" height="681" alt="The 3D scene tab showing the arm at the world origin with coordinate frames for cam-1 and gripper-1 near the wrist." class="" id="" style="" loading="lazy">
  

</picture>




Jog joint 1 with the arm card's sliders and watch the 3D scene as the arm turns. The `cam-1` frame moves with the arm, because the camera is mounted on the wrist rather than fixed in the workspace.

> **Why this matters later:**
> 
> 
> Because the camera is wrist-mounted, every detection it makes is relative to wherever the arm happens to be pointed at that moment. In Phase 5 you will detect from one fixed observation pose, the home pose you save in Phase 3, so that "camera space" always means the same thing. Notice that pose here; you will meet it again as the "detect from home" rule.
> 

## Check your work

If you want to compare your machine configuration, the companion repo has a reference copy at [machine-fragment.json](https://github.com/viam-devrel/pick-and-place/blob/main/config/machine-fragment.json). Use it to check your work.

With `arm-1`, `gripper-1`, and `cam-1` all live and verified, you are ready for [Phase 3](/tutorials/pick-and-place/static-positions/), where you save a set of fixed arm poses and prove the full hardware sequence works before perception enters the picture.

<nav class="workshop-nav" aria-label="Workshop phase navigation"><p class="workshop-progress">Phase 2 of 6</p><div class="workshop-nav-links"><a class="workshop-nav-prev" href="/tutorials/pick-and-place/platform-mental-model/">&larr; Previous</a><a class="workshop-nav-next" href="/tutorials/pick-and-place/static-positions/">Next &rarr;</a></div>
</nav>


