# fake

Reference for the fake switch model. Fake switch for testing.
> Source: https://docs.viam.com/reference/components/switch/fake/


The `fake` switch model is a model for testing switch functionality without physical hardware.
It simulates a multi-position switch which you can control programmatically.




### JSON Template

```json
{
  "components": [
    {
      "name": "<your-switch-name>",
      "model": "fake",
      "type": "switch",
      "namespace": "rdk",
      "attributes": {
        "position_count": <number>,
        "labels": ["<label1>", "<label2>", "<label3>"]
      }
    }
  ]
}
```

### JSON Example

```json
{
  "components": [
    {
      "name": "my_switch",
      "model": "fake",
      "type": "switch",
      "namespace": "rdk",
      "attributes": {
        "position_count": 4,
        "labels": ["Off", "Low", "Medium", "High"]
      }
    }
  ]
}
```



## Attributes

The following attributes are available for the `fake` switch model:

<!-- prettier-ignore -->
| Name | Type | Required? | Description |
| ---- | ---- | --------- | ----------- |
| `position_count` | int | **Required** | The number of positions that the switch can be in. Default: `2` |
| `labels` | array | Optional | An array of labels corresponding to the positions. Default: numeric values for the number of positions, starting with 0. |

## Troubleshooting

If your fake switch is not working as expected:

1. Check your machine logs on the **LOGS** tab to check for errors.
2. Make sure the `position_count` matches the number of `labels` if both are specified.
3. Verify that position values used with `SetPosition` are within the valid range (0 to `position_count - 1`).
4. Click on the **TEST** panel on the **CONFIGURE** or **CONTROL** tab and test if you can use the switch there.

