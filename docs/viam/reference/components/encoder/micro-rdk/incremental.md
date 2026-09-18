# incremental

Reference for the incremental encoder model. Incremental encoder.
> Source: https://docs.viam.com/reference/components/encoder/micro-rdk/incremental/


Use the `incremental` encoder model to configure [a quadrature encoder](https://en.wikipedia.org/wiki/Incremental_encoder).

Configuring an `incremental` encoder requires specifying the [pin numbers](/reference/glossary/#term-pin-number)
 of the two pins on the board to which the encoder is wired.
These two pins provide the phase outputs used to measure the speed and direction of rotation in relation to a given reference point.

To be able to test the encoder as you configure it, connect the encoder to your microcontroller and power both on.




### JSON Template

```json
{
  "name": "<your-encoder-name>",
  "model": "incremental",
  "api": "rdk:component:encoder",
  "attributes": {
    "board": "<your-board-name>",
    "a": "<your-first-pin-number>",
    "b": "<your-second-pin-number>"
  }
}
```

### JSON Example

```json
{
  "components": [
    {
      "name": "myEncoder",
      "model": "incremental",
      "api": "rdk:component:encoder",
      "attributes": {
        "board": "local",
        "a": "13",
        "b": "11"
      }
    }
  ]
}
```



The following attributes are available for `incremental` encoders:

<!-- prettier-ignore -->
| Name | Type | Required? | Description |
| ---- | ---- | --------- | ----------- |
| `board` | string | **Required** | The `name` of the [board](/reference/components/board/) to which the encoder is wired. |
| `a` | string | **Required** | GPIO number of one of the pins to which the encoder is wired |
| `b` | string | **Required** | GPIO number of the second board pin to which the encoder is wired |

## Test the encoder

Once your encoder is configured and connected, open the encoders's **TEST** panel on the **CONFIGURE** or [**CONTROL**](/monitor/default-interface/#web-ui) tabs.
The ticks count is displayed.
Try moving the encoder (for example, by turning a motor it is attached to) and check whether the count increases as expected.

{{<imgproc src="/components/encoder/control.png" alt="Encoder test panel." resize="800x" style="width:500px" class="imgzoom">}}

If the encoder does not appear on the **TEST** panel, or if you notice unexpected behavior, check your machine's [**LOGS** tab](/monitor/troubleshoot/#check-logs) for errors, and review the configuration.


