# mux

Reference for the mux input-controller model. Mux input controller to combine one or more input controllers.
> Source: https://docs.viam.com/reference/components/input-controller/mux/


Configuring a `mux` (multiplexed) input controller allows you to combine one or more controllers into a single virtual controller.

This lets you control a machine from different locations, such as the web and a locally connected gamepad, or use multiple controllers as one device.

For example, you could use a joystick alongside a numpad.

## Configuration

To combine multiple controllers into a `mux` controller, you must first configure each controller individually.




### JSON Template

```json
{
  "components": [
    {
      "name": "<your-mux-input-controller-name>",
      "model": "mux",
      "api": "rdk:component:input_controller",
      "attributes": {
        "sources": [
          "<your-gamepad-input-controller-name",
          "<your-other-gamepad-input-controller-name>"
        ]
      },
      "depends_on": [
        "<your-gamepad-input-controller-name>",
        "<your-other-gamepad-input-controller-name>"
      ]
    }
    <...CONFIGS FOR THE INDIVIDUAL INPUT CONTROLLERS...>
  ]
}
```

### JSON Example

The following example configuration combines a `gamepad` and a `webgamepad` controller:

```json
{
  "components": [
    {
      "name": "my-combined-controller",
      "model": "mux",
      "api": "rdk:component:input_controller",
      "attributes": {
        "sources": ["myGamepad", "WebGamepad"]
      },
      "depends_on": ["myGamepad", "WebGamepad"]
    },
    {
      "name": "myGamepad",
      "model": "gamepad",
      "api": "rdk:component:input_controller",
      "attributes": {
        "auto_reconnect": true
      },
      "depends_on": []
    },
    {
      "name": "WebGamepad",
      "model": "webgamepad",
      "api": "rdk:component:input_controller",
      "attributes": {},
      "depends_on": []
    }
  ]
}
```



The following attributes are available for `mux` input controllers:

<!-- prettier-ignore -->
| Name | Type | Required? | Description |
| ---- | ---- | --------- | ----------- |
| `sources` | array | **Required** | The `name` of every controller component you wish to combine input from. |

> **Important:**
> 
> You must put each controller’s `name` that you add in `sources` in `depends_on`.
> This tells the program loading the config to fully load the source components first.

## Test the input controller

After you configure your input controller, open the input controller's **TEST** panel on the **CONFIGURE** or [**CONTROL**](/monitor/default-interface/#web-ui) tabs.
View the current value of each input on your controller.

{{<imgproc src="/components/input-controller/input-controller-control-tab.png" alt="The input controller component in the test panel." resize="800x" style="width:500px">}}


