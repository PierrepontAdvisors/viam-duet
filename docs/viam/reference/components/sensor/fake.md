# fake

Reference for the fake sensor model. Fake sensor to use for testing.
> Source: https://docs.viam.com/reference/components/sensor/fake/


Configure a `fake` sensor to test implementing a sensor component on your machine without any physical hardware:




### JSON Template

```json
{
  "name": "<your-sensor-name>",
  "model": "fake",
  "api": "rdk:component:sensor",
  "attributes": {}
}
```



No attributes are available for `fake` sensors.

> **Info:**
> 
> A call to [`Readings()`](/reference/apis/components/sensor/#getreadings) on a `fake` sensor always returns readings of `{"a":1, "b":2, "c":3}`.

