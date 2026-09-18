# fake

Reference for the fake board model. Fake board.
> Source: https://docs.viam.com/reference/components/board/fake/


The `fake` board returns incrementing values for digital interrupt ticks and analogs.

Configure a `fake` board to test integrating a board into your machine without physical hardware:




### JSON Template

```json
{
  "components": [
    {
      "name": "<your-fake-board-name>",
      "model": "fake",
      "api": "rdk:component:board",
      "attributes": {
        "fail_new": <boolean>
      },
      "depends_on": []
    }
  ]
}
```



The following attributes are available for `fake` boards:

<!-- prettier-ignore -->
| Name | Type | Required? | Description |
| ---- | ---- | --------- | ----------- |
| `fail_new` | bool | **Required** | If the fake board should raise an error at machine start-up. |
| `analogs` | object | Optional | Attributes of any pins that can be used as Analog-to-Digital Converter (ADC) inputs. See [configuration info](#analogs). |
| `digital_interrupts` | object | Optional | Pin and name of any digital interrupts. See [configuration info](#digital_interrupts). |

## Attribute configuration

Configuring these attributes on your board allows you to integrate [analog-to-digital converters](#analogs) and [digital interrupts](#digital_interrupts) into your machine.

### `analogs`

An [analog-to-digital converter](https://www.electronics-tutorials.ws/combination/analogue-to-digital-converter.html) (ADC) takes a continuous voltage input (analog signal) and converts it to an discrete integer output (digital signal).

ADCs are useful when building a robot, as they enable your board to read the analog signal output by most types of [sensors](/reference/components/sensor/) and other hardware components.

To integrate an ADC into your machine, you must first physically connect the pins on your ADC to your board.

Then, integrate `analogs` into the `attributes` of your board by following the **Config Builder** instructions or by adding the following to your board's JSON configuration:

{{< tabs name="Configure an Analog Reader" >}}
{{% tab name="Config Builder" %}}

On your board's panel, click **Show more**, then select **Add analog**.
Assign a name to your analog and then fill in the required properties outlined below.

![An example configuration for analogs.](/components/board/analogs-ui-config.png)

{{% /tab %}}
{{% tab name="JSON Template" %}}

```json {class="line-numbers linkable-line-numbers"}
// "attributes": { ... ,
"analogs": [
  {
    "name": "<your-analog-reader-name>",
    "pin": "<pin-number-on-adc>",
    "spi_bus": "<your-spi-bus-index>",
    "chip_select": "<chip-select-index>",
    "average_over_ms": <int>,
    "samples_per_sec": <int>
  }
]
```

{{% /tab %}}
{{% tab name="JSON Example" %}}

```json {class="line-numbers linkable-line-numbers"}
{
  "components": [
    {
      "model": "pi",
      "name": "your-board",
      "api": "rdk:component:board",
      "attributes": {
        "analogs": [
          {
            "name": "current",
            "pin": "1",
            "spi_bus": "1",
            "chip_select": "0"
          },
          {
            "name": "pressure",
            "pin": "0",
            "spi_bus": "1",
            "chip_select": "0"
          }
        ]
      }
    }
  ]
}
```

{{% /tab %}}
{{< /tabs >}}

The following properties are available for `analogs`:

<!-- prettier-ignore -->
| Name | Type | Required? | Description |
| ---- | ---- | --------- | ----------- |
|`name` | string | **Required** | Your name for the analog reader. |
|`pin`| string | **Required** | The pin number of the ADC's connection pin, wired to the board. This should be labeled as the physical index of the pin on the ADC.
|`chip_select`| string | **Required** | The chip select index of the board's connection pin, wired to the ADC. |
|`spi_bus` | string | **Required** | The index of the SPI bus connecting the ADC and board. |
| `average_over_ms` | int | Optional | Duration in milliseconds over which the rolling average of the analog input should be taken. |
|`samples_per_sec` | int | Optional | Sampling rate of the analog input in samples per second. |

#### Test `analogs`

Once you have configured your analogs, open the board's **TEST** panel on the **CONFIGURE** or [**CONTROL**](/monitor/default-interface/#web-ui) tabs to monitor analogs.
The numbers displayed next to each analog name represent the digital signal received from the analog inputs.

{{<imgproc src="/components/board/analogs-control-tab.png" alt="Analogs in the test panel." resize="800x" style="width:500px" class="imgzoom">}}



### `digital_interrupts`

[Interrupts](https://en.wikipedia.org/wiki/Interrupt) are a method of signaling precise state changes.
Configuring digital interrupts to monitor GPIO pins on your board is useful when your application needs to know precisely when there is a change in GPIO value between high and low.

- When an interrupt configured on your board processes a change in the state of the GPIO pin it is configured to monitor, it ticks to record the state change.
  You can stream these ticks with the board API's [`StreamTicks()`](/reference/apis/components/board/#streamticks), or get the current value of the digital interrupt with [`Value()`](/reference/apis/components/board/#getdigitalinterruptvalue).
- Calling [`GetGPIO()`](/reference/apis/components/board/#getgpio) on a GPIO pin, which you can do without configuring interrupts, is useful when you want to know a pin's value at specific points in your program, but is less precise and convenient than using an interrupt.

Integrate `digital_interrupts` into your machine in the `attributes` of your board by following the **Config Builder** instructions, or by adding the following to your board's JSON configuration:

{{< tabs name="Configure a Digital Interrupt" >}}
{{% tab name="Config Builder" %}}

On your board's panel, click **Show more**, then select **Add digital interrupt**.
Assign a name to your digital interrupt and then enter a pin number.

![An example configuration for digital interrupts.](/components/board/digital-interrupts-ui-config.png)

{{% /tab %}}
{{% tab name="JSON Template" %}}

```json {class="line-numbers linkable-line-numbers"}
// "attributes": { ... ,
"digital_interrupts": [
  {
    "name": "<your-digital-interrupt-name>",
    "pin": "<pin-number>"
  }
]
```

{{% /tab %}}
{{% tab name="JSON Example" %}}

```json {class="line-numbers linkable-line-numbers"}
{
  "components": [
    {
      "model": "pi",
      "name": "your-board",
      "api": "rdk:component:board",
      "attributes": {
        "digital_interrupts": [
          {
            "name": "your-interrupt-1",
            "pin": "15"
          },
          {
            "name": "your-interrupt-2",
            "pin": "16"
          }
        ]
      }
    }
  ]
}
```

{{% /tab %}}
{{< /tabs >}}

The following properties are available for `digital_interrupts`:

<!-- prettier-ignore -->
| Name | Type | Required? | Description |
| ---- | ---- | --------- | ----------- |
|`name` | string | **Required** | Your name for the digital interrupt. |
|`pin`| string | **Required** | The {{< glossary_tooltip term_id="pin-number" text="pin number" >}} of the board's GPIO pin that you wish to configure the digital interrupt for. |

#### Test `digital_interrupts`

Once you have configured your digital interrupts, open the board's **TEST** panel on the **CONFIGURE** or [**CONTROL**](/monitor/default-interface/#web-ui) tabs to monitor interrupt activity.
The value displayed next to each interrupt name represents the total count of interrupts triggered by the corresponding digital interrupt.

{{<imgproc src="/components/board/digital-interrupts-control-tab.png" alt="Digital interrupts in the test panel." resize="800x" style="width:500px" class="imgzoom">}}



