# multi-axis

Reference for the multi-axis gantry model. Multi-axis gantry.
> Source: https://docs.viam.com/reference/components/gantry/multi-axis/


Configure a `multi-axis` gantry to integrate a gantry made up of multiple [`single-axis`](/reference/components/gantry/single-axis/) gantries into your machine.

First, physically assemble the gantry and connect it to your machine's computer.
Next, configure each single-axis gantry that is part of the muti-axis gantry.




### JSON Template

```json
{
  "components": [
    ... // < INSERT YOUR MOTOR AND SINGLE-AXIS GANTRY CONFIGURATIONS >
    {
      "name": "<your-fake-gantry-name>",
      "model": "multi-axis",
      "api": "rdk:component:gantry",
      "attributes": {
          "subaxes_list": [
              "<xaxis-name>",
              "<yaxis-name>",
              "<zaxis-name>"
          ]
      },
      "depends_on": []
    }
  ]
}
```

### JSON Example

```json
{
  "components": [
    {
      "name": "local",
      "model": "pi",
      "api": "rdk:component:board"
    },
    {
      "name": "xmotor",
      "model": "gpiostepper",
      "api": "rdk:component:motor",
      "attributes": {
        "board": "local",
        "pins": {
          "dir": "11",
          "pwm": "13",
          "step": "15"
        },
        "stepperDelay": 50,
        "ticksPerRotation": 200
      }
    },
    {
      "name": "ymotor",
      "model": "gpiostepper",
      "api": "rdk:component:motor",
      "attributes": {
        "board": "local",
        "pins": {
          "dir": "16",
          "pwm": "18",
          "step": "22"
        },
        "stepperDelay": 50,
        "ticksPerRotation": 200
      }
    },
    {
      "name": "zmotor",
      "model": "gpiostepper",
      "api": "rdk:component:motor",
      "attributes": {
        "board": "local",
        "pins": {
          "dir": "29",
          "pwm": "31",
          "step": "33"
        },
        "stepperDelay": 50,
        "ticksPerRotation": 200
      }
    },
    {
      "name": "xaxis",
      "model": "single-axis",
      "api": "rdk:component:gantry",
      "attributes": {
        "length_mm": 1000,
        "board": "local",
        "limit_pin_enabled_high": false,
        "limit_pins": ["32", "36"],
        "motor": "xmotor",
        "gantry_rpm": 500,
        "axis": {
          "x": 1,
          "y": 0,
          "z": 0
        }
      }
    },
    {
      "name": "yaxis",
      "model": "single-axis",
      "api": "rdk:component:gantry",
      "attributes": {
        "length_mm": 1000,
        "board": "local",
        "limit_pin_enabled_high": false,
        "limit_pins": ["37", "38"],
        "motor": "ymotor",
        "gantry_rpm": 500,
        "axis": {
          "x": 0,
          "y": 1,
          "z": 0
        }
      }
    },
    {
      "name": "zaxis",
      "model": "single-axis",
      "api": "rdk:component:gantry",
      "attributes": {
        "length_mm": 1000,
        "board": "local",
        "limit_pin_enabled_high": false,
        "limit_pins": ["10", "12"],
        "motor": "zmotor",
        "gantry_rpm": 500,
        "axis": {
          "x": 0,
          "y": 0,
          "z": 1
        }
      },
      "frame": {
        "parent": "world",
        "orientation": {
          "type": "euler_angles",
          "value": {
            "roll": 0,
            "pitch": 40,
            "yaw": 0
          }
        },
        "translation": {
          "x": 0,
          "y": 3,
          "z": 0
        }
      }
    },
    {
      "name": "my_multi-axis_gantry",
      "model": "multi-axis",
      "api": "rdk:component:gantry",
      "attributes": {
        "subaxes_list": ["xaxis", "yaxis", "zaxis"],
        "move_simultaneously": "false"
      }
    }
  ]
}
```



The following attributes are available for `multi-axis` gantries:

<!-- prettier-ignore -->
| Attribute | Type | Required? | Description |
| --------- | ---- | --------- | ----------- |
| `subaxes_list` | array | **Required** | An array of the `name` of each of the sub-axes, the [`single-axis`](/reference/components/gantry/single-axis/) gantries that make up the `multi-axis` gantry. |
| `move_simultaneously` | boolean | Optional | A boolean indicating if the sub-axes should move together, or one at a time when `MoveToPosition` is called. <br> Default:  `false` |

## Test the gantry

Once your gantry is configured and connected, open the gantry's **TEST** panel on the **CONFIGURE** or [**CONTROL**](/monitor/default-interface/#web-ui) tabs.

Use the panel to adjust the position of the actuator on the axis and check whether it moves as expected.

{{<imgproc src="/components/gantry/gantry-control-tab.png" declaredimensions=true alt="Gantry test panel." resize="800x" style="width:500px" class="imgzoom">}}

If the gantry does not appear on the **TEST** panel, or if you notice unexpected behavior, check your machine's [**LOGS** tab](/monitor/troubleshoot/#check-logs) for errors, and review the configuration.


