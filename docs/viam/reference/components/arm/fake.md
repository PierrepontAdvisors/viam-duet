# fake

Reference for the fake arm model. Fake arm to use for testing.
> Source: https://docs.viam.com/reference/components/arm/fake/


Configure a `fake` arm to test different models of robotic arms without any physical hardware:




### JSON Template

```json
{
  "name": "<arm_name>",
  "model": "fake",
  "api": "rdk:component:arm",
  "attributes": {
    "arm-model": "<your_arm_model>",
    "model-path": "<path_to_arm_model>"
  },
  "depends_on": []
}
```

### JSON Example

```json
{
  "name": "my-fake-arm",
  "model": "fake",
  "api": "rdk:component:arm",
  "attributes": {
    "arm-model": "ur5e"
  },
  "depends_on": []
}
```



The following attributes are available for `fake` arms:

<!-- prettier-ignore -->
| Name | Type | Required? | Description |
| ---- | ---- | --------- | ----------- |
| `arm-model` | string | Optional | Model name of the robotic arm model you want your fake arm to act as. See [built-in arm models](/reference/components/arm/) for supported model names. |
| `model-path` | string | Optional | The path to the [kinematic configuration file](/motion-planning/frame-system/) of the arm driver you want your fake arm to act as. This path should point to the exact location where the file is located on your computer running `viam-server`. |

## Test the arm

Once your arm is configured and connected, open the arm's **TEST** panel on the **CONFIGURE** or [**CONTROL**](/monitor/default-interface/#web-ui) tabs.

Use the buttons to move the end position or the joints and check whether it moves as expected.

{{<imgproc src="/components/arm/control.png" alt="Arm test panel." resize="800x" style="width:500px" class="imgzoom shadow">}}

If the arm does not appear on the **TEST** panel, or if you notice unexpected behavior, check your machine's [**LOGS** tab](/monitor/troubleshoot/#check-logs) for errors, and review the configuration.


