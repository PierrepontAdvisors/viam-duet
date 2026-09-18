# Using extra parameters with Viam's SDKs

Using the extra parameter on resource API methods with Viam's SDKs.
> Source: https://docs.viam.com/reference/sdks/use-extra-params/


How to [use](#use) and [define](#define) the `extra` parameters that many [resource](/reference/glossary/#term-resource)
 [API methods](/reference/apis/) offer in the Go and Python SDKs.

## Use

You can use `extra` parameters with modular [resource](/reference/glossary/#term-resource)
 implementations that are _models_ of built-in resource types.

For example, a new model of [sensor](/hardware/common-components/add-a-sensor/), or a new model of SLAM service.

The `extra` parameters in that built-in resource type's [API](/reference/apis/) allow users to pass information to a resource's driver that isn't specified as a parameter for all models of the resource type.
This is necessary to keep the API of resource types consistent across, for example, all models of [motor](/hardware/common-components/add-a-motor/) or all models of [camera](/hardware/common-components/add-a-camera/).

Send extra information in an API call in `extra` parameters as follows:




### Python

[`Optional[Dict[str, Any]]`](https://docs.python.org/3/library/typing.html#typing.Optional) indicates you are required to pass in an object of either type `Dict[str, Any]` or `None` as a parameter when calling this method.

An object of type `Dict[str, Any]` is a [dictionary](https://docs.python.org/3/tutorial/datastructures.html#dictionaries) with keys of type [`str`](https://docs.python.org/3/library/stdtypes.html#str) and values of [`any type`](https://docs.python.org/3/library/typing.html#typing.Any),

For example:

```python
async def main():
    # ... Connect to the machine.

    # Get your sensor resource from the machine.
    your_sensor = YourSensor.from_robot(robot, "your-sensor")

    # Define a dictionary containing extra information.
    your_info = {"type": "temperature", "description": "more info", "id": 123}

    # Send this information in an call to the sensor resource's API.
    await your_sensor.get_readings(extra=your_info)
```
<blockquote>
**Tip:**

If passing an object of type `None`, you do not have to specify `None` in the method call.

</blockquote>

### Go

`extra (map[string]interface{})` indicates you are required to pass in an object of either type `map[string]interface{}` or `nil` as a parameter when calling this method.

An object of type `map[string]interface{}` is an [map](https://go.dev/blog/maps) with keys of type [`string`](https://go.dev/blog/strings) and values of [any type that you have cast to an interface](https://jordanorelli.com/post/32665860244/how-to-use-interfaces-in-go).

For example:

```go
func main() {
    ... // Connect to the machine

    // Get your sensor resource from the machine.
    yourSensor, err := sensor.FromProvider(robot, "your-sensor")

    // Define a map containing extra information.
    your_info := map[string]interface{}{"type": "temperature", "description": "more info", "id": 123}

    // Send this information in an call to the sensor resource's API.
    err := yourSensor.Readings(context.Background(), your_info)
}
```
<blockquote>
**Important:**

If passing an object of type `nil`, you must specify `nil` in the method call or the method will fail.

</blockquote>



## Define

If `extra` information must be passed to a resource, it is handled within a new, _modular_ resource model's [custom API](/build-modules/write-a-driver-module/) wrapper.

**Click for instructions on defining a custom model to use extra params**



To do this, define a custom implementation of the resource's API as a new _model_, and modify the resource's API methods to handle the `extra` information you send.
Follow the steps in the [Modular Resources documentation](/build-modules/write-a-driver-module/) to do so.

For an example of how to check the values of keys in an `extra` parameter of a built-in resource [API method](/reference/apis/), reference this modification to the built-in [sensor](/hardware/common-components/add-a-sensor/) resource type's [Readings](/reference/apis/components/sensor/#getreadings) method in the code of a new sensor model:




### Python

```python
# Readings depends on extra parameters.
@abc.abstractmethod
async def get_readings(self,
                       *,
                       extra: Optional[Dict[str, Any]] = None,
                       timeout: Optional[float] = None,
                       **kwargs):

    # Define an empty dictionary for readings.
    readings = {}

    # If extra["type"] is temperature or humidity, get the temperature or
    # humidity from helper functions and return these values as the readings
    # the sensor has provided.
    if extra["type"] == "temperature":
        readings["type"] = get_temp()
    elif extra["type"] == "humidity":
        readings["type"] = get_humidity()
    # If the type is not one of these two cases, raise an exception.
    else:
        raise Exception(f"Invalid sensor reading request: type {type}")

    return readings
```

### Go

```go
// Readings depends on extra parameters.
func (s *mySensor) Readings(ctx context.Context, extra map[string]interface{}) (map[string]interface{}, error) {

    // Define an empty map for readings.
    readings := map[string]interface{}{}

    // If extra["type"] is temperature or humidity, get the temperature or humidity from helper methods and return these values as the readings the sensor has provided.
    if readingType, ok := extra["type"]; ok {
        rType, ok := readingType.(string)
        if !ok {
            return nil, errors.New("invalid sensor reading request")
        }
        switch rType {
        case "temperature":
            readings[rType] = getTemp()
        case "humidity":
            readings[rType] = getHumidity()
        // If the type is not one of these two cases, return an error.
        default:
            return nil, errors.Errorf("Invalid sensor reading request: type %s", rType)
        }
    }

    // Return the readings and `nil`/no error.
    return readings, nil
}
```



See [Create a module](/build-modules/write-a-driver-module/) for more information and instructions on modifying built-in API specifications.




