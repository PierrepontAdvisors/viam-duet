# Input Controller Component

Configuration attribute reference for built-in input controller models.
> Source: https://docs.viam.com/reference/components/input-controller/


This section documents the configuration attributes for each built-in input controller model.
Use these pages when you are writing a JSON configuration, debugging a config validation error, or looking up the default for a specific attribute.

- For how to add and configure a input controller component on your machine, see [Input controller](/hardware/common-components/add-an-input-controller/).
- For the methods you call on a input controller in code, see the [Input controller API reference](/reference/apis/components/input-controller/).
- For input controller models outside the built-in set, search for `input controller` in the [Viam registry](https://app.viam.com/registry). Each registry module's configuration is documented in its own README on its registry page.

## Built-in models

The following input controller models ship with `viam-server`:

| Model                       | Description                                                              |
| --------------------------- | ------------------------------------------------------------------------ |
| [`fake`](/reference/components/input-controller/fake/)             | A model for testing, with no physical hardware.                          |
| [`gamepad`](/reference/components/input-controller/gamepad/)       | Supports X-box, Playstation, and similar controllers with Linux support. |
| [`gpio`](/reference/components/input-controller/gpio/)             | Customizable GPIO/ADC based device using a board component.              |
| [`mux`](/reference/components/input-controller/mux/)               | Supports multiplexed controllers, combining multiple sources of input.   |
| [`webgamepad`](/reference/components/input-controller/webgamepad/) | Supports a remote, web based gamepad.                                    |

