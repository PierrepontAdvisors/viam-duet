# Trigger on data events

Use triggers to send email, webhook, or push notifications when data from the machine is synced.
> Source: https://docs.viam.com/data/trigger-on-data/


Get alerted when your robot's data meets a condition. Triggers send webhooks, email notifications, or push notifications to a mobile app when events occur on a machine, so you can respond to temperature spikes, low battery, detection results, or connectivity changes without polling.

Triggers are configured in the machine's config and are scoped to that machine. Each trigger fires when its event occurs on the specific machine it is configured on.

## Trigger types

Viam supports five trigger types:

| Type                       | Event JSON value            | Fires when                                                                |
| -------------------------- | --------------------------- | ------------------------------------------------------------------------- |
| Data synced                | `part_data_ingested`        | Any data syncs from the machine to the cloud.                             |
| Conditional data ingestion | `conditional_data_ingested` | Synced data meets a specified condition (key, operator, value).           |
| Part online                | `part_online`               | The machine part comes online.                                            |
| Part offline               | `part_offline`              | The machine part goes offline.                                            |
| Conditional logs ingestion | `conditional_logs_ingested` | Machine logs contain errors, warnings, or info messages (checked hourly). |

For the full attribute reference for all trigger types, see [Trigger configuration](/reference/triggers/).

## Configure a trigger




### Builder mode

<ol>
<li>
Go to the **CONFIGURE** tab of your machine.
Click the **+** (Create) button in the left side menu and select **Trigger**.

</li>
<li>
Enter a name and click **Create**.

</li>
<li>
In the **Type** dropdown, choose one of the following event types:

<ul>
<li>
**Data has been synced to the cloud**:
Whenever your machine syncs data of any of the specified data types, the trigger fires.
Then select the data types for which the trigger should send requests.

</li>
<li>
**Conditional data ingestion**:
Whenever your machine syncs data that meets certain criteria, the trigger fires.

<ol>
<li>
Choose the target component and method for your condition.

</li>
<li>
Add a **condition**: specify a **key** in the synced data, an **operator**, and a **value**.
When data from the target component and method syncs from your machine, the trigger uses the key as a path to look up a value in the synced data object.
The trigger applies the operator to the extracted value and the value you specified in your condition.

For example, the following trigger sends an alert when the `cpu-monitor` component’s `Readings` method syncs `cpu` usage greater than `50`:

<picture>
<source srcset="/build/configure/conditional-data-ingested_hu_7819aecfd03b5925.webp" type="image/webp" width="2361" height="800">
<img src="/build/configure/conditional-data-ingested.png" width="2361" height="800" alt="Example conditional data ingestion trigger with a condition." class="shadow imgzoom" id="" style="width: 600px" loading="lazy">
</picture>
To see the data your components are returning, use each component’s **TEST** panel.

For a full reference of trigger configuration attributes, see [Trigger configuration](/reference/triggers/).

</li>
</ol>
</li>
</ul>
</li>
<li>
Next, configure what should happen when an event occurs.
You can add **Webhook**, **Email**, and **Push** notifications:

To add a webhook:

<ol>
<li>Click **Add webhook**.</li>
<li>Add the URL of your cloud function.</li>
<li>Configure the time between notifications.</li>
<li>Optionally, check **Use basic authentication** and enter a username and password to include HTTP basic authentication credentials with each webhook request.</li>
<li>Write your cloud function to process the webhook payload.
Use your cloud function to process data or interact with external APIs, such as Twilio, PagerDuty, or Zapier.</li>
</ol>
To add an email notification for specific email addresses:

<ol>
<li>Toggle **Email specific addresses** on and add the email addresses you wish to be notified whenever this trigger fires.</li>
<li>Set the alert frequency (minimum time between notifications).</li>
</ol>
To add an email notification for all machine owners:

<ol>
<li>Toggle **Email all machine owners** on.</li>
<li>Set the alert frequency (minimum time between notifications).</li>
</ol>
To add a push notification:

<ol>
<li>Click **Add push notifications**.</li>
<li>Choose the target mobile app (Viam mobile or a custom app ID).</li>
<li>Add specific email addresses of recipients who should receive push notifications, or toggle on notifications for all machine owners.
Recipients must be machine owners or operators.</li>
<li>Set the alert frequency (minimum time between notifications).</li>
</ol>
For end-to-end setup of a custom application ID (Firebase upload, device registration, machine authorization), see [Set up custom push notifications](/monitor/custom-push-notifications/).

</li>
</ol>

### JSON Example

The following JSON configuration shows how to set up a trigger that fires when any data is synced to the cloud:

```json
{
  "components": [
    {
      "name": "local",
      "model": "pi",
      "api": "rdk:component:board",
      "attributes": {},
      "depends_on": []
    },
    {
      "name": "my_temp_sensor",
      "model": "bme280",
      "api": "rdk:component:sensor",
      "attributes": {},
      "depends_on": [],
      "service_configs": [
        {
          "type": "data_manager",
          "attributes": {
            "capture_methods": [
              {
                "method": "Readings",
                "additional_params": {},
                "capture_frequency_hz": 0.017
              }
            ]
          }
        }
      ]
    }
  ],
  "triggers": [
    {
      "name": "trigger-1",
      "event": {
        "type": "part_data_ingested",
        "data_ingested": {
          "data_types": ["binary", "tabular", "file", "unspecified"]
        }
      },
      "notifications": [
        {
          "type": "webhook",
          "value": "https://1abcde2ab3cd4efg5abcdefgh10zyxwv.lambda-url.us-east-1.on.aws",
          "seconds_between_notifications": 60
        },
        {
          "type": "email",
          "value": "test@viam.com",
          "seconds_between_notifications": 60
        }
      ]
    }
  ]
}
```
For more information about triggers, see [Trigger Configuration](/reference/triggers/).



## Webhook payload

When a trigger fires and sends a webhook, the HTTP request includes identifying headers (`Org-Id`, `Location-Id`, `Part-Id`, `Robot-Id`) and a JSON body with details about the event. For data triggers (`part_data_ingested`, `conditional_data_ingested`), the body includes the component name, method, timestamps, and the ingested data. For status triggers (`part_online`, `part_offline`), the request is a GET with metadata in headers only.

For the full header and body reference, see [Webhook attributes](/reference/triggers/#webhook-attributes). For example cloud functions that process the payload, see [Example cloud function](/reference/triggers/#example-cloud-function).

## Notification interval

The `seconds_between_notifications` field sets the minimum time between notifications for data triggers (`part_data_ingested` and `conditional_data_ingested`). If a trigger fires more frequently than this interval, additional notifications are suppressed until the interval has elapsed. To avoid floods of notifications, set the interval to a value appropriate for your use case (for example, 3600 to allow at most one alert per hour).

This field is ignored for `part_online` and `part_offline` triggers, which fire on every state transition. It is also ignored for `conditional_logs_ingested` triggers, where the check interval is always one hour.

## Machine telemetry triggers

The **Part online**, **Part offline**, and **Conditional logs ingestion** triggers are primarily used for machine health monitoring rather than data analysis. For step-by-step setup of these trigger types, see [Alert on machine telemetry](/monitor/alert/).

For the full attribute reference for all trigger types, see [Trigger configuration](/reference/triggers/).

