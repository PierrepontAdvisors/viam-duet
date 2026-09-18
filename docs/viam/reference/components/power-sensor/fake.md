# fake

Reference for the fake power-sensor model. Fake power sensor to test software without the physical hardware.
> Source: https://docs.viam.com/reference/components/power-sensor/fake/


Configure a `fake` power sensor to test implementing a power sensor component on your machine without any physical hardware:




### JSON Template

```json
{
  "name": "<your-sensor-name>",
  "model": "fake",
  "api": "rdk:component:power_sensor",
  "attributes": {}
}
```



No attributes are available for `fake` power sensors.

## Test the power sensor

After you configure your power sensor, open the power sensor's **TEST** panel on the **CONFIGURE** or [**CONTROL**](/monitor/default-interface/#web-ui) tabs.
The panel contains readings for your voltage, current, and power.

{{<imgproc src="/components/power-sensor/power-sensor-control.png" alt="An instance of the power sensor component's test panel with voltage, current, and power readings." resize="800x" style="width:500px" class="imgzoom">}}


