# Frame system reference

The frame system holds reference frame information for the relative position of components in space.
> Source: https://docs.viam.com/reference/services/frame-system/


The frame system is the basis for some of Viam's other services, like [motion](/reference/services/motion/) and [vision](/reference/services/vision/).
It stores the required contextual information to use the position and orientation readings returned by some components.

It is a mostly static system for storing the "reference frame" of each component of a machine within a coordinate system configured by the user.

## Used with

<div class="card-container">
  <div class="row-no-margin">








  
    <div class="relatedcard ">
      <a href="/reference/components/arm/" target="_blank" title="Arm">
          
            




    
    
    
<picture>

  
    
<img src="/icons/components/arm.svg" alt="Arm" class="" id="" style="" loading="lazy">
  

</picture>


          
          <p>
            
              Arm
            
          </p>
      </a>
    </div>
  










  
    <div class="relatedcard ">
      <a href="/reference/components/base/" target="_blank" title="Base">
          
            




    
    
    
<picture>

  
    
<img src="/icons/components/base.svg" alt="Base" class="" id="" style="" loading="lazy">
  

</picture>


          
          <p>
            
              Base
            
          </p>
      </a>
    </div>
  










  
    <div class="relatedcard ">
      <a href="/reference/components/camera/" target="_blank" title="Camera">
          
            




    
    
    
<picture>

  
    
<img src="/icons/components/camera.svg" alt="Camera" class="" id="" style="" loading="lazy">
  

</picture>


          
          <p>
            
              Camera
            
          </p>
      </a>
    </div>
  










  
    <div class="relatedcard ">
      <a href="/reference/components/gantry/" target="_blank" title="Gantry">
          
            




    
    
    
<picture>

  
    
<img src="/icons/components/gantry.svg" alt="Gantry" class="" id="" style="" loading="lazy">
  

</picture>


          
          <p>
            
              Gantry
            
          </p>
      </a>
    </div>
  










  
    <div class="relatedcard ">
      <a href="/reference/components/gripper/" target="_blank" title="Gripper">
          
            




    
    
    
<picture>

  
    
<img src="/icons/components/gripper.svg" alt="Gripper" class="" id="" style="" loading="lazy">
  

</picture>


          
          <p>
            
              Gripper
            
          </p>
      </a>
    </div>
  


</div>
</div>

## Configuration

For a full how-to guide, see [Frame system](/motion-planning/frame-system/) and the [frame system how-tos](/motion-planning/frame-system/).

You can configure a reference frame within the frame system for each of your machine's components:

1. Navigate to the **CONFIGURE** tab of your machine's page.

1. Find the configuration card for the component you want to add a frame to.

1. Click the **Frame** button.

1. Leave the default values, or edit the frame configuration.
   The frame configuration is a JSON object with the following parameters:

<!-- prettier-ignore -->
| Parameter | Required? | Description |
| --------- | ----------- | ----- |
| `parent`  | **Required** | The name of the reference frame you want to act as the parent of this frame. <br> Default: `world`. |
| `translation` | **Required** | The coordinates that the origin of this component's reference frame has within its parent reference frame. <br> Units: Millimeters. <br> Default: `(0, 0, 0)`. |
| `orientation`  | **Required** | The [orientation vector](/motion-planning/reference/orientation-vectors/) that yields the axes of the component's reference frame when applied as a rotation to the axes of the parent reference frame. <br> Types: Orientation vector in degrees (`ov_degrees`), orientation vector in radians (`ov_radians`), Euler angles (`euler_angles`), and quaternion (`quaternion`). <br> Default: `(0, 0, 1), 0`. |
| `geometry`  | Optional | Collision geometries for defining bounds in the environment of the machine. <br> Units: Millimeters. <br> Types: `sphere`, `box`, `capsule`, and `cylinder`. <br> Default: `none`. |




### JSON Template

```json
{
  "components": [
    {
      "name": "<your_component_name_1>",
      "type": "<your_component_type_1>",
      "model": "<your_component_model_1>",
      "attributes": { ... },
      "depends_on": [],
      "frame": {
        "parent": "<world_or_parent_component_name>",
        "translation": {
          "y": <float>,
          "z": <float>,
          "x": <float>
        },
        "orientation": {
          "type": "<type>",
          "value": {
            "x": <float>,
            "y": <float>,
            "z": <float>,
            "th": <float> // "w": <int> if "type": "quaternion"
          }
        },
        "geometry": {
          "type": "<type>",
          "x": <float>,
          "y": <float>,
          "z": <float>
        }
      }
    }
  ]
}
```

### JSON Example

```json
{
  "components": [
    {
      "name": "cam",
      "api": "rdk:component:camera",
      "model": "webcam",
      "attributes": {
        "video_path": "FDF90FEC-59E5-4FCF-AABD-DA03C4E19BFB"
      },
      "frame": {
        "parent": "world",
        "translation": {
          "x": 0,
          "y": 0,
          "z": 0
        },
        "orientation": {
          "type": "quaternion",
          "value": {
            "x": 0,
            "y": 0,
            "z": 0,
            "w": 1
          }
        },
        "geometry": {
          "type": "box",
          "x": 100,
          "y": 100,
          "z": 100
        }
      }
    }
  ]
}
```



> **Info:**
> 
> The `orientation` parameter offers different types for ease of configuration, but the frame system always stores and returns [orientation vectors](/motion-planning/reference/orientation-vectors/) in radians.
> Other types will be converted to `ov_radians`.

> **Tip:**
> 
> For [base components](/reference/components/base/), Viam considers `+X` to be to the right, `+Y` to be forwards, and `+Z` to be up.
> You can use [the right-hand rule](https://en.wikipedia.org/wiki/Right-hand_rule) to understand rotation about any of these axes.
> 
> For non base components, there is no inherent concept of “forward,” so it is up to the user to define frames that make sense in their application.

## How the frame system works

`viam-server` builds a tree of reference frames for your machine with the `world` as the root node and regenerates this tree following reconfiguration.

Access a [topologically-sorted list](https://en.wikipedia.org/wiki/Topological_sorting) of the generated reference frames in the machine's logs at `--debug` level:

![an example of a logged frame system](/services/frame-system/frame_sys_log_example.png)

Consider the example of nested reference frame configuration where two dynamic components are attached: A robotic arm, `A`, attaches to a gantry, `G`, which in turn is fixed in place at a point in the `world` frame of a table.

The resulting tree of reference frames looks like:






    
    
    
<picture>

  
  
<source srcset="/services/frame-system/frame_tree_hu_65e41391d88e69d6.webp" type="image/webp" width="1162" height="1100">
<img src="/services/frame-system/frame_tree.png" width="1162" height="1100" alt="Linear tree diagram of nested reference frames with world at the root, connected to G_origin, which connects to G, in turn connected to A_origin, connected to A." class="imgzoom" id="" style="max-width:500px" loading="lazy">
  

</picture>




`viam-server` builds the connections in this tree by looking at the `"frame"` portion of each component in the machine's configuration and defining _two_ reference frames for each component:

1. One with the name of the component, representing the actuator or final link in the component's kinematic chain: like `"A"` as the end of an arm.
2. Another representing the origin of the component, defined with the component's name and the suffix _"\_origin"_.

## Access the frame system

The [Machine Management API](/reference/apis/robot/) supplies the following methods to interact with the frame system:

<!-- prettier-ignore -->
| Method Name | Description |
| ----- | ----------- |
| [`FrameSystemConfig`](/reference/apis/robot/#framesystemconfig) | Return a topologically sorted list of all the reference frames monitored by the frame system. |
| [`TransformPose`](/reference/apis/robot/#transformpose) | Transform a given source Pose from the original reference frame to a new destination reference frame. |

## Additional transforms

_Additional transforms_ exist to help the frame system determine the location of and relationships between objects not initially known to the machine.

### Example of additional transforms

Imagine you are using a wall-mounted [camera](/reference/components/camera/) to find objects near your arm.
You can use the [vision service](/reference/services/vision/) with the camera to detect objects and provide the poses of the objects with respect to the camera's reference frame.
The camera is fixed with respect to the `world` reference frame.

If the camera finds an apple or an orange, you can command the arm to move to the detected fruit's location by providing an additional transform that contains the detected pose of the fruit with respect to the camera that performed the detection.

The frame system uses the supplemental transform to determine where the arm should move to pick up the fruit.

### Transform usage

- You can pass a detected object's frame information to the `supplemental_transforms` parameter in your calls to Viam's motion service's [`GetPose`](/reference/apis/services/motion/#getpose) method.
- Functions of some services and components also take in a `WorldState` parameter, which includes a `transforms` property.
- [`TransformPose`](/reference/apis/robot/#transformpose) has the option to take in these additional transforms.

### Visualize components and frames

You can visualize your machine's geometries and frames in the Viam app:

{{% alert title="Tip" color="tip" %}}
To visualize a component without moving any real-world hardware, configure a `fake` model to represent your component (for example, a [`fake` arm](/reference/components/arm/fake/)), then follow the steps below using the fake component.
{{% /alert %}}

1. In Viam, navigate to your machine's page.
1. Make sure your machine is live and connected to Viam.
   **If your machine is not live, the visualization will not display.**
1. Select the **VISUALIZE** tab.

   {{<imgproc src="/operate/mobility/arm-viz.png" resize="x1100" declaredimensions=true alt="Visualization of a series of pill-shaped links forming an arm, above a grid." style="width:700px" class="shadow imgzoom" >}}

1. Scroll to zoom, click and drag to tilt, and right-click and drag to pan.

1. Use the tree menu or click on the visualization to select a component, link, or other object to display its position, orientation, and dimensions.

1. You can go to the **CONTROL** tab, move your components, and then return to the **VISUALIZE** tab to see the updated visualization.


