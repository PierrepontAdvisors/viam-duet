# single

Reference for the single encoder model. Single encoder with a microcontroller.
> Source: https://docs.viam.com/reference/components/encoder/micro-rdk/single/


A `single` encoder sends a signal from the rotating encoder over a single wire to one pin on the [board](/reference/components/board/).
The direction of spin is dictated by the [motor](/reference/components/motor/) that has this encoder's name in its `encoder` attribute field.

To be able to test the encoder as you configure it, connect the encoder to your machine's computer and power both on.




### JSON Template

```json
{
  "name": "<your-encoder-name>",
  "model": "single",
  "api": "rdk:component:encoder",
  "attributes": {
    "pin": <int>,
    "dir_flip": <boolean>
  }
}
```

### JSON Example

```json
{
  "name": "<your-encoder-name>",
  "model": "single",
  "api": "rdk:component:encoder",
  "attributes": {
    "pin": 22,
    "dir_flip": false
  }
}
```



The following attributes are available for `single` encoders:

<!-- prettier-ignore -->
| Name | Type | Required? | Description |
| ---- | ---- | --------- | ----------- |
| `pin` | object | **Required** | GPIO number of the pin to which the encoder is wired. |
| `dir_flip` | boolean | **Required** | If the encoder's count should increment or decrement in its initial state before a [`SetPower()`](/reference/apis/components/motor/#setpower) call is made to an encoded [motor](/reference/components/motor/). `true` implies decrement. |

## Test the encoder

Once your encoder is configured and connected, open the encoders's **TEST** panel on the **CONFIGURE** or [**CONTROL**](/monitor/default-interface/#web-ui) tabs.
The ticks count is displayed.
Try moving the encoder (for example, by turning a motor it is attached to) and check whether the count increases as expected.

{{<imgproc src="/components/encoder/control.png" alt="Encoder test panel." resize="800x" style="width:500px" class="imgzoom">}}

If the encoder does not appear on the **TEST** panel, or if you notice unexpected behavior, check your machine's [**LOGS** tab](/monitor/troubleshoot/#check-logs) for errors, and review the configuration.


