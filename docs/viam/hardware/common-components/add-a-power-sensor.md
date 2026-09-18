# Add a power sensor

Add and configure a power sensor to monitor voltage, current, and power consumption.
> Source: https://docs.viam.com/hardware/common-components/add-a-power-sensor/


Add a power sensor to your machine's configuration so you can monitor voltage, current, and power consumption from the Viam app and from code.

## Concepts

A power sensor component provides three methods:

- `GetVoltage`: voltage in volts and whether it's AC or DC.
- `GetCurrent`: current in amperes and whether it's AC or DC.
- `GetPower`: power in watts.

### Built-in models

- [`fake`](/reference/components/power-sensor/fake/) — A model for testing, with no physical hardware.

### Registry modules

Viam-maintained power-sensor modules:

| Module                                                                         | Sensors supported                            |
| ------------------------------------------------------------------------------ | -------------------------------------------- |
| [`viam:texas-instruments`](https://app.viam.com/module/viam/texas-instruments) | Texas Instruments INA219 and INA226 monitors |

For power sensors not covered above (Renogy controllers, other chips), search for `power sensor` in the [Viam registry](https://app.viam.com/registry).

## Steps

### 1. Prerequisites

- Your machine is online in the Viam app.
- A [board component](/hardware/common-components/add-a-board/) is configured (for I2C
  communication).
- Your power sensor is wired: I2C data and clock lines to the board, power
  measurement lines in the circuit you want to monitor.

### 2. Add a power sensor component

1. Click the **+** button.
2. Select **Blocks**.
3. Search for the power sensor model that matches your hardware. Search
   by chip name (for example, **ina219**, **ina226**).
4. Name it (for example, `battery-monitor`) and click **Add to machine**.

### 3. Configure attributes

**INA219 example:**

```json
{
  "board": "my-board",
  "i2c_bus": "1",
  "i2c_address": 64
}
```

| Attribute     | Type   | Required | Description                                   |
| ------------- | ------ | -------- | --------------------------------------------- |
| `board`       | string | Yes      | Name of the board component.                  |
| `i2c_bus`     | string | Yes      | I2C bus number (typically `"1"`).             |
| `i2c_address` | int    | No       | I2C address. Default: `64` (0x40) for INA219. |

### 4. Save and test

Click **Save**, then expand the **Test** section.

- The test panel shows voltage, current, and power readings.
- Verify the voltage matches what you expect from your power supply or
  battery.

## Try it

Read voltage, current, and power programmatically.

To get the credentials for the code below, go to your machine's page in the Viam app, click the **CONNECT** tab, and select **API keys**.
Copy the **Key** and **ID**.
Then click the **CONFIGURE** tab, and click **Details**, and copy the **Remote address**.
When you run the code below, you'll see voltage, current, and power readings. Verify the voltage matches your power supply.



### Python

Install the Viam Python SDK in a virtual environment by following [Install the Python SDK](/reference/sdks/python/python-venv/).

Save this as `power_sensor_test.py`:

```python
import asyncio
from viam.robot.client import RobotClient
from viam.components.power_sensor import PowerSensor

async def main():
    opts = RobotClient.Options.with_api_key(
        api_key="YOUR-API-KEY",
        api_key_id="YOUR-API-KEY-ID"
    )
    robot = await RobotClient.at_address("YOUR-MACHINE-ADDRESS", opts)

    sensor = PowerSensor.from_robot(robot, "battery-monitor")

    voltage, is_ac = await sensor.get_voltage()
    print(f"Voltage: {voltage:.2f}V ({'AC' if is_ac else 'DC'})")

    current, is_ac = await sensor.get_current()
    print(f"Current: {current:.3f}A ({'AC' if is_ac else 'DC'})")

    power = await sensor.get_power()
    print(f"Power: {power:.2f}W")

    await robot.close()

if __name__ == "__main__":
    asyncio.run(main())
```
Run it:

```bash
python power_sensor_test.py
```
You should see output like:

```text
Voltage: 12.34V (DC)
Current: 0.567A (DC)
Power: 6.99W
```

### Go

```bash
mkdir power-sensor-test && cd power-sensor-test
go mod init power-sensor-test
go get go.viam.com/rdk
```
Save this as `main.go`:

```go
package main

import (
    "context"
    "fmt"

    "go.viam.com/rdk/components/powersensor"
    "go.viam.com/rdk/logging"
    "go.viam.com/rdk/robot/client"
)

func main() {
    ctx := context.Background()
    logger := logging.NewLogger("power-sensor-test")

    robot, err := client.New(ctx, "YOUR-MACHINE-ADDRESS", logger,
        client.WithDialOptions(client.WithEntityCredentials(
            "YOUR-API-KEY-ID",
            client.Credentials{
                Type:    client.CredentialsTypeAPIKey,
                Payload: "YOUR-API-KEY",
            })),
    )
    if err != nil {
        logger.Fatal(err)
    }
    defer robot.Close(ctx)

    sensor, err := powersensor.FromProvider(robot, "battery-monitor")
    if err != nil {
        logger.Fatal(err)
    }

    voltage, isAC, err := sensor.Voltage(ctx, nil)
    if err != nil {
        logger.Fatal(err)
    }
    acdc := "DC"
    if isAC {
        acdc = "AC"
    }
    fmt.Printf("Voltage: %.2fV (%s)\n", voltage, acdc)

    current, isAC, err := sensor.Current(ctx, nil)
    if err != nil {
        logger.Fatal(err)
    }
    acdc = "DC"
    if isAC {
        acdc = "AC"
    }
    fmt.Printf("Current: %.3fA (%s)\n", current, acdc)

    power, err := sensor.Power(ctx, nil)
    if err != nil {
        logger.Fatal(err)
    }
    fmt.Printf("Power: %.2fW\n", power)
}
```
Run it:

```bash
go run main.go
```



## Troubleshooting

**No readings or all zeros**



- Verify I2C wiring: SDA and SCL to the correct board pins.
- Check the I2C address. Run `i2cdetect -y 1` to confirm the sensor is
  visible on the bus.
- Ensure the power sensor is wired in-line with the circuit you want to
  measure (current sensing requires the sensor to be in the current path).




**Current reads zero but voltage is correct**



- The shunt resistor may not be in the current path. INA219/INA226 measure
  current by reading the voltage drop across a shunt resistor. The load
  current must flow through it.




If your power sensor is not working as expected, follow these steps:

1. Check your machine logs on the **LOGS** tab to check for errors.
1. Review this power sensor model's documentation to ensure you have configured all required attributes.
1. Click on the **TEST** panel on the **CONFIGURE** or **CONTROL** tab and test if you can use the power sensor there.

If none of these steps work, reach out to us on the [Community Discord](https://discord.gg/viam) and we will be happy to help.

## Related

- [Power sensor API reference](/reference/apis/components/power-sensor/): full method documentation.
- [Capture and Sync Data](/data/capture-sync/capture-and-sync-data/): log power
  consumption over time.
- [What is a module?](/build-modules/overview/): write a module that
  alerts on low battery or high current draw.

