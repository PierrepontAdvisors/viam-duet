# incremental

Reference for the incremental encoder model. Incremental encoder.
> Source: https://docs.viam.com/reference/components/encoder/incremental/


Use the `incremental` encoder model to configure [a quadrature encoder](https://en.wikipedia.org/wiki/Incremental_encoder).

Configuring an `incremental` encoder requires specifying the [pin numbers](/reference/glossary/#term-pin-number)
 of the two pins on the board to which the encoder is wired.
These two pins provide the phase outputs used to measure the speed and direction of rotation in relation to a given reference point.

To be able to test the encoder as you configure it, connect the encoder to your machine's computer and power both on.




### JSON Template

```json
{
  "name": "<your-encoder-name>",
  "model": "incremental",
  "api": "rdk:component:encoder",
  "attributes": {
    "board": "<your-board-name>",
    "pins": {
      "a": "<your-first-pin-number>",
      "b": "<your-second-pin-number>"
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
      "model": "pi",
      "api": "rdk:component:board",
      "attributes": {}
    },
    {
      "name": "myEncoder",
      "model": "incremental",
      "api": "rdk:component:encoder",
      "attributes": {
        "board": "local",
        "pins": {
          "a": "13",
          "b": "11"
        }
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
| `pins` | object | **Required** | A struct holding the names of the pins wired to the encoder: <ul> <li> <code>a</code>: [Pin number](/reference/glossary/#term-pin-number)
 of one of the pins to which the encoder is wired. </li> <li> <code>b</code>: Required for two phase encoder. [Pin number](/reference/glossary/#term-pin-number)
 for the second board pin to which the encoder is wired. </li><p>If the encoded motor does not operate as expected, the encoder pins might be configured in reverse, switch the <code>a</code> and <code>b</code> pin definitions in your incremental encoder attributes to reconfigure your encoded motor.</p> </ul> |

Viam also supports a model of encoder called [`"single"`](/reference/components/encoder/single/) which requires only one pin (`i`).

## Test the encoder

Once your encoder is configured and connected, open the encoders's **TEST** panel on the **CONFIGURE** or [**CONTROL**](/monitor/default-interface/#web-ui) tabs.
The ticks count is displayed.
Try moving the encoder (for example, by turning a motor it is attached to) and check whether the count increases as expected.

{{<imgproc src="/components/encoder/control.png" alt="Encoder test panel." resize="800x" style="width:500px" class="imgzoom">}}

If the encoder does not appear on the **TEST** panel, or if you notice unexpected behavior, check your machine's [**LOGS** tab](/monitor/troubleshoot/#check-logs) for errors, and review the configuration.


