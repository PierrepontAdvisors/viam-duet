# ultrasonic

Reference for the ultrasonic sensor model. Ultrasonic sensor with a microcontroller.
> Source: https://docs.viam.com/reference/components/sensor/micro-rdk/ultrasonic/


Configure an `ultrasonic` sensor to integrate the [HC-S204](https://www.sparkfun.com/products/15569) ultrasonic distance sensor into your machine.




### Attributes example

```json
{
  "trigger_pin": "15",
  "echo_interrupt_pin": "18"
}
```

### JSON Template

```json
{
  "components": [
    {
      "name": "<your-ultrasonic-sensor-name>",
      "model": "ultrasonic",
      "api": "rdk:component:sensor",
      "attributes": {
        "trigger_pin": "<pin-number>",
        "echo_interrupt_pin": "<pin-number>"
      },
      "depends_on": []
    }
  ]
}
```

### JSON Example

```json
{
  "components": [
    {
      "name": "my-ultrasonic-sensor",
      "model": "ultrasonic",
      "api": "rdk:component:sensor",
      "attributes": {
        "trigger_pin": "15",
        "echo_interrupt_pin": "18"
      },
      "depends_on": []
    }
  ]
}
```



The following attributes are available for `ultrasonic` sensors:

<!-- prettier-ignore -->
| Attribute | Type | Required? | Description |
| --------- | ---- | --------- | ----------- |
| `trigger_pin` | string | **Required** | The GPIO number of the [board's](/reference/components/board/) GPIO pin that you have wired to the trigger pin of your ultrasonic sensor. |
| `echo_interrupt_pin` | string | **Required** | The GPIO number of the board's GPIO pin that you have wired to the echo pin of your ultrasonic sensor. Please note that unlike the RDK ultrasonic sensor, you must not use a named pin associated with a digital interrupt configured on your board: it will not (currently) work. |
| `timeout_ms`  | int | Optional | Time to wait in milliseconds before initiating a timeout when requesting readings from your ultrasonic sensor. <br> Default: `50` <br> Max: `100` |

