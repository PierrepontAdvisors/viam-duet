# gamepad

Reference for the gamepad input-controller model. Linux-supported gamepad as an input controller.
> Source: https://docs.viam.com/reference/components/input-controller/gamepad/


Configuring a `gamepad` input controller allows you to use a Linux-supported gamepad as a device to communicate with your machine.
Linux supports most standard gamepads, such as PlayStation or Xbox type game controllers, as well as many joysticks, racing wheels, and more.

To be able to test your gamepad as you configure it, physically connect your gamepad to your machine's computer and turn both on.




### JSON Template

```json
{
  "components": [
    {
      "name":  "<your-gamepad-input-controller>",
      "model": "gamepad",
      "api": "rdk:component:input_controller",
      "attributes": {
        "dev_file": "<string>",
        "auto_reconnect": <boolean>
      }
    }
  ]
}
```



The following attributes are available for `gamepad` input controllers:

<!-- prettier-ignore -->
| Name | Type | Required? | Description |
| ---- | ---- | --------- | ----------- |
| `dev_file` | string | Optional | If `dev_file` is left blank or not included, `viam-server` will search and use the first gamepad it finds that's connected to the computer controlling your machine. If you want to specify a device, give the absolute path to the input device event file. For example: `/dev/input/event42`. |
| `auto_reconnect` | boolean | Optional | Applies to both remote (gRPC) and local (Bluetooth or direct USB connected) devices. If set to `true`, `viam-server` tries to (re)connect the device automatically. It waits for a device to connect during a machine's start-up. If set to false (default) then start-up fails if a device is not already connected. |

## Test the input controller

After you configure your input controller, open the input controller's **TEST** panel on the **CONFIGURE** or [**CONTROL**](/monitor/default-interface/#web-ui) tabs.
View the current value of each input on your controller.

{{<imgproc src="/components/input-controller/input-controller-control-tab.png" alt="The input controller component in the test panel." resize="800x" style="width:500px">}}


## Work in progress models

Mappings are currently available for a wired XBox 360 controller, and wireless XBox Series X|S, along with the 8bitdo Pro 2 Bluetooth gamepad (which works great with the Raspberry Pi).

The XBox controllers emulate an XBox 360 gamepad when in wired mode, as does the 8bitdo.

Because of that, any unknown gamepad is mapped as an XBox 360.

If you have another controller that you want to use to control your machine, feel free to submit a PR on [GitHub](https://github.com/viamrobotics/rdk/blob/main/components/input/input.go) with new mappings.

## Troubleshooting

**Not able to see a dropdown menu?**


If you are not able to see a dropdown menu with the name of your controller appear in the **CONTROL** tab, try specifying the `dev_file` attribute to match the exact path to your device.
You can also try setting `auto_reconnect` to `True`.



