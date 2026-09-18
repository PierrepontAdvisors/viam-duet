# fake

Reference for the fake gantry model. Fake gantry.
> Source: https://docs.viam.com/reference/components/gantry/fake/


Configure a `fake` gantry to test implementing a gantry component on your machine without any physical hardware.
The fake gantry is single-axis: it tracks position in memory along one prismatic joint, validates moves against the axis length, always returns `false` from `IsMoving`, and returns `true` immediately from `Home`.




### JSON Template

```json
{
  "name": "<your-fake-gantry-name>",
  "model": "fake",
  "api": "rdk:component:gantry",
  "attributes": {
    "length_mm": <float>,
    "model_path": "<path_to_gantry_model>"
  }
}
```

### JSON Example

```json
{
  "name": "my-fake-gantry",
  "model": "fake",
  "api": "rdk:component:gantry",
  "attributes": {
    "length_mm": 1000
  }
}
```



The following attributes are available for `fake` gantries:

<!-- prettier-ignore -->
| Name | Type | Required? | Description |
| ---- | ---- | --------- | ----------- |
| `length_mm` | float | Optional | Travel length of the single axis in millimeters. Defaults to `100` when omitted. Cannot be set together with `model_path`. |
| `model_path` | string | Optional | Path to a [kinematic configuration file](/motion-planning/frame-system/) for a single-DoF prismatic gantry. This path should point to the exact location where the file is located on your computer running `viam-server`. Cannot be set together with `length_mm`. |

See [GitHub](https://github.com/viamrobotics/rdk/blob/main/components/gantry/fake/gantry.go) for API call return specifications.

## Test the gantry

Once your gantry is configured and connected, open the gantry's **TEST** panel on the **CONFIGURE** or [**CONTROL**](/monitor/default-interface/#web-ui) tabs.

Use the panel to adjust the position of the actuator on the axis and check whether it moves as expected.

{{<imgproc src="/components/gantry/gantry-control-tab.png" declaredimensions=true alt="Gantry test panel." resize="800x" style="width:500px" class="imgzoom">}}

If the gantry does not appear on the **TEST** panel, or if you notice unexpected behavior, check your machine's [**LOGS** tab](/monitor/troubleshoot/#check-logs) for errors, and review the configuration.


