# Motor Component

Configuration attribute reference for built-in motor models.
> Source: https://docs.viam.com/reference/components/motor/


This section documents the configuration attributes for each built-in motor model.
Use these pages when you are writing a JSON configuration, debugging a config validation error, or looking up the default for a specific attribute.

- For how to add and configure a motor component on your machine, see [Motor](/hardware/common-components/add-a-motor/).
- For the methods you call on a motor in code, see the [Motor API reference](/reference/apis/components/motor/).
- For motor models outside the built-in set, search for `motor` in the [Viam registry](https://app.viam.com/registry). Each registry module's configuration is documented in its own README on its registry page.

## Built-in models

The following motor models ship with `viam-server`:

| Model                             | Description                                                                   |
| --------------------------------- | ----------------------------------------------------------------------------- |
| [`dmc4000`](/reference/components/motor/dmc4000/)             | Stepper motor driven by a DMC-40x0 series motion controller.                  |
| [`encoded-motor`](/reference/components/motor/encoded-motor/) | Standard brushed or brushless DC motor with an encoder.                       |
| [`fake`](/reference/components/motor/fake/)                   | A model for testing, with no physical hardware.                               |
| [`gpio`](/reference/components/motor/gpio/)                   | Supports standard brushed or brushless DC motors.                             |
| [`gpiostepper`](/reference/components/motor/gpiostepper/)     | Supports stepper motors driven by basic GPIO-controlled stepper driver chips. |

## Micro-RDK models

The following motor models ship with the [Micro-RDK](/reference/device-setup/setup-micro/):

| Model                     | Description |
| ------------------------- | ----------- |
| [`gpio`](/reference/components/motor/micro-rdk/gpio/) | —           |

