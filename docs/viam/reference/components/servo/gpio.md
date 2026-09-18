# gpio

Reference for the gpio servo model. Gpio servo.
> Source: https://docs.viam.com/reference/components/servo/gpio/


Configure a `gpio` servo to integrate a hobby servo controlled by general-purpose input/output (GPIO) pins on a non-`viam:raspberry-pi:rpi` model [board](/reference/components/board/) into your machine.




### JSON Template

```json
{
  "components": [
    {
      "name": "<your-servo-name>",
      "model": "gpio",
      "api": "rdk:component:servo",
      "attributes": {
        "pin": "<your-pin-number>",
        "board": "<your-board-name>",
        "min_angle_deg": <float>,
        "max_angle_deg": <float>,
        "starting_position_deg": <float>,
        "frequency_hz": <int>,
        "pwm_resolution": <int>,
        "min_width_us": <int>,
        "max_width_us": <int>
      }
    }
  }
```

### JSON Example

```json
{
  "components": [
    {
      "name": "local",
      "model": "jetson",
      "api": "rdk:component:board"
    },
    {
      "name": "my_servo",
      "model": "gpio",
      "api": "rdk:component:servo",
      "attributes": {
        "pin": "16",
        "board": "local"
      }
    }
  ]
}
```



The following attributes are available for `gpio` servos:

<!-- prettier-ignore -->
| Name | Type | Required? | Description |
| ---- | ---- | --------- | ----------- |
| `pin` | string | **Required** | The [pin number](/reference/glossary/#term-pin-number)
 of the pin the servo's control wire is wired to on the [board](/reference/components/board/). |
| `board` | string | **Required** | `name` of the [board](/reference/components/board/) the servo is wired to. |
| `min_angle_deg` | float | Optional | The minimum angle in degrees that the servo can reach. <br> Default = `0.0` <br> Range = [`0.0`, `180.0`] |
| `max_angle_deg` | float | Optional | The maximum angle in degrees that the servo can reach. <br> Default = `180.0` <br> Range = [`0.0`, `180.0`] |
| `starting_position_deg` | float | Optional | Starting position of the servo in degrees. <br> Default = `0.0` <br> Range = [`0.0`, `180.0`] |
| `frequency_hz` | int | Optional | The frequency of [PWM](https://docs.arduino.cc/learn/microcontrollers/analog-output) pulses sent to the servo, in Hertz (*Hz*). <br> Default = [`300`] <br> Range = [`0`, `450`] |
| `pwm_resolution` | int | Optional | The resolution of the [PWM](https://docs.arduino.cc/learn/microcontrollers/analog-output) driver (for example, the number of ticks for a full period). If not specified or given as `0`, the driver will attempt to estimate the resolution. |
| `min_width_us` | int | Optional | Override the safe minimum [PWM](https://docs.arduino.cc/learn/microcontrollers/analog-output) pulse width in microseconds. <br> Range > `450` |
| `max_width_us` | int | Optional | Override the safe maximum [PWM](https://docs.arduino.cc/learn/microcontrollers/analog-output) pulse width in microseconds. <br> Range < `2500` |

> **Tip:**
> 
> Refer to your servo’s data sheet for [pulse-width modulation (PWM)](https://docs.arduino.cc/learn/microcontrollers/analog-output), rotation, and wiring specifications.

## Test the servo

After you establish the connection to your servo motor, open the servo's **TEST** panel on the **CONFIGURE** or [**CONTROL**](/monitor/default-interface/#web-ui) tabs. Use the buttons to move the servo motor to the desired angle.

{{<imgproc src="/components/servo/servo-control-tab.png" alt="The servo component in the test panel" resize="800x" style="width:500px" class="imgzoom">}}


