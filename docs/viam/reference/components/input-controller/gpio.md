# gpio

Reference for the gpio input-controller model. GPIO- or ADC-based device as an input controller.
> Source: https://docs.viam.com/reference/components/input-controller/gpio/


Configure a `gpio` input controller to use a GPIO- or ADC-based device to communicate with your machine.

To be able to test your controller as you configure it, physically connect your controller to your machine's computer and turn both on.




### Attributes example

```json
{
  "board": "piboard",
  "buttons": {
    "interrupt1": {
      "control": "ButtonNorth",
      "invert": false,
      "debounce_msec": 5
    },
    "interrupt2": {
      "control": "ButtonSouth",
      "invert": true,
      "debounce_msec": 5
    }
  },
  "axes": {
    "analog1": {
      "control": "AbsoluteX",
      "min": 0,
      "max": 1023,
      "poll_hz": 50,
      "deadzone": 30,
      "min_change": 5,
      "bidirectional": false,
      "invert": false
    },
    "analog2": {
      "control": "AbsoluteY",
      "min": 0,
      "max": 1023,
      "poll_hz": 50,
      "deadzone": 30,
      "min_change": 5,
      "bidirectional": true,
      "invert": true
    }
  },
  "depends_on": ["piboard"]
}
```

### JSON Template

```json
{
  "components": [
    {
      "name": "<your-gpio-input-controller-name>",
      "model": "gpio",
      "api": "rdk:component:input_controller",
      "attributes": {
        "board": "<your-board-name>",
        "buttons": {
          "<your-button-name>": {
            "control": "<button-control-name>",
            "invert": <boolean>,
            "debounce_msec": <int>
          }
        },
        "axes": {
          "<your-axis-name>": {
            "control": "<axis-control-name>",
            "min": <int>,
            "max": <int>,
            "poll_hz": <int>,
            "deadzone": <int>,
            "min_change": <int>,
            "bidirectional": <boolean>,
            "invert": <boolean>
          }
        }
      },
      "depends_on": ["<your-board-name>"]
    }
  ]
}
```

### JSON Example

```json
{
  "components": [
    {
      "name": "my_gpio_ic",
      "model": "gpio",
      "api": "rdk:component:input_controller",
      "attributes": {
        "board": "piboard",
        "buttons": {
          "interrupt1": {
            "control": "ButtonNorth",
            "invert": false,
            "debounce_msec": 5
          },
          "interrupt2": {
            "control": "ButtonSouth",
            "invert": true,
            "debounce_msec": 5
          }
        },
        "axes": {
          "analog1": {
            "control": "AbsoluteX",
            "min": 0,
            "max": 1023,
            "poll_hz": 50,
            "deadzone": 30,
            "min_change": 5,
            "bidirectional": false,
            "invert": false
          },
          "analog2": {
            "control": "AbsoluteY",
            "min": 0,
            "max": 1023,
            "poll_hz": 50,
            "deadzone": 30,
            "min_change": 5,
            "bidirectional": true,
            "invert": true
          }
        }
      },
      "depends_on": ["piboard"]
    }
  ]
}
```



The following attributes are available for `gpio` input controllers:

<!-- prettier-ignore -->
| Name | Type | Required? | Description |
| ---- | ---- | --------- | ----------- |
| `board` | string | **Required**| The name of the board component with GPIO or ADC pins to use as the controlling device. |
| `buttons` | object | **Required** | The [Buttons](/reference/apis/components/input-controller/#button-controls) available for control. These should be connected to the GPIO/ADC board. <br><br> <b>Each button has the following fields:</b> <br><ul><li><code>name</code>: Name of the Digital Interrupt the button/switch is connected to, as configured on the board component.</li><li><code>control</code>: The [Control](/reference/apis/components/input-controller/#control-field) type to use when reporting events as this button's state is changed.</li><li><code>invert</code>: Boolean indicating if the digital input (high/low) should be inverted when reporting button Control value indicating button state.<br> This option is given because digital switches vary between high, `1`, and low, `0`, as their default at rest.<ul><li>*true:* `0` is pressed, and `1` is released.</li><li>*false (default):* `0` is released, and `1` is pressed.</li></ul></li><li><code>debounce_ms</code>: How many milliseconds to wait for the interrupt to settle. This is needed because some switches can be electrically noisy.</li></ul> |
| `axes` | object | **Required** | The [Axes](/reference/apis/components/input-controller/#axis-controls) available for control. These should be connected to the GPIO/ADC board.<br><br>**Each axis has the following fields:**<ul><li><code>name</code>: Name of the Analog Reader that reports ADC values for the axis Control, as configured on the board component.</li><li><code>control</code>: The [Control](/reference/apis/components/input-controller/#control-field) type to use when reporting events as this axis's position is changed.</li><li><code>min</code>: The minimum ADC value that the analog reader can report as this axis's position changes. </li><li><code>max</code>: The maximum ADC value that the analog reader can report as this axis's position changes.</li><li><code>deadzone</code>: The absolute ADC value change from the neutral `0` point to still consider as a neutral position. This option is given so tiny wiggles on loose controls don't result in events being reported.</li><li><code>min_change</code>: The minimum absolute ADC value change from the previous ADC value reading that can occur before reporting a new [`PositionChangeAbs Event`](/reference/apis/components/input-controller/#event-object). This option is given so tiny wiggles on loose controls don't result in events being reported.</li><li><code>bidirectional</code>: Boolean indicating if the axis changes position in 1 direction, like on an analog trigger or pedal, or 2, like on an analog control stick.<ul><li>*true:* The axis should report center, `0`, as halfway between the min/max ADC values.</li><li>*false:* `0` is still the neutral point of the axis, but only positive change values can be reported.</li></ul></li><li><code>poll_hz</code>: How many times per second to check for a new ADC reading that can generate an event.</li><li><code>invert</code>: Boolean indicating if the direction of the axis should be flipped when translating ADC value readings to the axis Control value indicating position change.<ul><li>*true:* flips the direction of the axis so that the minimum ADC value is reported as the maximum axis Control value.</li><li>*false:* keeps the direction of the axis the same, so that the minimum ADC value is reported as the minimum axis Control value.</li></ul></li></ul> |

## Test the input controller

After you configure your input controller, open the input controller's **TEST** panel on the **CONFIGURE** or [**CONTROL**](/monitor/default-interface/#web-ui) tabs.
View the current value of each input on your controller.

{{<imgproc src="/components/input-controller/input-controller-control-tab.png" alt="The input controller component in the test panel." resize="800x" style="width:500px">}}


