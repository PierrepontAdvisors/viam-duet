# fake

Reference for the fake generic model. Fake generic component.
> Source: https://docs.viam.com/reference/components/generic/fake/


Configure a `fake` generic component to test implementing a generic component on your machine without any physical hardware:




### JSON Template

```json
{
  "name": "<your-fake-generic-component-name>",
  "model": "fake",
  "api": "rdk:component:generic",
  "attributes": {}
}
```



No attributes are available for the `fake` generic component.
See [GitHub](https://github.com/viamrobotics/rdk/blob/main/components/generic/fake/generic.go) for API call return specifications.

## Test the generic component

After you configure your generic component, open the generic's panel on the [**CONTROL**](/monitor/default-interface/#web-ui) tab.
Use the card to send arbitrary commands to the resource with [`DoCommand()`](/reference/apis/components/generic/#docommand).

{{<imgproc src="/components/generic/generic-control.png" alt="The generic component in control panel." resize="900x" style="width:500px" class="imgzoom shadow">}}

The example above works for interacting with the generic component model shown in [Deploy control logic](/build-modules/write-a-logic-module/), but other components require different commands depending on how `DoCommand()` is implemented.


