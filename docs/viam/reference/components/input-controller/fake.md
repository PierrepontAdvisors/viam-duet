# fake

Reference for the fake input-controller model. Fake input controller for testing.
> Source: https://docs.viam.com/reference/components/input-controller/fake/


Configuring a `fake` input controller allows you to test an input controller communicating with your machine, without any physical hardware.

This controller can have [Controls](/reference/apis/components/input-controller/#control-field) defined in `attributes`, as seen in the "JSON Template" tab below.
However, these Controls only ever return a single `PositionChangeAbs` event on the X axis, with the [Event.value](/reference/apis/components/input-controller/#event-object) stuck at 0.7.




### JSON Template

```json
{
  "components": [
    {
      "name": "<your-fake-input-controller>",
      "model": "fake",
      "api": "rdk:component:input_controller",
      "attributes": {
        "controls": [
          "AbsoluteX",
          "AbsoluteY",
          "AbsoluteZ"
        ],
        "event_value": <float>,
        "callback_delay_sec": <float>
      }
    }
}
```



The following attributes are available for `fake` input controllers:

<!-- prettier-ignore -->
| Name | Type | Required? | Description |
| ---- | ---- | --------- | ----------- |
| `callback_delay_sec` | float | **Required** | The number of seconds between callbacks getting triggered. Random between 1 and 2 if not specified. `0` is not valid and will be overwritten by a random delay. |
| `event_value` | float | Optional | Set the value of events returned. Random between -1 and 1 if not specified. |
| `controls` | array | Optional | Set the [Controls](/reference/apis/components/input-controller/#control-field) that are present on the controller. |

## Test the input controller

After you configure your input controller, open the input controller's **TEST** panel on the **CONFIGURE** or [**CONTROL**](/monitor/default-interface/#web-ui) tabs.
View the current value of each input on your controller.

{{<imgproc src="/components/input-controller/input-controller-control-tab.png" alt="The input controller component in the test panel." resize="800x" style="width:500px">}}


