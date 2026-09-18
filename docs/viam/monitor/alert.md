# Set up alerts

Configure triggers to receive email, webhook, or push notifications when machines need attention.
> Source: https://docs.viam.com/monitor/alert/


Configure triggers to receive email, webhook, or push notifications when your machines need attention. Triggers fire when specific events occur, such as a sensor reading crossing a threshold, a machine going offline, or error logs appearing.

## Types of alerts

| Trigger type          | Fires when                               | Use case                                                     |
| --------------------- | ---------------------------------------- | ------------------------------------------------------------ |
| Telemetry sync        | Data syncs from a machine to the cloud   | Know when any data arrives                                   |
| Conditional telemetry | Synced data meets a condition you define | CPU above 80%, temperature below freezing, battery under 20% |
| Machine logs          | Error, warning, or info logs appear      | Catch errors without watching the LOGS tab                   |
| Part online           | A machine part comes online              | Know when a machine reconnects after maintenance             |
| Part offline          | A machine part goes offline              | Respond to unexpected disconnections                         |

## Prerequisites

**A running machine connected to Viam.**



Add a new machine on [Viam](https://app.viam.com).
On the machine's page, follow the {{< glossary_tooltip term_id="setup" text="setup instructions" >}} to install `viam-server` on the computer you're using for your project.
Wait until your machine has successfully connected to Viam.





## Alert on telemetry

To alert on sensor data, you need three things: a sensor producing data, the data management service capturing and syncing that data, and a trigger that fires when the data arrives or meets a condition.

### Add a performance sensor

To monitor machine health metrics like CPU usage, memory, and temperature, add a performance metrics sensor.




### Linux

On your machine’s **CONFIGURE** page, click the **+** icon next to your machine part and select **Blocks**.
Search for and add the `hwmonitor:cpu_monitor` model from the [`sbc-hwmonitor`](https://app.viam.com/module/rinzlerlabs/sbc-hwmonitor) module.

You can add additional sensors for memory, temperature, and other metrics.
See the [`sbc-hwmonitor` module page](https://app.viam.com/module/rinzlerlabs/sbc-hwmonitor) for the full list.

### macOS

First install [`telegraf`](https://github.com/influxdata/telegraf):

```sh
brew install telegraf
```
On your machine’s **CONFIGURE** page, click the **+** icon next to your machine part and select **Component**.
Search for and add the [`viam-sensor:telegrafsensor` model](https://github.com/viam-modules/viam-telegraf-sensor).

You can add additional sensors for other metrics.
See the [`viam-telegraf-sensor` module page](https://app.viam.com/module/viam/viam-telegraf-sensor) for the full list.



Click **Save**, then click **Test** at the bottom of the sensor configuration card to verify readings are coming through.

### Configure data capture

1. On your sensor's configuration card, click the **Data Capture** button.
1. If you see a "Data management service missing" banner, click
   **Create data management service**, click **Save**, navigate back to
   your sensor, and click the **Data Capture** button again.
1. Select `Readings` from the **Method** dropdown and set the **Frequency** to `0.05` Hz (once every 20 seconds).
1. Click **Save**.

To verify data is syncing, click the **...** menu on the sensor card and select **View captured data**.
Wait a minute for data to capture and sync, then refresh.

### Configure the trigger




### Builder mode

<ol>
<li>Go to the **CONFIGURE** tab.
Click **+** in the left sidebar and select **Trigger**.</li>
<li>Enter a name and click **Create**.</li>
<li>In the **Type** dropdown, choose:
<ul>
<li>**Data has been synced to the cloud**: fires whenever data of the selected types syncs.</li>
<li>**Conditional data ingestion**: fires when synced data meets a condition you define.
Choose the target component and method, then add a condition with a key, operator, and value.
For example, to alert when CPU usage exceeds 50%: select your cpu-monitor component, Readings method, key `cpu`, operator `greater than`, value `50`.</li>
</ul>
</li>
<li>Add notification methods:
<ul>
<li>**Email specific addresses**: toggle on, add addresses, set alert frequency.</li>
<li>**Email all machine owners**: toggle on, set alert frequency.</li>
<li>**Webhook**: click **Add webhook**, enter your cloud function URL, set alert frequency.
Optionally, check **Use basic authentication** to include HTTP basic authentication credentials with each request.
See [Trigger configuration](/reference/triggers/#webhook-attributes) for webhook payload details.</li>
<li>**Push notifications**: click **Add push notifications**, choose the target mobile app, add recipient email addresses or enable notifications for all machine owners, and set alert frequency.
Recipients must be machine owners or operators.
To route notifications to a custom mobile app instead of the Viam mobile app, see [Set up custom push notifications](/monitor/custom-push-notifications/).</li>
</ul>
</li>
<li>Click **Save**.</li>
</ol>

### JSON mode

Add a `triggers` field to your machine configuration:

<h3 id="telemetry-sync" class="main-content-heading">
    Telemetry sync
    
</h3>
```json
"triggers": [
  {
    "name": "trigger-1",
    "event": {
      "type": "part_data_ingested",
      "data_ingested": {
        "data_types": ["binary", "tabular", "file"]
      }
    },
    "notifications": [
      {
        "type": "email",
        "value": "you@example.com",
        "seconds_between_notifications": 300
      }
    ]
  }
]
```
<h3 id="conditional-telemetry" class="main-content-heading">
    Conditional telemetry
    
</h3>
```json
"triggers": [
  {
    "name": "cpu-alert",
    "event": {
      "type": "conditional_data_ingested",
      "conditional": {
        "data_capture_method": "sensor:cpu-monitor:Readings",
        "conditions": {
          "evals": [
            {
              "operator": "gt",
              "value": {
                "cpu": 50
              }
            }
          ]
        }
      }
    },
    "notifications": [
      {
        "type": "email",
        "value": "you@example.com",
        "seconds_between_notifications": 600
      }
    ]
  }
]
```



### Stop data capture

If this is a test, stop data capture to avoid charges for syncing unwanted data.
In the **Data capture** section of your sensor's configuration, toggle the switch to **Off** and click **Save**.

## Alert on machine logs

Configure a trigger that fires when machine logs of a specified level appear.
Viam checks for matching logs once per hour.




### Builder mode

<ol>
<li>Go to the **CONFIGURE** tab.
Click **+** in the left sidebar and select **Trigger**.</li>
<li>Enter a name and click **Create**.</li>
<li>Select **Conditional logs ingestion** as the trigger **Type**.</li>
<li>Select the log levels to alert on: **Error**, **Warn**, or **Info**.</li>
<li>Add notification methods (email, webhook, or push notification) and set the alert frequency.</li>
<li>Click **Save**.</li>
</ol>

### JSON mode

```json
"triggers": [
  {
    "name": "error-log-alert",
    "event": {
      "type": "conditional_logs_ingested",
      "log_levels": ["error", "warn"]
    },
    "notifications": [
      {
        "type": "email",
        "value": "you@example.com"
      }
    ]
  }
]
```
The notification interval for log triggers is always one hour.



## Alert on machine status

### Part online




### Builder mode

<ol>
<li>Go to the **CONFIGURE** tab.
Click **+** in the left sidebar and select **Trigger**.</li>
<li>Enter a name and click **Create**.</li>
<li>Select **Part is online** as the trigger **Type**.</li>
<li>Add notification methods.</li>
<li>Click **Save**.</li>
</ol>

### JSON mode

```json
"triggers": [
  {
    "name": "machine-online",
    "event": {
      "type": "part_online"
    },
    "notifications": [
      {
        "type": "email",
        "value": "you@example.com"
      }
    ]
  }
]
```
Part online triggers fire on every state transition, so you receive a notification each time the part comes online.



### Part offline




### Builder mode

<ol>
<li>Go to the **CONFIGURE** tab.
Click **+** in the left sidebar and select **Trigger**.</li>
<li>Enter a name and click **Create**.</li>
<li>Select **Part is offline** as the trigger **Type**.</li>
<li>Add notification methods.</li>
<li>Click **Save**.</li>
</ol>

### JSON mode

```json
"triggers": [
  {
    "name": "machine-offline",
    "event": {
      "type": "part_offline"
    },
    "notifications": [
      {
        "type": "email",
        "value": "you@example.com"
      }
    ]
  }
]
```
Part offline triggers fire on every state transition, so you receive a notification each time the part goes offline.



Viam uses a 60-second buffer before declaring a part offline.
This prevents false alerts from brief network interruptions.

## Manage alert frequency

For data and conditional triggers, each notification method has a `seconds_between_notifications` setting that controls the minimum time between consecutive alerts.
If a trigger fires more frequently than this interval, Viam suppresses the extra notifications.

Set this value based on how quickly you need to respond:

- **Safety thresholds**: 60-300 seconds
- **Operational alerts** (elevated CPU, low battery): 300-600 seconds
- **Informational alerts** (data sync confirmations): 3600 seconds or more

Starting with a longer interval and shortening it as needed is better than starting short and dealing with notification noise.

Part online and part offline triggers do not use this setting.
They fire on every state transition, so you receive a notification each time the machine comes online or goes offline.

## Use the CLI

You can also manage triggers from the command line:

```sh {class="command-line" data-prompt="$"}
viam machines part add-trigger --part <part-name-or-id>
```

```sh {class="command-line" data-prompt="$"}
viam machines part delete-trigger --part <part-name-or-id> --name <trigger-name>
```

## Other alert types

- For alerts based on data sync events (not tied to machine health), see [Trigger on data events](/data/trigger-on-data/).
- For alerts when an ML model detects specific objects or classifications, see [Alert on detections](/vision/object-detection/alert-on-detections/).
- For full trigger configuration reference, see [Trigger configuration](/reference/triggers/).

