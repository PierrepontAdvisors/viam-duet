# single-axis

Reference for the single-axis gantry model. Single-axis gantry.
> Source: https://docs.viam.com/reference/components/gantry/single-axis/


Configure a `single-axis` gantry to integrate a single-axis gantry into your machine.
First, be sure to physically assemble the gantry and connect it to your machine's computer.
Also, configure any [motor components](/reference/components/motor/) that are part of the gantry.




### JSON Template

```json
{
  "components": [
    // < Your motor config >
    {
      "name": "<your-single-axis-gantry-name>",
      "model": "single-axis",
      "api": "rdk:component:gantry",
      "attributes": {
        "motor": "<your-motor-name>",
        "length_mm": <int>,
        "mm_per_rev": <int>
      },
      "depends_on": []
    }
  ]
}
```



The following attributes are available for `single-axis` gantries:

<!-- prettier-ignore -->
| Attribute | Type | Required? | Description |
| --------- | ---- | --------- | ----------  |
| `length_mm` | int | **Required** | Length of the axis of the gantry in millimeters. |
| `motor` | string | **Required** | `name` of the [motor](/reference/components/motor/) that moves the gantry's actuator. |
| `board`  |  string | Optional | `name` of the [board](/reference/components/board/) containing the limit switches and pins. If `limit_pins` exist, `board` is required. |
| `limit_pins`  | object | Optional | The `boards`'s pins attached to the limit switches on either end. If the [motor](/reference/components/motor/) used does not include an [encoder](/reference/components/motor/encoded-motor/), `limit_pins` are required to be set. |
| `limit_pin_enabled_high` | boolean | Optional | Whether the limit pins are enabled. <br> Default: `false` |
| `mm_per_rev` | int | **Required** | How far the gantry moves (linear, distance in mm) per one revolution of the motor’s output shaft. This typically corresponds to Distance = PulleyDiameter * pi, or the pitch of a linear screw. |
| `gantry_mm_per_sec` | int | Optional | The speed at which the gantry moves in millimeters per second. Used to calculate the gantry `motor`'s revolutions per minute (RPM). <br> Default: `100` RPM |

## Test the gantry

Once your gantry is configured and connected, open the gantry's **TEST** panel on the **CONFIGURE** or [**CONTROL**](/monitor/default-interface/#web-ui) tabs.

Use the panel to adjust the position of the actuator on the axis and check whether it moves as expected.

{{<imgproc src="/components/gantry/gantry-control-tab.png" declaredimensions=true alt="Gantry test panel." resize="800x" style="width:500px" class="imgzoom">}}

If the gantry does not appear on the **TEST** panel, or if you notice unexpected behavior, check your machine's [**LOGS** tab](/monitor/troubleshoot/#check-logs) for errors, and review the configuration.


