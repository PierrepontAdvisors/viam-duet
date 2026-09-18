# webgamepad

Reference for the webgamepad input-controller model. Web-based gamepad as an input controller.
> Source: https://docs.viam.com/reference/components/input-controller/webgamepad/


Configuring a `webgamepad` input controller allows you to use a web-based gamepad as a device to communicate with your machine.

> **Important:**
> 
> You **must** use “WebGamepad” as the `name` of the web gamepad controller.
> This restriction will be removed in the future.

To be able to test your gamepad as you configure it, physically connect your gamepad to your machine's computer and turn both on.

## Configuration

Use the following configuration for an input controller of model `webgamepad`:




### JSON Template

```json
{
  "components": [
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



## Test the input controller

After you configure your input controller, open the input controller's **TEST** panel on the **CONFIGURE** or [**CONTROL**](/monitor/default-interface/#web-ui) tabs.
View the current value of each input on your controller.

{{<imgproc src="/components/input-controller/input-controller-control-tab.png" alt="The input controller component in the test panel." resize="800x" style="width:500px">}}


> **Important:**
> 
> You have to press a button or move a stick on your gamepad for the browser to report the gamepad.
> For your security, the browser won’t report a gamepad until an input has been sent.

