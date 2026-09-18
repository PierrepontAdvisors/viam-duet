# fake

Reference for the fake servo model. Fake servo.
> Source: https://docs.viam.com/reference/components/servo/fake/


Configure a `fake` servo to test implementing a servo component on your machine without any physical hardware:




### JSON Template

```json
{
  "name": "<your-fake-servo-name>",
  "model": "fake",
  "api": "rdk:component:servo",
  "attributes": {}
}
```



No attributes are available for fake servos.
See [GitHub](https://github.com/viamrobotics/rdk/blob/main/components/servo/fake/servo.go) for API call return specifications.

## Test the servo

After you establish the connection to your servo motor, open the servo's **TEST** panel on the **CONFIGURE** or [**CONTROL**](/monitor/default-interface/#web-ui) tabs. Use the buttons to move the servo motor to the desired angle.

{{<imgproc src="/components/servo/servo-control-tab.png" alt="The servo component in the test panel" resize="800x" style="width:500px" class="imgzoom">}}


