# Encoder Component

Configuration attribute reference for built-in encoder models.
> Source: https://docs.viam.com/reference/components/encoder/


This section documents the configuration attributes for each built-in encoder model.
Use these pages when you are writing a JSON configuration, debugging a config validation error, or looking up the default for a specific attribute.

- For how to add and configure a encoder component on your machine, see [Encoder](/hardware/common-components/add-an-encoder/).
- For the methods you call on a encoder in code, see the [Encoder API reference](/reference/apis/components/encoder/).
- For encoder models outside the built-in set, search for `encoder` in the [Viam registry](https://app.viam.com/registry). Each registry module's configuration is documented in its own README on its registry page.

## Built-in models

The following encoder models ship with `viam-server`:

| Model                         | Description                                                                                                                 |
| ----------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| [`fake`](/reference/components/encoder/fake/)               | An encoder model for testing.                                                                                               |
| [`incremental`](/reference/components/encoder/incremental/) | Supports a two phase encoder, which can measure the speed and direction of rotation in relation to a given reference point. |
| [`single`](/reference/components/encoder/single/)           | A single pin 'pulse output' encoder which returns its relative position but no direction.                                   |

## Micro-RDK models

The following encoder models ship with the [Micro-RDK](/reference/device-setup/setup-micro/):

| Model                                   | Description |
| --------------------------------------- | ----------- |
| [`incremental`](/reference/components/encoder/micro-rdk/incremental/) | —           |
| [`single`](/reference/components/encoder/micro-rdk/single/)           | —           |

