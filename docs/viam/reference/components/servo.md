# Servo Component

Configuration attribute reference for built-in servo models.
> Source: https://docs.viam.com/reference/components/servo/


This section documents the configuration attributes for each built-in servo model.
Use these pages when you are writing a JSON configuration, debugging a config validation error, or looking up the default for a specific attribute.

- For how to add and configure a servo component on your machine, see [Servo](/hardware/common-components/add-a-servo/).
- For the methods you call on a servo in code, see the [Servo API reference](/reference/apis/components/servo/).
- For servo models outside the built-in set, search for `servo` in the [Viam registry](https://app.viam.com/registry). Each registry module's configuration is documented in its own README on its registry page.

## Built-in models

The following servo models ship with `viam-server`:

| Model           | Description                                                                                                           |
| --------------- | --------------------------------------------------------------------------------------------------------------------- |
| [`fake`](/reference/components/servo/fake/) | A model used for testing, with no physical hardware.                                                                  |
| [`gpio`](/reference/components/servo/gpio/) | Supports a hobby servo wired to a board that supports PWM, for example Raspberry Pi 5, Orange Pi, Jetson, or PCAXXXX. |

## Micro-RDK models

The following servo models ship with the [Micro-RDK](/reference/device-setup/setup-micro/):

| Model                     | Description |
| ------------------------- | ----------- |
| [`gpio`](/reference/components/servo/micro-rdk/gpio/) | —           |

