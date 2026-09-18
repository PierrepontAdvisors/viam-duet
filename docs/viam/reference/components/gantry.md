# Gantry Component

Configuration attribute reference for built-in gantry models.
> Source: https://docs.viam.com/reference/components/gantry/


This section documents the configuration attributes for each built-in gantry model.
Use these pages when you are writing a JSON configuration, debugging a config validation error, or looking up the default for a specific attribute.

- For how to add and configure a gantry component on your machine, see [Gantry](/hardware/common-components/add-a-gantry/).
- For the methods you call on a gantry in code, see the [Gantry API reference](/reference/apis/components/gantry/).
- For gantry models outside the built-in set, search for `gantry` in the [Viam registry](https://app.viam.com/registry). Each registry module's configuration is documented in its own README on its registry page.

## Built-in models

The following gantry models ship with `viam-server`:

| Model                         | Description                                                                              |
| ----------------------------- | ---------------------------------------------------------------------------------------- |
| [`fake`](/reference/components/gantry/fake/)               | A model used for testing, with no physical hardware.                                     |
| [`multi-axis`](/reference/components/gantry/multi-axis/)   | Supports a gantry with multiple linear rails. Composed of multiple single-axis gantries. |
| [`single-axis`](/reference/components/gantry/single-axis/) | Supports a gantry with a singular linear rail.                                           |

