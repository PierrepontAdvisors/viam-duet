# Connect to the Viam cloud

Open a connection to the Viam cloud to access the fleet, data, ML training, billing, and provisioning APIs, and to enumerate and connect to multiple machines.
> Source: https://docs.viam.com/build-apps/tasks/connect-to-cloud/


Open a connection to the Viam cloud to access the fleet, data, ML training, billing, and provisioning APIs, and to enumerate and connect to multiple machines from one app. For connecting directly to a single known machine, use [Connect to a machine](/build-apps/tasks/connect-to-machine/) instead.

## When to connect to the cloud

Use the cloud connection when your app needs any of these:

- **Multiple machines.** Your app lets users pick from a fleet, shows status across many devices, or connects to different machines based on user input.
- **Machine discovery.** Your app does not know the machine address ahead of time and needs to list machines from an organization or location.
- **Captured data queries.** Your app queries sensor or binary data with SQL or MQL (see [Query captured data](/build-apps/tasks/query-data/)).
- **Fleet management.** Your app creates or manages machines, API keys, locations, or fragments programmatically.
- **Custom provisioning.** Your app onboards new machines through the provisioning service (see [Provision devices](/fleet/provision-devices/)).
- **Billing or ML training.** Your app reads billing information or launches ML training jobs.

If your app only talks to one machine whose address you already know, skip this page and use [Connect to a machine](/build-apps/tasks/connect-to-machine/) directly.

## Prerequisites

- A project set up with the Viam SDK (see [App scaffolding](/build-apps/setup/))
- An API key scoped to the organization or location your app needs to access, and its API key ID. Create an API key in [Admin and access](/organization/access/).

## Open a cloud connection




### TypeScript

```ts
import * as VIAM from "@viamrobotics/sdk";

const client = await VIAM.createViamClient({
  credentials: {
    type: "api-key",
    authEntity: "<API-KEY-ID>",
    payload: "<API-KEY>",
  },
});
```
`createViamClient` returns a `ViamClient` with five platform-client properties:

<table>
  <thead>
      <tr>
          <th>Property</th>
          <th>Purpose</th>
      </tr>
  </thead>
  <tbody>
      <tr>
          <td>`client.appClient`</td>
          <td>Organizations, locations, machines, API keys, fragments, RBAC</td>
      </tr>
      <tr>
          <td>`client.dataClient`</td>
          <td>Query and upload captured data</td>
      </tr>
      <tr>
          <td>`client.mlTrainingClient`</td>
          <td>Launch and monitor ML training jobs</td>
      </tr>
      <tr>
          <td>`client.billingClient`</td>
          <td>Read billing information</td>
      </tr>
      <tr>
          <td>`client.provisioningClient`</td>
          <td>Device provisioning for custom provisioning apps</td>
      </tr>
  </tbody>
</table>
The default `serviceHost` is `https://app.viam.com`. Override it only if you are pointing at a self-hosted Viam platform.

### Flutter

```dart
import 'package:viam_sdk/viam_sdk.dart';

final viam = await Viam.withApiKey(
  'your-api-key-id',
  'your-api-key-secret',
);
```
`Viam.withApiKey` returns a `Viam` instance with five platform-client properties:

<table>
  <thead>
      <tr>
          <th>Property</th>
          <th>Purpose</th>
      </tr>
  </thead>
  <tbody>
      <tr>
          <td>`viam.appClient`</td>
          <td>Organizations, locations, machines, API keys, fragments, RBAC</td>
      </tr>
      <tr>
          <td>`viam.dataClient`</td>
          <td>Query and upload captured data</td>
      </tr>
      <tr>
          <td>`viam.mlTrainingClient`</td>
          <td>Launch and monitor ML training jobs</td>
      </tr>
      <tr>
          <td>`viam.billingClient`</td>
          <td>Read billing information</td>
      </tr>
      <tr>
          <td>`viam.provisioningClient`</td>
          <td>Device provisioning for custom provisioning apps</td>
      </tr>
  </tbody>
</table>
The default `serviceHost` is `app.viam.com`. Override it through the optional `serviceHost` parameter if you are pointing at a self-hosted Viam platform.

### Python

```python
from viam.app.viam_client import ViamClient
from viam.rpc.dial import DialOptions

async def connect():
    dial_options = DialOptions.with_api_key(
        api_key='your-api-key-secret',
        api_key_id='your-api-key-id'
    )
    return await ViamClient.create_from_dial_options(dial_options)

client = await connect()
```
`ViamClient` exposes the same platform clients:

<table>
  <thead>
      <tr>
          <th>Property</th>
          <th>Purpose</th>
      </tr>
  </thead>
  <tbody>
      <tr>
          <td>`client.app_client`</td>
          <td>Organizations, locations, machines, API keys, fragments, RBAC</td>
      </tr>
      <tr>
          <td>`client.data_client`</td>
          <td>Query and upload captured data</td>
      </tr>
      <tr>
          <td>`client.ml_training_client`</td>
          <td>Launch and monitor ML training jobs</td>
      </tr>
      <tr>
          <td>`client.billing_client`</td>
          <td>Read billing information</td>
      </tr>
      <tr>
          <td>`client.provisioning_client`</td>
          <td>Device provisioning for custom provisioning apps</td>
      </tr>
  </tbody>
</table>

### Go

```go
import (
    "context"
    "go.viam.com/rdk/app"
    "go.viam.com/rdk/logging"
)

logger := logging.NewDebugLogger("client")
client, err := app.CreateViamClientWithAPIKey(
    context.Background(),
    app.Options{},
    "your-api-key-secret",
    "your-api-key-id",
    logger,
)
if err != nil {
    logger.Fatal(err)
}
```
Access platform clients through methods on `ViamClient`:

<table>
  <thead>
      <tr>
          <th>Method</th>
          <th>Purpose</th>
      </tr>
  </thead>
  <tbody>
      <tr>
          <td>`client.AppClient()`</td>
          <td>Organizations, locations, machines, API keys, fragments, RBAC</td>
      </tr>
      <tr>
          <td>`client.DataClient()`</td>
          <td>Query and upload captured data</td>
      </tr>
      <tr>
          <td>`client.MLTrainingClient()`</td>
          <td>Launch and monitor ML training jobs</td>
      </tr>
      <tr>
          <td>`client.BillingClient()`</td>
          <td>Read billing information</td>
      </tr>
      <tr>
          <td>`client.ProvisioningClient()`</td>
          <td>Device provisioning</td>
      </tr>
  </tbody>
</table>



Unlike `RobotClient`, the cloud client does not hold a persistent WebRTC connection. Each method call is a separate request to the Viam cloud. There is no `close()` or `disconnect()` method to call when you are done.

## Enumerate machines

Common pattern: list the organizations a user can access, then list machines in a selected organization.




### TypeScript

```ts
const orgs = await client.appClient.listOrganizations();
console.log(`Found ${orgs.length} organizations`);

const orgId = orgs[0].id;
const summaries = await client.appClient.listMachineSummaries(orgId);
for (const location of summaries) {
  console.log(`Location: ${location.locationName}`);
  for (const machine of location.machines) {
    console.log(`  ${machine.machineName} (${machine.machineId})`);
  }
}
```
`listMachineSummaries` returns a list of location summaries, each containing the machines in that location. Pass `fragmentIds` to filter to machines that include specific fragments, or `locationIds` to scope to particular locations.

### Flutter

```dart
final orgs = await viam.appClient.listOrganizations();
print('Found ${orgs.length} organizations');

final orgId = orgs.first.id;
final locations = await viam.appClient.listLocations(orgId);

for (final location in locations) {
  print('Location: ${location.name}');
  final robots = await viam.appClient.listRobots(location.id);
  for (final robot in robots) {
    print('  ${robot.name} (${robot.id})');
  }
}
```



See [the fleet API reference](/reference/apis/fleet/) for the full method list on `AppClient`.

## Connect to a machine from the cloud client

Once you have identified a machine, open a `RobotClient` connection to it.




### TypeScript

```ts
const machine = await client.connectToMachine({
  id: "abc-123-def-456",
});
```
`connectToMachine` accepts either `{ host: "..." }` with the machine’s FQDN or `{ id: "..." }` with the machine’s UUID. It returns a `RobotClient` that behaves the same as one created by `createRobotClient`.

Note that `connectToMachine` uses `reconnectMaxAttempts: 1` instead of the default of 10. If you need the standard reconnection behavior, call `createRobotClient` directly with the host and credentials you obtained from the cloud client.

### Flutter

```dart
final locations = await viam.appClient.listLocations(orgId);
final location = locations.first;
final robots = await viam.appClient.listRobots(location.id);
final robot = robots.first;

final robotClient = await viam.getRobotClient(robot);
```
`getRobotClient` takes a `Robot` object (returned from `appClient.listRobots` or `appClient.getRobot`) and returns a `RobotClient` connected to the machine’s main part.



Close the `RobotClient` when your app is done with the machine. See [Connect to a machine](/build-apps/tasks/connect-to-machine/) for the close pattern and for error handling.

## Handle errors

API key errors, network failures, and missing permissions all raise errors from `createViamClient` or `Viam.withApiKey`. Wrap the call in a try-catch the same way you would for a machine connection. The cloud client does not distinguish credential errors from network errors in its error messages; log the error verbatim when debugging.

If a subsequent `appClient` or `dataClient` call fails because the API key does not have permission for the target resource, the SDK throws an error from that specific call, not from the initial `createViamClient`. Check errors on every cloud method call that accesses resources across organizations or locations.

## Next

- [Query captured data](/build-apps/tasks/query-data/) for using `dataClient` to read sensor and binary data
- [Handle disconnection and reconnection](/build-apps/tasks/handle-connection-state/) for reconnection behavior on the `RobotClient` instances you get from the cloud connection
- [Provision devices](/fleet/provision-devices/) for custom provisioning apps that use `provisioningClient`
- [Fleet API reference](/reference/apis/fleet/) for the full `AppClient` method list
- [Data API reference](/reference/apis/data-client/) for the full `DataClient` method list

