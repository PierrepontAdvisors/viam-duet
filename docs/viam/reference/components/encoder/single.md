# single

Reference for the single encoder model. Single encoder.
> Source: https://docs.viam.com/reference/components/encoder/single/


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
    "board": "<your-board-name>",
    "pins": {
      "i": "<your-pin-number-on-board>"
    }
  }
}
```



The following attributes are available for `single` encoders:

<!-- prettier-ignore -->
| Name | Type | Required? | Description |
| ---- | ---- | --------- | ----------- |
| `board` | string | **Required** | The `name` of the [board](/reference/components/board/) to which the encoder is wired. |
| `pins` | object | **Required** | A struct holding the name of the pin wired to the encoder: <ul> <li> <code>i</code>: [Pin number](/reference/glossary/#term-pin-number)
 of the pin to which the encoder is wired. </li> </ul> |

Viam also supports a model of encoder called [`"incremental"`](/reference/components/encoder/incremental/) which uses two pins.

## Test the encoder

Once your encoder is configured and connected, open the encoders's **TEST** panel on the **CONFIGURE** or [**CONTROL**](/monitor/default-interface/#web-ui) tabs.
The ticks count is displayed.
Try moving the encoder (for example, by turning a motor it is attached to) and check whether the count increases as expected.

{{<imgproc src="/components/encoder/control.png" alt="Encoder test panel." resize="800x" style="width:500px" class="imgzoom">}}

If the encoder does not appear on the **TEST** panel, or if you notice unexpected behavior, check your machine's [**LOGS** tab](/monitor/troubleshoot/#check-logs) for errors, and review the configuration.


