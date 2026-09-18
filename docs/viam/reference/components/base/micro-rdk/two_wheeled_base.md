# two_wheeled_base

Reference for the two_wheeled_base base model. And wire a two-wheeled base with a microcontroller.
> Source: https://docs.viam.com/reference/components/base/micro-rdk/two_wheeled_base/


A `two_wheeled_base` base supports mobile robotic bases with drive motors on both sides (differential steering).
Only bases with two drive wheels are supported by this `viam-micro-server` model.

> **Info:**
> 
> 
> 
> The`two_wheeled_base` base model is not currently available when configuring your machine using **Builder** mode.
> 
> 

If you want to test your base as you configure it, physically assemble the base, connect it to your machine's computer, and turn it on.




### JSON Template

```json
{
  "components": [
    {
      "name": "<your-base-name>",
      "model": "two_wheeled_base",
      "api": "rdk:component:base",
      "attributes": {
        "left": "<your-left-motor-name>",
        "right": "<your-right-motor-name>"
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
      "name": "my-wheeled-base",
      "model": "two_wheeled_base",
      "api": "rdk:component:base",
      "attributes": {
        "left": "leftm",
        "right": "rightm"
      },
      "depends_on": []
    }, ... <INSERT LEFT AND RIGHT MOTOR CONFIGS>
  ]
}
```



The following attributes are available for `two_wheeled_base` bases:

<!-- prettier-ignore -->
| Name | Type | Required? | Description |
| ---- | ---- | --------- | ----------- |
| `left` | string | **Required** | The `name` of a drive motor on the left side of the base. |
| `right` | string | **Required** | The `name` of a drive motor on the right side of the base. |

