# Upload and retrieve data with Viam's data client API

Use the data client API to upload and retrieve data directly.
> Source: https://docs.viam.com/reference/apis/data-client/


The data client allows you to upload and retrieve data to and from the Viam Cloud.

The data client API supports the following methods:

Methods to upload data like images or sensor readings directly to Viam:

<!-- prettier-ignore -->
| Method Name | Description |
| ----------- | ----------- |
| [`BinaryDataCaptureUpload`](/reference/apis/data-client/#binarydatacaptureupload) | Upload binary data collected on your machine through a specific component and the relevant metadata to Viam. |
| [`TabularDataCaptureUpload`](/reference/apis/data-client/#tabulardatacaptureupload) | Upload tabular data collected on your machine through a specific {{< glossary_tooltip term_id="component" text="component" >}} to Viam. |
| [`FileUpload`](/reference/apis/data-client/#fileupload) | Upload arbitrary files stored on your machine to Viam by file name. |
| [`FileUploadFromPath`](/reference/apis/data-client/#fileuploadfrompath) | Upload files stored on your machine to Viam by filepath. |
| [`StreamingDataCaptureUpload`](/reference/apis/data-client/#streamingdatacaptureupload) | Upload the contents of streaming binary data and the relevant metadata to Viam. |


Methods to download, filter, tag, or perform other tasks on data like images or sensor readings:

<!-- prettier-ignore -->
| Method Name | Description |
| ----------- | ----------- |
| [`GetLatestTabularData`](/reference/apis/data-client/#getlatesttabulardata) | Gets the most recent tabular data captured from the specified data source, as long as it was synced within the last year. |
| [`ExportTabularData`](/reference/apis/data-client/#exporttabulardata) | Obtain unified tabular data and metadata from the specified data source. |
| [`TabularDataByFilter`](/reference/apis/data-client/#tabulardatabyfilter) | Retrieve optionally filtered tabular data from Viam. |
| [`TabularDataBySQL`](/reference/apis/data-client/#tabulardatabysql) | Obtain unified tabular data and metadata, queried with SQL. Make sure your API key has permissions at the organization level in order to use this. |
| [`TabularDataByMQL`](/reference/apis/data-client/#tabulardatabymql) | Obtain unified tabular data and metadata, queried with MQL. |
| [`BinaryDataByFilter`](/reference/apis/data-client/#binarydatabyfilter) | Retrieve optionally filtered binary data from Viam. |
| [`BinaryDataByIDs`](/reference/apis/data-client/#binarydatabyids) | Retrieve binary data from Viam by `BinaryID`. |
| [`DeleteTabularData`](/reference/apis/data-client/#deletetabulardata) | Delete tabular data older than a specified number of days. |
| [`DeleteBinaryDataByFilter`](/reference/apis/data-client/#deletebinarydatabyfilter) | Filter and delete binary data. |
| [`DeleteBinaryDataByIDs`](/reference/apis/data-client/#deletebinarydatabyids) | Filter and delete binary data by ids. |
| [`AddTagsToBinaryDataByIDs`](/reference/apis/data-client/#addtagstobinarydatabyids) | Add tags to binary data by ids. |
| [`RemoveTagsFromBinaryDataByIDs`](/reference/apis/data-client/#removetagsfrombinarydatabyids) | Remove tags from binary by ids. |
| [`TagsByFilter`](/reference/apis/data-client/#tagsbyfilter) | Get a list of tags using a filter. |
| [`AddBoundingBoxToImageByID`](/reference/apis/data-client/#addboundingboxtoimagebyid) | Add a bounding box to an image specified by its BinaryID. |
| [`RemoveBoundingBoxFromImageByID`](/reference/apis/data-client/#removeboundingboxfromimagebyid) | Removes a bounding box from an image specified by its BinaryID. |
| [`BoundingBoxLabelsByFilter`](/reference/apis/data-client/#boundingboxlabelsbyfilter) | Get a list of bounding box labels using a Filter. |
| [`GetDatabaseConnection`](/reference/apis/data-client/#getdatabaseconnection) | Get a connection to access a MongoDB Atlas Data federation instance. |
| [`ConfigureDatabaseUser`](/reference/apis/data-client/#configuredatabaseuser) | Configure a database user for the Viam organization’s MongoDB Atlas Data Federation instance. |
| [`AddBinaryDataToDatasetByIDs`](/reference/apis/data-client/#addbinarydatatodatasetbyids) | Add the `BinaryData` to the provided dataset. |
| [`RemoveBinaryDataFromDatasetByIDs`](/reference/apis/data-client/#removebinarydatafromdatasetbyids) | Remove the BinaryData from the provided dataset. |
| [`GetDataPipeline`](/reference/apis/data-client/#getdatapipeline) | Get the configuration for a data pipeline. |
| [`ListDataPipelines`](/reference/apis/data-client/#listdatapipelines) | List all of the data pipelines in an organization. |
| [`CreateDataPipeline`](/reference/apis/data-client/#createdatapipeline) | Create a data pipeline. |
| [`DeleteDataPipeline`](/reference/apis/data-client/#deletedatapipeline) | Delete a data pipeline, its execution history, and all of its output data. |
| [`ListDataPipelineRuns`](/reference/apis/data-client/#listdatapipelineruns) | Get information about individual executions of a data pipeline. |
| [`RenameDataPipeline`](/reference/apis/data-client/#renamedatapipeline) | Rename a data pipeline. |
| [`AddTagsToBinaryDataByFilter`](/reference/apis/data-client/#addtagstobinarydatabyfilter) | Add tags to binary data by filter. |
| [`CreateBinaryDataSignedURL`](/reference/apis/data-client/#createbinarydatasignedurl) | Create a signed URL for accessing binary data without authentication. The URL expires after the specified duration. |
| [`CreateIndex`](/reference/apis/data-client/#createindex) | Create a custom index on your data to speed up queries. You specify the organization, the collection type (tabular or binary), and the fields to index. |
| [`DeleteIndex`](/reference/apis/data-client/#deleteindex) | Delete a custom index from your data. |
| [`ListIndexes`](/reference/apis/data-client/#listindexes) | List all custom indexes for an organization. |
| [`RemoveTagsFromBinaryDataByFilter`](/reference/apis/data-client/#removetagsfrombinarydatabyfilter) | Remove tags from binary data by filter. |
| [`UpdateBoundingBox`](/reference/apis/data-client/#updateboundingbox) | Update an existing bounding box on an image. You can change the label, position, or dimensions of the bounding box. |


Methods to work with datasets:

<!-- prettier-ignore -->
| Method Name | Description |
| ----------- | ----------- |
| [`CreateDataset`](/reference/apis/data-client/#createdataset) | Create a new dataset. |
| [`DeleteDataset`](/reference/apis/data-client/#deletedataset) | Delete a dataset. |
| [`RenameDataset`](/reference/apis/data-client/#renamedataset) | Rename a dataset specified by the dataset ID. |
| [`ListDatasetsByOrganizationID`](/reference/apis/data-client/#listdatasetsbyorganizationid) | Get the datasets in an organization. |
| [`ListDatasetsByIDs`](/reference/apis/data-client/#listdatasetsbyids) | Get a list of datasets using their IDs. |


## Establish a connection

To use the data client API, you need to instantiate a `ViamClient` and then instantiate a `DataClient`.

You need an API key and API key ID with at least [Machine operator permissions](/organization/rbac/#organization-settings-and-roles) to use the data client API.
To get an API key (and corresponding ID), use the [web UI](/organization/api-keys/#create-an-api-key)
to the [Viam CLI](/cli/).




### From a client application

<h3 id="python" class="main-content-heading">
    Python
    
</h3>
```python
import asyncio

from viam.rpc.dial import DialOptions, Credentials
from viam.app.viam_client import ViamClient

async def connect() -> ViamClient:
    dial_options = DialOptions(
      credentials=Credentials(
        type="api-key",
        # TODO: Replace "<API-KEY>" (including brackets) with your machine's
        # API key
        payload='<API-KEY>',
      ),
      # TODO: Replace "<API-KEY-ID>" (including brackets) with your machine's
      # API key ID
      auth_entity='<API-KEY-ID>'
    )
    return await ViamClient.create_from_dial_options(dial_options)

async def main():
    # Make a ViamClient
    async with await connect() as viam_client:
        # Instantiate a DataClient to run data client API methods on
        data_client = viam_client.data_client

if __name__ == '__main__':
    asyncio.run(main())
```
<h3 id="go" class="main-content-heading">
    Go
    
</h3>
```go
package main

import (
  "context"

  "go.viam.com/rdk/app"
  "go.viam.com/rdk/logging"
)

func main() {
  logger := logging.NewDebugLogger("client")
  ctx := context.Background()
  // TODO: Replace "<API-KEY>" (including brackets) with your machine's API key
  // TODO: Replace "<API-KEY-ID>" (including brackets) with your machine's
  // API key ID
  viamClient, err := app.CreateViamClientWithAPIKey(
    ctx, app.Options{}, "<API-KEY>", "<API-KEY-ID>", logger)
  if err != nil {
    logger.Fatal(err)
  }
  defer viamClient.Close()

  dataClient := viamClient.DataClient()
}
```
<h3 id="typescript" class="main-content-heading">
    TypeScript
    
</h3>
```ts
async function connect(): Promise<VIAM.ViamClient> {
  // TODO: Replace "<API-KEY-ID>" (including brackets) with your machine's
  const API_KEY_ID = "<API-KEY-ID>";
  // TODO: Replace "<API-KEY>" (including brackets) with your machine's API key
  const API_KEY = "<API-KEY>";
  const opts: VIAM.ViamClientOptions = {
    serviceHost: "https://app.viam.com:443",
    credentials: {
      type: "api-key",
      authEntity: API_KEY_ID,
      payload: API_KEY,
    },
  };

  const client = await VIAM.createViamClient(opts);
  return client;
}

const viamClient = await connect();
const dataClient = viamClient.dataClient;
```

### From within a Module

See [Use platform APIs from within a module](/build-modules/platform-apis/).



Once you have instantiated a `DataClient`, you can run [API methods](#api) against the `DataClient` object (named `data_client` in the examples).

## API

### BinaryDataCaptureUpload

Upload binary data collected on your machine through a specific component and the relevant metadata to [Viam](https://app.viam.com).
Uploaded binary data can be found under the **Images**, **Point clouds**, or **Files** subtab of the [**Data** tab](https://app.viam.com/data), depending on the type of data that you upload.
{{< tabs >}}
{{% tab name="Python" %}}

**Parameters:**

- `binary_data` ([bytes](https://docs.python.org/3/library/stdtypes.html#bytes-objects)) (required): The data to be uploaded, represented in bytes.
- `part_id` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (required): Part ID of the component used to capture the data.
- `component_type` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (required): Type of the component used to capture the data (for example, “movement_sensor”).
- `component_name` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (required): Name of the component used to capture the data.
- `method_name` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (required): Name of the method used to capture the data.
- `file_extension` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (required): The file extension of binary data, including the period, for example .jpg, .png, .pcd. The backend routes the binary to its corresponding mime type based on this extension. Files with a .jpeg, .jpg, or .png extension will appear in the Images tab.
- `method_parameters` (Mapping[[str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str), Any]) (optional): Optional dictionary of method parameters. No longer in active use.
- `tags` (List[[str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)]) (optional): Optional list of tags to allow for tag-based data filtering when retrieving data.
- `dataset_ids` (List[[str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)]) (optional): Optional list of datasets to add the data to.
- `data_request_times` (Tuple[[datetime.datetime](https://docs.python.org/3/library/datetime.html), [datetime.datetime](https://docs.python.org/3/library/datetime.html)]) (optional): Optional tuple containing datetime objects denoting the times this data was requested [0] by the robot and received [1] from the appropriate sensor.
- `mime_type` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (optional): Optional mime type of the data.

**Returns:**

- ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)): :   The binary data ID of the uploaded data.

**Raises:**

- (GRPCError): If an invalid part ID is passed.

**Example:**

```python {class="line-numbers linkable-line-numbers"}
time_requested = datetime(2023, 6, 5, 11)
time_received = datetime(2023, 6, 5, 11, 0, 3)

file_id = await data_client.binary_data_capture_upload(
    part_id="INSERT YOUR PART ID",
    component_type='camera',
    component_name='my_camera',
    method_name='GetImages',
    method_parameters=None,
    tags=["tag_1", "tag_2"],
    data_request_times=[time_requested, time_received],
    file_extension=".jpg",
    binary_data=b"Encoded image bytes",
    dataset_ids=["dataset_1", "dataset_2"]
)
```

For more information, see the [Python SDK Docs](https://python.viam.dev/autoapi/viam/app/data_client/index.html#viam.app.data_client.DataClient.binary_data_capture_upload).

{{% /tab %}}
{{% tab name="TypeScript" %}}

**Parameters:**

- `binaryData` (Uint8Array) (required): The data to be uploaded, represented in bytes.
- `partId` (string) (required): The part ID of the component used to capture the data.
- `componentType` (string) (required): The type of the component used to capture the data (for example,
  "movementSensor").
- `componentName` (string) (required): The name of the component used to capture the data.
- `methodName` (string) (required): The name of the method used to capture the data.
- `dataRequestTimes` (Date) (required): Tuple containing `Date` objects denoting the times this data was
  requested[0] by the robot and received[1] from the appropriate sensor.
- `options` ([BinaryDataCaptureUploadOptions](https://ts.viam.dev/interfaces/BinaryDataCaptureUploadOptions.html)) (optional): Optional parameters including `mimeType`, `fileExtension`, `tags`, and
  `datasetIds`.

**Returns:**

- (Promise<string>): The binary data ID of the uploaded data.

**Example:**

```ts {class="line-numbers linkable-line-numbers"}
const binaryDataId = await dataClient.binaryDataCaptureUpload(
  binaryData,
  '123abc45-1234-5678-90ab-cdef12345678',
  'rdk:component:camera',
  'my-camera',
  'ReadImage',
  [new Date('2025-03-19'), new Date('2025-03-19')],
  { mimeType: 'image/jpeg' },
);
```

For more information, see the [TypeScript SDK Docs](https://ts.viam.dev/interfaces/DataClient.html#binarydatacaptureupload).

{{% /tab %}}
{{% tab name="Flutter" %}}

**Parameters:**

- `binaryData` [List](https://api.flutter.dev/flutter/dart-core/List-class.html)<[int](https://api.flutter.dev/flutter/dart-core/int-class.html)> (required)
- `partId` [String](https://api.flutter.dev/flutter/dart-core/String-class.html) (required)
- `fileExtension` [String](https://api.flutter.dev/flutter/dart-core/String-class.html) (required)
- `componentType` [String](https://api.flutter.dev/flutter/dart-core/String-class.html)? (optional)
- `componentName` [String](https://api.flutter.dev/flutter/dart-core/String-class.html)? (optional)
- `methodName` [String](https://api.flutter.dev/flutter/dart-core/String-class.html)? (optional)
- `methodParameters` [Map](https://api.flutter.dev/flutter/dart-core/Map-class.html)<[String](https://api.flutter.dev/flutter/dart-core/String-class.html), Any>? (optional)
- `dataRequestTimes` ([DateTime](https://api.flutter.dev/flutter/dart-core/DateTime-class.html), [DateTime](https://api.flutter.dev/flutter/dart-core/DateTime-class.html))? (optional)
- `datasetIds` [Iterable](https://api.flutter.dev/flutter/dart-core/Iterable-class.html)<[String](https://api.flutter.dev/flutter/dart-core/String-class.html)> (optional)
- `tags` [Iterable](https://api.flutter.dev/flutter/dart-core/Iterable-class.html)<[String](https://api.flutter.dev/flutter/dart-core/String-class.html)> (optional)

**Returns:**

- [Future](https://api.flutter.dev/flutter/dart-async/Future-class.html)<[String](https://api.flutter.dev/flutter/dart-core/String-class.html)>

**Example:**

```dart {class="line-numbers linkable-line-numbers"}
_viam = await Viam.withApiKey(
     dotenv.env['API_KEY_ID'] ?? '',
     dotenv.env['API_KEY'] ?? ''
 );
 final dataClient = _viam.dataClient;

 try {
   final imageBytes = getPNGasBytes(); // Replace with your image bytes getter

   (DateTime, DateTime) dataRequestTimes = (
     DateTime(2025, 1, 15, 10, 30), // Start time
     DateTime(2025, 1, 15, 14, 45)  // End time
   );

   final binaryDataId = await dataClient.binaryDataCaptureUpload(
     imageBytes,
     "<YOUR-PART-ID>",
     ".png",
     componentType: "rdk:component:camera",
     componentName: "camera-1",
     methodName: "ReadImage",
     dataRequestTimes: dataRequestTimes);

   print('Successfully uploaded binary data with binaryDataId: $binaryDataId');
 } catch (e) {
   print('Error uploading binary data: $e');
 }
```

For more information, see the [Flutter SDK Docs](https://flutter.viam.dev/viam_sdk/DataClient/binaryDataCaptureUpload.html).

{{% /tab %}}
{{< /tabs >}}

### TabularDataCaptureUpload

Upload tabular data collected on your machine through a specific {{< glossary_tooltip term_id="component" text="component" >}} to [Viam](https://app.viam.com).
Uploaded tabular data can be found under the **Sensors** subtab of the [**Data** tab](https://app.viam.com/data).

{{< alert title="Size limit" color="note" >}}
Viam enforces a maximum size of 4MB for any single reading for tabular data.
{{< /alert >}}
{{< tabs >}}
{{% tab name="Python" %}}

**Parameters:**

- `tabular_data` (List[Mapping[[str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str), Any]]) (required): List of the data to be uploaded, represented tabularly as a collection of dictionaries. Must include the key readings for sensors.
- `part_id` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (required): Part ID of the component used to capture the data.
- `component_type` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (required): Type of the component used to capture the data (for example, rdk:component:movement_sensor).
- `component_name` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (required): Name of the component used to capture the data.
- `method_name` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (required): Name of the method used to capture the data.
- `data_request_times` (List[Tuple[[datetime.datetime](https://docs.python.org/3/library/datetime.html), [datetime.datetime](https://docs.python.org/3/library/datetime.html)]]) (required): List of tuples, each containing datetime objects denoting the times this data was requested [0] by the robot and received [1] from the appropriate sensor. Pass a list of tabular data and timestamps with length n > 1 to upload n datapoints, all with the same metadata.
- `method_parameters` (Mapping[[str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str), Any]) (optional): Optional dictionary of method parameters. No longer in active use.
- `tags` (List[[str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)]) (optional): Optional list of tags to allow for tag-based data filtering when retrieving data.

**Returns:**

- ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)): :   The file ID of the uploaded data.

**Raises:**

- (GRPCError): If an invalid part ID is passed.
- (ValueError): If the provided list of Timestamp objects has a length that does not match the length of the list of tabular data.

**Example:**

```python {class="line-numbers linkable-line-numbers"}
from datetime import datetime

time_requested = datetime(2023, 6, 5, 11)
time_received = datetime(2023, 6, 5, 11, 0, 3)
file_id = await data_client.tabular_data_capture_upload(
    part_id="INSERT YOUR PART ID",
    component_type='rdk:component:movement_sensor',
    component_name='my_movement_sensor',
    method_name='Readings',
    tags=["sensor_data"],
    data_request_times=[(time_requested, time_received)],
    tabular_data=[{
        'readings': {
            'linear_velocity': {'x': 0.5, 'y': 0.0, 'z': 0.0},
            'angular_velocity': {'x': 0.0, 'y': 0.0, 'z': 0.1}
        }
    }]
)
```

For more information, see the [Python SDK Docs](https://python.viam.dev/autoapi/viam/app/data_client/index.html#viam.app.data_client.DataClient.tabular_data_capture_upload).

{{% /tab %}}
{{% tab name="TypeScript" %}}

**Parameters:**

- `tabularData` (Record) (required): The list of data to be uploaded, represented tabularly as an array.
- `partId` (string) (required): The part ID of the component used to capture the data.
- `componentType` (string) (required): The type of the component used to capture the data (for example,
  "movementSensor").
- `componentName` (string) (required): The name of the component used to capture the data.
- `methodName` (string) (required): The name of the method used to capture the data.
- `dataRequestTimes` (Date) (required): Array of Date tuples, each containing two `Date` objects denoting the
  times this data was requested[0] by the robot and received[1] from the appropriate sensor.
  Passing a list of tabular data and Timestamps with length n > 1 will result in n datapoints
  being uploaded, all tied to the same metadata.
- `tags` (string) (optional): The list of tags to allow for tag-based filtering when retrieving data.

**Returns:**

- (Promise<string>): The file ID of the uploaded data.

**Example:**

```ts {class="line-numbers linkable-line-numbers"}
const fileId = await dataClient.tabularDataCaptureUpload(
  [
    {
      readings: {
        timestamp: '2025-03-26T10:00:00Z',
        value: 10,
      },
    },
  ],
  '123abc45-1234-5678-90ab-cdef12345678',
  'rdk:component:sensor',
  'my-sensor',
  'Readings',
  [[new Date('2025-03-26T10:00:00Z'), new Date('2025-03-26T10:00:00Z')]],
);
```

For more information, see the [TypeScript SDK Docs](https://ts.viam.dev/interfaces/DataClient.html#tabulardatacaptureupload).

{{% /tab %}}
{{% tab name="Flutter" %}}

**Parameters:**

- `tabularData` [List](https://api.flutter.dev/flutter/dart-core/List-class.html)<[Map](https://api.flutter.dev/flutter/dart-core/Map-class.html)<[String](https://api.flutter.dev/flutter/dart-core/String-class.html), dynamic>> (required)
- `partId` [String](https://api.flutter.dev/flutter/dart-core/String-class.html) (required)
- `componentType` [String](https://api.flutter.dev/flutter/dart-core/String-class.html)? (optional)
- `componentName` [String](https://api.flutter.dev/flutter/dart-core/String-class.html)? (optional)
- `methodName` [String](https://api.flutter.dev/flutter/dart-core/String-class.html)? (optional)
- `methodParameters` [Map](https://api.flutter.dev/flutter/dart-core/Map-class.html)<[String](https://api.flutter.dev/flutter/dart-core/String-class.html), Any>? (optional)
- `dataRequestTimes` [List](https://api.flutter.dev/flutter/dart-core/List-class.html)<([DateTime](https://api.flutter.dev/flutter/dart-core/DateTime-class.html), [DateTime](https://api.flutter.dev/flutter/dart-core/DateTime-class.html))>? (optional)
- `tags` [Iterable](https://api.flutter.dev/flutter/dart-core/Iterable-class.html)<[String](https://api.flutter.dev/flutter/dart-core/String-class.html)> (optional)

**Returns:**

- [Future](https://api.flutter.dev/flutter/dart-async/Future-class.html)<[String](https://api.flutter.dev/flutter/dart-core/String-class.html)>

**Example:**

```dart {class="line-numbers linkable-line-numbers"}
_viam = await Viam.withApiKey(
     dotenv.env['API_KEY_ID'] ?? '',
     dotenv.env['API_KEY'] ?? ''
 );

 try {
   // Define tabular data
   final List<Map<String, dynamic>> tabularData;
   tabularData = [{
     "altitude_m": 50.2,
     "coordinate": {
       "latitude": 40.5,
       "longitude": -72.98
     },
   }];

  // Define date request times
  final List<(DateTime, DateTime)> timeSpan = [(DateTime(2025, 1, 23, 11), DateTime(2025, 1, 23, 11, 0, 3))];

  // Upload captured tabular data
  final fileId = await dataClient.tabularDataCaptureUpload(
    tabularData,
    "<YOUR-PART-ID>",
    componentType: "rdk:component:movement_sensor",
    componentName: "movement_sensor-1",
    methodName: "Position",
    dataRequestTimes: timeSpan,
    tags: ["tag_1", "tag_2"]
  );
   print('Successfully uploaded captured tabular data: $fileId');
 } catch (e) {
   print('Error uploading captured tabular data: $e');
 }
```

For more information, see the [Flutter SDK Docs](https://flutter.viam.dev/viam_sdk/DataClient/tabularDataCaptureUpload.html).

{{% /tab %}}
{{< /tabs >}}

### FileUpload

Upload arbitrary files stored on your machine to Viam by file name.
If uploaded with a file extension of <file>.jpeg/.jpg/.png</file>, uploaded files can be found in the **Images** subtab of the app's [**Data** tab](https://app.viam.com/data).
If <file>.pcd</file>, the uploaded files can be found in the **Point clouds** subtab.
All other types of uploaded files can be found under the **Files** subtab of the app's [**Data** tab](https://app.viam.com/data).

{{< tabs >}}
{{% tab name="Python" %}}

**Parameters:**

- `part_id` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (required): Part ID of the resource associated with the file.
- `data` ([bytes](https://docs.python.org/3/library/stdtypes.html#bytes-objects)) (required): Bytes representing file data to upload.
- `component_type` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (optional): Optional type of the component associated with the file (for example, “movement_sensor”).
- `component_name` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (optional): Optional name of the component associated with the file.
- `method_name` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (optional): Optional name of the method associated with the file.
- `file_name` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (optional): Optional name of the file. The empty string "" will be assigned as the file name if one isn’t provided.
- `method_parameters` (Mapping[[str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str), Any]) (optional): Optional dictionary of the method parameters. No longer in active use.
- `file_extension` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (optional): Optional file extension. The empty string "" will be assigned as the file extension if one isn’t provided. Files with a .jpeg, .jpg, or .png extension will be saved to the Images tab.
- `tags` (List[[str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)]) (optional): Optional list of tags to allow for tag-based filtering when retrieving data.
- `dataset_ids` (List[[str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)]) (optional): Optional list of datasets to add the data to.
- `mime_type` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (optional): Optional mime type of the data.

**Returns:**

- ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)): :   Binary data ID of the new file.

**Raises:**

- (GRPCError): If an invalid part ID is passed.

**Example:**

```python {class="line-numbers linkable-line-numbers"}
file_id = await data_client.file_upload(
    data=b"Encoded image bytes",
    part_id="INSERT YOUR PART ID",
    tags=["tag_1", "tag_2"],
    file_name="your-file",
    file_extension=".txt",
    dataset_ids=["dataset_1", "dataset_2"]
)
```

For more information, see the [Python SDK Docs](https://python.viam.dev/autoapi/viam/app/data_client/index.html#viam.app.data_client.DataClient.file_upload).

{{% /tab %}}
{{% tab name="Flutter" %}}

**Parameters:**

- `path` [String](https://api.flutter.dev/flutter/dart-core/String-class.html) (required)
- `partId` [String](https://api.flutter.dev/flutter/dart-core/String-class.html) (required)
- `fileName` [String](https://api.flutter.dev/flutter/dart-core/String-class.html)? (optional)
- `componentType` [String](https://api.flutter.dev/flutter/dart-core/String-class.html)? (optional)
- `componentName` [String](https://api.flutter.dev/flutter/dart-core/String-class.html)? (optional)
- `methodName` [String](https://api.flutter.dev/flutter/dart-core/String-class.html)? (optional)
- `methodParameters` [Map](https://api.flutter.dev/flutter/dart-core/Map-class.html)<[String](https://api.flutter.dev/flutter/dart-core/String-class.html), Any>? (optional)
- `datasetIds` [Iterable](https://api.flutter.dev/flutter/dart-core/Iterable-class.html)<[String](https://api.flutter.dev/flutter/dart-core/String-class.html)> (optional)
- `tags` [Iterable](https://api.flutter.dev/flutter/dart-core/Iterable-class.html)<[String](https://api.flutter.dev/flutter/dart-core/String-class.html)> (optional)

**Returns:**

- [Future](https://api.flutter.dev/flutter/dart-async/Future-class.html)<[String](https://api.flutter.dev/flutter/dart-core/String-class.html)>

**Example:**

```dart {class="line-numbers linkable-line-numbers"}
import 'package:file_picker/file_picker.dart';
import 'package:cross_file/cross_file.dart';

_viam = await Viam.withApiKey(
     dotenv.env['API_KEY_ID'] ?? '',
     dotenv.env['API_KEY'] ?? ''
);
final dataClient = _viam.dataClient;

// File picker function
Future<XFile?> pickTextFile() async {
  FilePickerResult? result = await FilePicker.platform.pickFiles(
    type: FileType.custom,
    allowedExtensions: ['txt', 'md', 'json', 'csv'],  // Add any other text file extensions you want to support
  );
 if (result != null) {
   return XFile(result.files.single.path!);
 }
   return null;
 }

// Upload text file function. Call this in onPressed in a button in your application.
Future<void> uploadTextFile() async {
  final file = await pickTextFile();
  if (file == null) return;

  try {
    // Get file name
    final fileName = file.name;

    // Upload the file
    final result = await _viam.dataClient.uploadFile(
      file.path,
      fileName: fileName,
      "<YOUR-PART-ID>",
      tags: ["text_file", "document"],
      datasetIds: ["datasetId"]
    );
    print('Upload success: $result');
  } catch (e) {
    print('Upload error: $e');
  }
 }
```

For more information, see the [Flutter SDK Docs](https://flutter.viam.dev/viam_sdk/DataClient/uploadFile.html).

{{% /tab %}}
{{< /tabs >}}

### FileUploadFromPath

Upload files stored on your machine to [Viam](https://app.viam.com) by filepath.
Uploaded files can be found under the **Files** subtab of the [**Data** tab](https://app.viam.com/data).
{{< tabs >}}
{{% tab name="Python" %}}

**Parameters:**

- `filepath` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (required): Absolute filepath of file to be uploaded.
- `part_id` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (required): Part ID of the component associated with the file.
- `component_type` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (optional): Optional type of the component associated with the file (for example, “movement_sensor”).
- `component_name` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (optional): Optional name of the component associated with the file.
- `method_name` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (optional): Optional name of the method associated with the file.
- `method_parameters` (Mapping[[str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str), Any]) (optional): Optional dictionary of the method parameters. No longer in active use.
- `tags` (List[[str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)]) (optional): Optional list of tags to allow for tag-based filtering when retrieving data.
- `dataset_ids` (List[[str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)]) (optional): Optional list of datasets to add the data to.
- `mime_type` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (optional): Optional mime type of the data.
- `file_name` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (optional): Optional name of the file. If not provided, the name will be derived from the filepath.

**Returns:**

- ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)): :   Binary data ID of the new file.

**Raises:**

- (GRPCError): If an invalid part ID is passed.
- (FileNotFoundError): If the provided filepath is not found.

**Example:**

```python {class="line-numbers linkable-line-numbers"}
file_id = await data_client.file_upload_from_path(
    part_id="INSERT YOUR PART ID",
    tags=["tag_1", "tag_2"],
    dataset_ids=["dataset_1", "dataset_2"],
    filepath="/Users/<your-username>/<your-directory>/<your-file.txt>"
)
```

For more information, see the [Python SDK Docs](https://python.viam.dev/autoapi/viam/app/data_client/index.html#viam.app.data_client.DataClient.file_upload_from_path).

{{% /tab %}}
{{< /tabs >}}

### StreamingDataCaptureUpload

Upload the contents of streaming binary data and the relevant metadata to [Viam](https://app.viam.com).
Uploaded streaming data can be found under the [**Data** tab](https://app.viam.com/data).

{{< tabs >}}
{{% tab name="Python" %}}

**Parameters:**

- `data` ([bytes](https://docs.python.org/3/library/stdtypes.html#bytes-objects)) (required): The data to be uploaded.
- `part_id` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (required): Part ID of the resource associated with the file.
- `file_ext` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (required): File extension type for the data. required for determining MIME type.
- `component_type` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (optional): Optional type of the component associated with the file (for example, “movement_sensor”).
- `component_name` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (optional): Optional name of the component associated with the file.
- `method_name` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (optional): Optional name of the method associated with the file.
- `method_parameters` (Mapping[[str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str), Any]) (optional): Optional dictionary of the method parameters. No longer in active use.
- `data_request_times` (Tuple[[datetime.datetime](https://docs.python.org/3/library/datetime.html), [datetime.datetime](https://docs.python.org/3/library/datetime.html)]) (optional): Optional tuple containing datetime objects denoting the times this data was requested [0] by the robot and received [1] from the appropriate sensor.
- `tags` (List[[str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)]) (optional): Optional list of tags to allow for tag-based filtering when retrieving data.
- `dataset_ids` (List[[str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)]) (optional): Optional list of datasets to add the data to.
- `mime_type` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (optional): Optional mime type of the data.

**Returns:**

- ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)): :   The binary data ID of the uploaded data.

**Raises:**

- (GRPCError): If an invalid part ID is passed.

**Example:**

```python {class="line-numbers linkable-line-numbers"}
time_requested = datetime(2023, 6, 5, 11)
time_received = datetime(2023, 6, 5, 11, 0, 3)

file_id = await data_client.streaming_data_capture_upload(
    data="byte-data-to-upload",
    part_id="INSERT YOUR PART ID",
    file_ext="png",
    component_type='motor',
    component_name='left_motor',
    method_name='IsPowered',
    data_request_times=[time_requested, time_received],
    tags=["tag_1", "tag_2"],
    dataset_ids=["dataset_1", "dataset_2"]
)
```

For more information, see the [Python SDK Docs](https://python.viam.dev/autoapi/viam/app/data_client/index.html#viam.app.data_client.DataClient.streaming_data_capture_upload).

{{% /tab %}}
{{% tab name="Flutter" %}}

**Parameters:**

- `bytes` [List](https://api.flutter.dev/flutter/dart-core/List-class.html)<[int](https://api.flutter.dev/flutter/dart-core/int-class.html)> (required)
- `partId` [String](https://api.flutter.dev/flutter/dart-core/String-class.html) (required)
- `fileExtension` [String](https://api.flutter.dev/flutter/dart-core/String-class.html) (required)
- `componentType` [String](https://api.flutter.dev/flutter/dart-core/String-class.html)? (optional)
- `componentName` [String](https://api.flutter.dev/flutter/dart-core/String-class.html)? (optional)
- `methodName` [String](https://api.flutter.dev/flutter/dart-core/String-class.html)? (optional)
- `methodParameters` [Map](https://api.flutter.dev/flutter/dart-core/Map-class.html)<[String](https://api.flutter.dev/flutter/dart-core/String-class.html), Any>? (optional)
- `dataRequestTimes` ([DateTime](https://api.flutter.dev/flutter/dart-core/DateTime-class.html), [DateTime](https://api.flutter.dev/flutter/dart-core/DateTime-class.html))? (optional)
- `datasetIds` [Iterable](https://api.flutter.dev/flutter/dart-core/Iterable-class.html)<[String](https://api.flutter.dev/flutter/dart-core/String-class.html)> (optional)
- `tags` [Iterable](https://api.flutter.dev/flutter/dart-core/Iterable-class.html)<[String](https://api.flutter.dev/flutter/dart-core/String-class.html)> (optional)

**Returns:**

- [Future](https://api.flutter.dev/flutter/dart-async/Future-class.html)<[String](https://api.flutter.dev/flutter/dart-core/String-class.html)>

**Example:**

```dart {class="line-numbers linkable-line-numbers"}
import 'package:file_picker/file_picker.dart';
import 'dart:typed_data';

Future<Uint8List> pickVideoAsBytes() async {
  try {
    // Open file picker
    FilePickerResult? result = await FilePicker.platform.pickFiles(
      type: FileType.video,
      allowMultiple: false,
    );

    if (result == null || result.files.isEmpty) {
      throw Exception('No file selected');
    }

    // For mobile, we get the file path and read it
    final String? filePath = result.files.first.path;
    if (filePath == null) {
      throw Exception('Invalid file path');
    }

    // Read the file as bytes
    final File file = File(filePath);
    final Uint8List bytes = await file.readAsBytes();

    if (bytes.isEmpty) {
      throw Exception('File is empty');
    }

    print('Successfully read file: ${bytes.length} bytes');

    return bytes;
  } catch (e, stackTrace) {
    print('Error picking video: $e');
    print('Stack trace: $stackTrace');
    rethrow;
  }
}

void _uploadData() async {
  _viam = await Viam.withApiKey(
       dotenv.env['API_KEY_ID'] ?? '',
       dotenv.env['API_KEY'] ?? ''
   );
   final dataClient = _viam.dataClient;

   try {
     Uint8List video = await pickVideoAsBytes();

     (DateTime, DateTime) dataRequestTimes = (
       DateTime(2025, 1, 15, 10, 30), // Start time
       DateTime(2025, 1, 15, 14, 45)  // End time
     );

     final binaryDataId = await dataClient.streamingDataCaptureUpload(
       video,
       "<YOUR-PART-ID>",
       ".mp4", // Replace with your desired file format
       componentType: "rdk:component:camera",
       componentName: "camera-1",
       dataRequestTimes: dataRequestTimes);

     print('Successfully uploaded streaming binary data with binaryDataId: $binaryDataId');
   } catch (e) {
     print('Error uploading streaming binary data: $e');
   }
}
```

For more information, see the [Flutter SDK Docs](https://flutter.viam.dev/viam_sdk/DataClient/streamingDataCaptureUpload.html).

{{% /tab %}}
{{< /tabs >}}


### GetLatestTabularData

Gets the most recent tabular data captured from the specified data source, as long as it was synced within the last year.

{{< tabs >}}
{{% tab name="Python" %}}

**Parameters:**

- `part_id` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (required): The ID of the part that owns the data.
- `resource_name` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (required): The name of the requested resource that captured the data. For example, “my-sensor”.
- `resource_api` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (required): The API of the requested resource that captured the data. For example, “rdk:component:sensor”.
- `method_name` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (required): The data capture method name. For exampe, “Readings”.
- `additional_params` (Mapping[[str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str), viam.utils.ValueTypes]) (optional): Optional additional parameters of the resource that captured the data.

**Returns:**

- (Tuple[[datetime.datetime](https://docs.python.org/3/library/datetime.html), [datetime.datetime](https://docs.python.org/3/library/datetime.html), Dict[[str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str), viam.utils.ValueTypes]] | None): :   A return value of `None` means that this data source
    has not synced data in the last year. Otherwise, the data source has synced some data in the last year, so the returned
    tuple contains the following:
        * `time_captured` (*datetime*): The time captured.
        * `time_synced` (*datetime*): The time synced.
        * `payload` (*Dict[str, ValueTypes]*): The latest tabular data captured from the specified data source.

**Example:**

```python {class="line-numbers linkable-line-numbers"}
tabular_data = await data_client.get_latest_tabular_data(
    part_id="77ae3145-7b91-123a-a234-e567cdca8910",
    resource_name="camera-1",
    resource_api="rdk:component:camera",
    method_name="GetImages",
    additional_params={"docommand_input": {"test": "test"}}
)

if tabular_data:
    time_captured, time_synced, payload = tabular_data
    print(f"Time Captured: {time_captured}")
    print(f"Time Synced: {time_synced}")
    print(f"Payload: {payload}")
else:
    print(f"No data returned: {tabular_data}")
```

For more information, see the [Python SDK Docs](https://python.viam.dev/autoapi/viam/app/data_client/index.html#viam.app.data_client.DataClient.get_latest_tabular_data).

{{% /tab %}}
{{% tab name="Go" %}}

**Parameters:**

- `ctx` [(Context)](https://pkg.go.dev/context#Context): A Context carries a deadline, a cancellation signal, and other values across API boundaries.
- `partID`
- `resourceName`
- `resourceSubtype`
- `methodName` [(string)](https://pkg.go.dev/builtin#string)
- `opts` [(*TabularDataOptions)](https://pkg.go.dev/go.viam.com/rdk/app#TabularDataOptions)

**Returns:**

- [(*GetLatestTabularDataResponse)](https://pkg.go.dev/go.viam.com/rdk/app#GetLatestTabularDataResponse)
- [(error)](https://pkg.go.dev/builtin#error): An error, if one occurred.

For more information, see the [Go SDK Docs](https://pkg.go.dev/go.viam.com/rdk/app#DataClient.GetLatestTabularData).

{{% /tab %}}
{{% tab name="TypeScript" %}}

**Parameters:**

- `partId` (string) (required): The ID of the part that owns the data.
- `resourceName` (string) (required): The name of the requested resource that captured the data. Ex: "my-sensor".
- `resourceSubtype` (string) (required): The subtype of the requested resource that captured the data. Ex:
  "rdk:component:sensor".
- `methodName` (string) (required): The data capture method name. Ex: "Readings".
- `additionalParams` (Record) (optional)

**Returns:**

- (Promise<[Date, Date, Record<string, [JsonValue](https://ts.viam.dev/types/JsonValue.html)>] | null>): A tuple containing [timeCaptured, timeSynced, payload] or null if no data has been
synced for the specified resource OR the most recently captured data was over a year ago.

**Example:**

```ts {class="line-numbers linkable-line-numbers"}
const data = await dataClient.getLatestTabularData(
  '123abc45-1234-5678-90ab-cdef12345678',
  'my-sensor',
  'rdk:component:sensor',
  'Readings',
);
```

For more information, see the [TypeScript SDK Docs](https://ts.viam.dev/interfaces/DataClient.html#getlatesttabulardata).

{{% /tab %}}
{{% tab name="Flutter" %}}

**Parameters:**

- `partId` [String](https://api.flutter.dev/flutter/dart-core/String-class.html) (required)
- `resourceName` [String](https://api.flutter.dev/flutter/dart-core/String-class.html) (required)
- `resourceSubtype` [String](https://api.flutter.dev/flutter/dart-core/String-class.html) (required)
- `methodName` [String](https://api.flutter.dev/flutter/dart-core/String-class.html) (required)
- `additionalParams` [Map](https://api.flutter.dev/flutter/dart-core/Map-class.html)<[String](https://api.flutter.dev/flutter/dart-core/String-class.html), dynamic>? (required)

**Returns:**

- [Future](https://api.flutter.dev/flutter/dart-async/Future-class.html)<({[Map](https://api.flutter.dev/flutter/dart-core/Map-class.html)<[String](https://api.flutter.dev/flutter/dart-core/String-class.html), dynamic> payload, [DateTime](https://api.flutter.dev/flutter/dart-core/DateTime-class.html) timeCaptured, [DateTime](https://api.flutter.dev/flutter/dart-core/DateTime-class.html) timeSynced})?>

**Example:**

```dart {class="line-numbers linkable-line-numbers"}
_viam = await Viam.withApiKey(
     dotenv.env['API_KEY_ID'] ?? '',
     dotenv.env['API_KEY'] ?? ''
 );
 final dataClient = _viam.dataClient;

 try {
   // Get latest tabular data
   final response = await dataClient.getLatestTabularData(
     "<YOUR-PART-ID>",
     "movement_sensor-1",
     "rdk:component:movement_sensor",
     "Position"
   );
   print('Successfully retrieved latest tabular data: $response');
 } catch (e) {
   print('Error retrieving latest tabular data: $e');
 }
```

For more information, see the [Flutter SDK Docs](https://flutter.viam.dev/viam_sdk/DataClient/getLatestTabularData.html).

{{% /tab %}}
{{< /tabs >}}

### ExportTabularData

Obtain unified tabular data and metadata from the specified data source.

{{< tabs >}}
{{% tab name="Python" %}}

**Parameters:**

- `part_id` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (required): The ID of the part that owns the data.
- `resource_name` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (required): The name of the requested resource that captured the data.
- `resource_api` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (required): The API of the requested resource that captured the data.
- `method_name` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (required): The data capture method name.
- `start_time` ([datetime.datetime](https://docs.python.org/3/library/datetime.html)) (optional): Optional start time for requesting a specific range of data.
- `end_time` ([datetime.datetime](https://docs.python.org/3/library/datetime.html)) (optional): Optional end time for requesting a specific range of data.
- `additional_params` (Mapping[[str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str), viam.utils.ValueTypes]) (optional): Optional additional parameters of the resource that captured the data.

**Returns:**

- ([List[TabularDataPoint]](https://python.viam.dev/autoapi/viam/app/data_client/index.html#viam.app.data_client.DataClient.TabularDataPoint)): :   The unified tabular data and metadata.

**Example:**

```python {class="line-numbers linkable-line-numbers"}
tabular_data = await data_client.export_tabular_data(
    part_id="<PART-ID>",
    resource_name="<RESOURCE-NAME>",
    resource_api="<RESOURCE-API>",
    method_name="<METHOD-NAME>",
    start_time="<START_TIME>"
    end_time="<END_TIME>"
    additional_params="<ADDITIONAL_PARAMETERS>"
)

print(f"My data: {tabular_data}")
```

For more information, see the [Python SDK Docs](https://python.viam.dev/autoapi/viam/app/data_client/index.html#viam.app.data_client.DataClient.export_tabular_data).

{{% /tab %}}
{{% tab name="Go" %}}

**Parameters:**

- `ctx` [(Context)](https://pkg.go.dev/context#Context): A Context carries a deadline, a cancellation signal, and other values across API boundaries.
- `partID`
- `resourceName`
- `resourceSubtype`
- `method` [(string)](https://pkg.go.dev/builtin#string)
- `interval` [(CaptureInterval)](https://pkg.go.dev/go.viam.com/rdk/app#CaptureInterval)
- `opts` [(*TabularDataOptions)](https://pkg.go.dev/go.viam.com/rdk/app#TabularDataOptions)

**Returns:**

- [([]*ExportTabularDataResponse)](https://pkg.go.dev/go.viam.com/rdk/app#ExportTabularDataResponse)
- [(error)](https://pkg.go.dev/builtin#error): An error, if one occurred.

For more information, see the [Go SDK Docs](https://pkg.go.dev/go.viam.com/rdk/app#DataClient.ExportTabularData).

{{% /tab %}}
{{% tab name="TypeScript" %}}

**Parameters:**

- `partId` (string) (required): The ID of the part that owns the data.
- `resourceName` (string) (required): The name of the requested resource that captured the data.
- `resourceSubtype` (string) (required): The subtype of the requested resource that captured the data.
- `methodName` (string) (required): The data capture method name.
- `startTime` (Date) (optional): Optional start time (`Date` object) for requesting a specific range of data.
- `endTime` (Date) (optional): Optional end time (`Date` object) for requesting a specific range of data.
- `additionalParams` (Record) (optional)

**Returns:**

- (Promise<TabularDataPoint[]>): An array of unified tabular data and metadata.

**Example:**

```ts {class="line-numbers linkable-line-numbers"}
const data = await dataClient.exportTabularData(
  '123abc45-1234-5678-90ab-cdef12345678',
  'my-sensor',
  'rdk:component:sensor',
  'Readings',
  new Date('2025-03-25'),
  new Date('2024-03-27'),
);
```

For more information, see the [TypeScript SDK Docs](https://ts.viam.dev/interfaces/DataClient.html#exporttabulardata).

{{% /tab %}}
{{% tab name="Flutter" %}}

**Parameters:**

- `partId` [String](https://api.flutter.dev/flutter/dart-core/String-class.html) (required)
- `resourceName` [String](https://api.flutter.dev/flutter/dart-core/String-class.html) (required)
- `resourceSubtype` [String](https://api.flutter.dev/flutter/dart-core/String-class.html) (required)
- `methodName` [String](https://api.flutter.dev/flutter/dart-core/String-class.html) (required)
- `startTime` [DateTime](https://api.flutter.dev/flutter/dart-core/DateTime-class.html)? (required)
- `endTime` [DateTime](https://api.flutter.dev/flutter/dart-core/DateTime-class.html)? (required)
- `additionalParams` [Map](https://api.flutter.dev/flutter/dart-core/Map-class.html)<[String](https://api.flutter.dev/flutter/dart-core/String-class.html), dynamic>? (required)

**Returns:**

- [Future](https://api.flutter.dev/flutter/dart-async/Future-class.html)<[List](https://api.flutter.dev/flutter/dart-core/List-class.html)<[TabularDataPoint](https://flutter.viam.dev/viam_sdk/TabularDataPoint-class.html)>\>

**Example:**

```dart {class="line-numbers linkable-line-numbers"}
 _viam = await Viam.withApiKey(
     dotenv.env['API_KEY_ID'] ?? '',
     dotenv.env['API_KEY'] ?? ''
 );
 final dataClient = _viam.dataClient;

 try {
  // Define date request times
  final startTime = DateTime(2025, 1, 23, 11);
  final endTime = DateTime(2025, 1, 23, 11, 0, 3);

  final tabularData = await dataClient.exportTabularData(
    "<YOUR-PART-ID>",
    "movement_sensor-1",
    "rdk:component:movement_sensor",
    "Position",
    startTime,
    endTime
  );

  for (var dataPoint in tabularData) {
    print(dataPoint.partId);
    print(dataPoint.resourceName);
    print(dataPoint.methodName);
    print(dataPoint.payload);
  }

  print('Successfully exported tabular data');
 } catch (e) {
  print('Error exporting tabular data: $e');
 }
```

For more information, see the [Flutter SDK Docs](https://flutter.viam.dev/viam_sdk/DataClient/exportTabularData.html).

{{% /tab %}}
{{< /tabs >}}

### TabularDataByFilter

Retrieve optionally filtered tabular data from [Viam](https://app.viam.com).
You can also find your tabular data under the **Sensors** subtab of the [**Data** tab](https://app.viam.com/data).
{{< tabs >}}
{{% tab name="Python" %}}

**Parameters:**

- `filter` ([viam.proto.app.data.Filter](https://python.viam.dev/autoapi/viam/proto/app/data/index.html#viam.proto.app.data.Filter)) (optional): Optional, specifies tabular data to retrieve. If missing, matches all tabular data.
- `limit` ([int](https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex)) (optional): The maximum number of entries to include in a page. Defaults to 50 if unspecified.
- `sort_order` ([viam.proto.app.data.Order.ValueType](https://python.viam.dev/autoapi/viam/proto/app/data/index.html#viam.proto.app.data.Order)) (optional): The desired sort order of the data.
- `last` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (optional): Optional string indicating the object identifier of the last-returned data. This object identifier is returned by calls to `TabularDataByFilter` as the last value. If provided, the server will return the next data entries after the last object identifier.
- `count_only` ([bool](https://docs.python.org/3/library/stdtypes.html#boolean-type-bool)) (required): Whether to return only the total count of entries.
- `include_internal_data` ([bool](https://docs.python.org/3/library/stdtypes.html#boolean-type-bool)) (required): Whether to return the internal data. Internal data is used for Viam-specific data ingestion, like cloud SLAM. Defaults to False.
- `dest` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (optional): Optional filepath for writing retrieved data.

**Returns:**

- (Tuple[List[TabularData], [int](https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex), [str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)]): :   A tuple containing the following:
        * `tabular_data` (*List[TabularData]*): The tabular data.
        * `count` (*int*): The count (number of entries).
        * `last` (*str*): The last-returned page ID.

**Example:**

```python {class="line-numbers linkable-line-numbers"}
from viam.utils import create_filter

my_data = []
my_filter = create_filter(component_name="motor-1")
last = None
while True:
    tabular_data, count, last = await data_client.tabular_data_by_filter(my_filter, last=last)
    if not tabular_data:
        break
    my_data.extend(tabular_data)

print(f"My data: {my_data}")
```

For more information, see the [Python SDK Docs](https://python.viam.dev/autoapi/viam/app/data_client/index.html#viam.app.data_client.DataClient.tabular_data_by_filter).

{{% /tab %}}
{{% tab name="Go" %}}

**Parameters:**

- `ctx` [(Context)](https://pkg.go.dev/context#Context): A Context carries a deadline, a cancellation signal, and other values across API boundaries.
- `opts` [(*DataByFilterOptions)](https://pkg.go.dev/go.viam.com/rdk/app#DataByFilterOptions)

**Returns:**

- [(*TabularDataByFilterResponse)](https://pkg.go.dev/go.viam.com/rdk/app#TabularDataByFilterResponse)
- [(error)](https://pkg.go.dev/builtin#error): An error, if one occurred.

For more information, see the [Go SDK Docs](https://pkg.go.dev/go.viam.com/rdk/app#DataClient.TabularDataByFilter).

{{% /tab %}}
{{% tab name="TypeScript" %}}

**Parameters:**

- `filter` ([Filter](https://ts.viam.dev/classes/dataApi.Filter.html)) (optional): Optional `pb.Filter` specifying tabular data to retrieve. No `filter` implies all
  tabular data.
- `limit` (number) (optional): The maximum number of entries to include in a page. Defaults to 50 if unspecfied.
- `sortOrder` ([Order](https://ts.viam.dev/enums/dataApi.Order.html)) (optional): The desired sort order of the data.
- `last` (string) (optional): Optional string indicating the ID of the last-returned data. If provided, the
  server will return the next data entries after the `last` ID.
- `countOnly` (boolean) (optional): Whether to return only the total count of entries.
- `includeInternalData` (boolean) (optional): Whether to retun internal data. Internal data is used for
  Viam-specific data ingestion, like cloud SLAM. Defaults to `false`.

**Returns:**

- (Promise<{ count: bigint; data: TabularData[]; last: string }>): An array of data objects, the count (number of entries), and the last-returned page
ID.

**Example:**

```ts {class="line-numbers linkable-line-numbers"}
const data = await dataClient.tabularDataByFilter(
  {
    componentName: 'sensor-1',
    componentType: 'rdk:component:sensor',
  } as Filter,
  5,
);
```

For more information, see the [TypeScript SDK Docs](https://ts.viam.dev/interfaces/DataClient.html#tabulardatabyfilter).

{{% /tab %}}
{{% tab name="Flutter" %}}

**Parameters:**

- `filter` [Filter](https://flutter.viam.dev/viam_protos.app.data/Filter-class.html)? (optional)
- `limit` [int](https://api.flutter.dev/flutter/dart-core/int-class.html)? (optional)
- `sortOrder` [Order](https://flutter.viam.dev/viam_protos.app.data/Order-class.html)? (optional)
- `last` [String](https://api.flutter.dev/flutter/dart-core/String-class.html)? (optional)
- `countOnly` dynamic (optional)

**Returns:**

- [Future](https://api.flutter.dev/flutter/dart-async/Future-class.html)<[TabularDataByFilterResponse](https://flutter.viam.dev/viam_protos.app.data/TabularDataByFilterResponse-class.html)>

**Example:**

```dart {class="line-numbers linkable-line-numbers"}
_viam = await Viam.withApiKey(
    dotenv.env['API_KEY_ID'] ?? '',
    dotenv.env['API_KEY'] ?? ''
);
final dataClient = _viam.dataClient;

try {
 // Create a filter to target specific tabular data
 final filter = Filter(
  componentName: "arm-1",
 );

 final response = await dataClient.tabularDataByFilter(
   filter: filter,
   limit: 10
 );
 print('Number of items: ${response.count.toInt()}');
 print('Total size: ${response.totalSizeBytes.toInt()}');
 for (var metadata in response.metadata) {
   print(metadata);
 }
 for (var data in response.data) {
   print(data);
 }

 print('Successfully retrieved tabular data by filter');
} catch (e) {
 print('Error retrieving tabular data by filter: $e');
}
```

For more information, see the [Flutter SDK Docs](https://flutter.viam.dev/viam_sdk/DataClient/tabularDataByFilter.html).

{{% /tab %}}
{{< /tabs >}}

### TabularDataBySQL

Obtain unified tabular data and metadata, queried with SQL. Make sure your API key has permissions at the organization level in order to use this.

{{< tabs >}}
{{% tab name="Python" %}}

**Parameters:**

- `organization_id` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (required): The ID of the organization that owns the data. To find your organization ID, visit the organization settings page.
- `sql_query` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (required): The SQL query to run.

**Returns:**

- (List[Dict[[str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str), viam.utils.ValueTypes | [datetime.datetime](https://docs.python.org/3/library/datetime.html)]]): :   An array of decoded BSON data objects.

**Example:**

```python {class="line-numbers linkable-line-numbers"}
data = await data_client.tabular_data_by_sql(
    organization_id="<YOUR-ORG-ID>",
    sql_query="SELECT * FROM readings LIMIT 5"
)
```

For more information, see the [Python SDK Docs](https://python.viam.dev/autoapi/viam/app/data_client/index.html#viam.app.data_client.DataClient.tabular_data_by_sql).

{{% /tab %}}
{{% tab name="Go" %}}

**Parameters:**

- `ctx` [(Context)](https://pkg.go.dev/context#Context): A Context carries a deadline, a cancellation signal, and other values across API boundaries.
- `organizationID`
- `sqlQuery` [(string)](https://pkg.go.dev/builtin#string)

**Returns:**

- [([]map[string]any)](https://pkg.go.dev/builtin#any)
- [(error)](https://pkg.go.dev/builtin#error): An error, if one occurred.

For more information, see the [Go SDK Docs](https://pkg.go.dev/go.viam.com/rdk/app#DataClient.TabularDataBySQL).

{{% /tab %}}
{{% tab name="TypeScript" %}}

**Parameters:**

- `organizationId` (string) (required): The ID of the organization that owns the data.
- `query` (string) (required): The SQL query to run.

**Returns:**

- (Promise<(Object | any[])[]>): An array of data objects.

**Example:**

```ts {class="line-numbers linkable-line-numbers"}
const data = await dataClient.tabularDataBySQL(
  '123abc45-1234-5678-90ab-cdef12345678',
  'SELECT * FROM readings LIMIT 5',
);
```

For more information, see the [TypeScript SDK Docs](https://ts.viam.dev/interfaces/DataClient.html#tabulardatabysql).

{{% /tab %}}
{{% tab name="Flutter" %}}

**Parameters:**

- `organizationId` [String](https://api.flutter.dev/flutter/dart-core/String-class.html) (required)
- `query` [String](https://api.flutter.dev/flutter/dart-core/String-class.html) (required)

**Returns:**

- [Future](https://api.flutter.dev/flutter/dart-async/Future-class.html)<[List](https://api.flutter.dev/flutter/dart-core/List-class.html)<[Map](https://api.flutter.dev/flutter/dart-core/Map-class.html)<[String](https://api.flutter.dev/flutter/dart-core/String-class.html), dynamic>\>>

**Example:**

```dart {class="line-numbers linkable-line-numbers"}
// List<Map<String, dynamic>>? _responseData;

 _viam = await Viam.withApiKey(
     dotenv.env['API_KEY_ID'] ?? '',
     dotenv.env['API_KEY'] ?? ''
 );
 final dataClient = _viam.dataClient;

 // Example SQL query
 final sqlQuery = "SELECT * FROM readings LIMIT 5";

 _responseData = await dataClient.tabularDataBySql(
   "<YOUR-ORG-ID>",
   sqlQuery
 );
```

For more information, see the [Flutter SDK Docs](https://flutter.viam.dev/viam_sdk/DataClient/tabularDataBySql.html).

{{% /tab %}}
{{< /tabs >}}

### TabularDataByMQL

Obtain unified tabular data and metadata, queried with MQL.

{{< tabs >}}
{{% tab name="Python" %}}

**Parameters:**

- `organization_id` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (required): The ID of the organization that owns the data. To find your organization ID, visit the organization settings page.
- `query` (List[[bytes](https://docs.python.org/3/library/stdtypes.html#bytes-objects)] | List[Dict[[str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str), Any]]) (required): The MQL query to run, as a list of MongoDB aggregation pipeline stages. Each stage can be provided as either a dictionary or raw BSON bytes, but support for bytes will be removed in the future, so prefer the dictionary option.
- `use_recent_data` ([bool](https://docs.python.org/3/library/stdtypes.html#boolean-type-bool)) (optional): Whether to query blob storage or your recent data store. Defaults to False.. Deprecated, use tabular_data_source_type instead.
- `tabular_data_source_type` ([viam.proto.app.data.TabularDataSourceType.ValueType](https://python.viam.dev/autoapi/viam/proto/app/data/index.html#viam.proto.app.data.TabularDataSourceType)) (required): The data source to query. Defaults to TABULAR_DATA_SOURCE_TYPE_STANDARD.
- `pipeline_id` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (optional): The ID of the data pipeline to query. Defaults to None. Required if tabular_data_source_type is TABULAR_DATA_SOURCE_TYPE_PIPELINE_SINK.
- `query_prefix_name` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (optional): Optional field that can be used to specify a saved query to run.

**Returns:**

- (List[Dict[[str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str), viam.utils.ValueTypes | [datetime.datetime](https://docs.python.org/3/library/datetime.html)]]): :   An array of decoded BSON data objects.

**Example:**

```python {class="line-numbers linkable-line-numbers"}
import bson

tabular_data = await data_client.tabular_data_by_mql(organization_id="<YOUR-ORG-ID>", query=[
    { '$match': { 'location_id': '<YOUR-LOCATION-ID>' } },
    { "$limit": 5 }
])

print(f"Tabular Data: {tabular_data}")
```

For more information, see the [Python SDK Docs](https://python.viam.dev/autoapi/viam/app/data_client/index.html#viam.app.data_client.DataClient.tabular_data_by_mql).

{{% /tab %}}
{{% tab name="Go" %}}

**Parameters:**

- `ctx` [(Context)](https://pkg.go.dev/context#Context): A Context carries a deadline, a cancellation signal, and other values across API boundaries.
- `organizationID` [(string)](https://pkg.go.dev/builtin#string)
- `query` [([]map[string]any)](https://pkg.go.dev/builtin#any)
- `opts` [(*TabularDataByMQLOptions)](https://pkg.go.dev/go.viam.com/rdk/app#TabularDataByMQLOptions)

**Returns:**

- [([]map[string]any)](https://pkg.go.dev/builtin#any)
- [(error)](https://pkg.go.dev/builtin#error): An error, if one occurred.

For more information, see the [Go SDK Docs](https://pkg.go.dev/go.viam.com/rdk/app#DataClient.TabularDataByMQL).

{{% /tab %}}
{{% tab name="TypeScript" %}}

**Parameters:**

- `organizationId` (string) (required): The ID of the organization that owns the data.
- `query` (Uint8Array) (required): The MQL query to run as a list of BSON documents.
- `useRecentData` (boolean) (optional): Whether to query blob storage or your recent data store. Defaults to
  false. Deprecated - use dataSource instead.
- `tabularDataSource` ([TabularDataSource](https://ts.viam.dev/classes/dataApi.TabularDataSource.html)) (optional)
- `queryPrefixName` (string) (optional): Optional name of the query prefix.

**Returns:**

- (Promise<(Object | any[])[]>): An array of data objects.

**Example:**

```ts {class="line-numbers linkable-line-numbers"}
// {@link JsonValue} is imported from @bufbuild/protobuf
const mqlQuery: Record<string, JsonValue>[] = [
  {
    $match: {
      component_name: 'sensor-1',
    },
  },
  {
    $limit: 5,
  },
];

const data = await dataClient.tabularDataByMQL(
  '123abc45-1234-5678-90ab-cdef12345678',
  mqlQuery,
);
```

For more information, see the [TypeScript SDK Docs](https://ts.viam.dev/interfaces/DataClient.html#tabulardatabymql).

{{% /tab %}}
{{% tab name="Flutter" %}}

**Parameters:**

- `organizationId` [String](https://api.flutter.dev/flutter/dart-core/String-class.html) (required)
- `query` dynamic (required)
- `useRecentData` [bool](https://api.flutter.dev/flutter/dart-core/bool-class.html) (optional)
- `queryPrefixName` [String](https://api.flutter.dev/flutter/dart-core/String-class.html)? (optional)

**Returns:**

- [Future](https://api.flutter.dev/flutter/dart-async/Future-class.html)<[List](https://api.flutter.dev/flutter/dart-core/List-class.html)<[Map](https://api.flutter.dev/flutter/dart-core/Map-class.html)<[String](https://api.flutter.dev/flutter/dart-core/String-class.html), dynamic>\>>

**Example:**

```dart {class="line-numbers linkable-line-numbers"}
// import 'package:bson/bson.dart';

// List<Map<String, dynamic>>? _responseData;

 _viam = await Viam.withApiKey(
     dotenv.env['API_KEY_ID'] ?? '',
     dotenv.env['API_KEY'] ?? ''
 );
 final dataClient = _viam.dataClient;

 final query = BsonCodec.serialize({
  "\$match": {
     "location_id": "<YOUR-LOCATION-ID>",
  }
 });

 final sort = BsonCodec.serialize({
   "\$sort": {"time_requested": -1}
   sqlQuery
 });

 final limit = BsonCodec.serialize({"\$limit": 1});

 final pipeline = [query.byteList, sort.byteList, limit.byteList];
 _responseData = await dataClient.tabularDataByMql(
  "<YOUR-ORG-ID>",
  pipeline
 );
```

For more information, see the [Flutter SDK Docs](https://flutter.viam.dev/viam_sdk/DataClient/tabularDataByMql.html).

{{% /tab %}}
{{< /tabs >}}

### BinaryDataByFilter

Retrieve optionally filtered binary data from [Viam](https://app.viam.com).
You can also find your binary data under the **Images**, **Point clouds**, or **Files** subtab of the [**Data** tab](https://app.viam.com/data), depending on the type of data that you have uploaded.
{{< tabs >}}
{{% tab name="Python" %}}

**Parameters:**

- `filter` ([viam.proto.app.data.Filter](https://python.viam.dev/autoapi/viam/proto/app/data/index.html#viam.proto.app.data.Filter)) (optional): Optional, specifies tabular data to retrieve. An empty filter matches all binary data.
- `limit` ([int](https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex)) (optional): The maximum number of entries to include in a page. Defaults to 50 if unspecified.
- `sort_order` ([viam.proto.app.data.Order.ValueType](https://python.viam.dev/autoapi/viam/proto/app/data/index.html#viam.proto.app.data.Order)) (optional): The desired sort order of the data.
- `last` ([str](https://python.viam.dev/autoapi/viam/app/data_client/index.html#viam.app.data_client.DataClient.binary_data_by_filter)) (optional): Optional string indicating the object identifier of the last-returned data. This object identifier is returned by calls to `BinaryDataByFilter` as the last value. If provided, the server will return the next data entries after the last object identifier.
- `include_binary_data` ([bool](https://docs.python.org/3/library/stdtypes.html#boolean-type-bool)) (required): Boolean specifying whether to actually include the binary file data with each retrieved file. Defaults to true (that is, both the files’ data and metadata are returned).
- `count_only` ([bool](https://docs.python.org/3/library/stdtypes.html#boolean-type-bool)) (required): Whether to return only the total count of entries.
- `include_internal_data` ([bool](https://docs.python.org/3/library/stdtypes.html#boolean-type-bool)) (required): Whether to return the internal data. Internal data is used for Viam-specific data ingestion, like cloud SLAM. Defaults to False.
- `dest` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (optional): Optional filepath for writing retrieved data.

**Returns:**

- (Tuple[List[viam.proto.app.data.BinaryData], [int](https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex), [str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)]): :   A tuple containing the following:
        * `data` (*List[* [`BinaryData`](https://python.viam.dev/autoapi/viam/proto/app/data/index.html#viam.proto.app.data.BinaryData "viam.proto.app.data.BinaryData") *]*): The binary data.
        * `count` (*int*): The count (number of entries).
        * `last` (*str*): The last-returned page ID.

**Example:**

```python {class="line-numbers linkable-line-numbers"}
from viam.utils import create_filter
from viam.proto.app.data import Filter, TagsFilter, TagsFilterType

# Get data captured from camera components
my_data = []
last = None
my_filter = create_filter(component_name="camera-1")

while True:
    data, count, last = await data_client.binary_data_by_filter(
        my_filter, limit=1, last=last)
    if not data:
        break
    my_data.extend(data)

print(f"My data: {my_data}")

# Get untagged data from a dataset

my_untagged_data = []
last = None
tags_filter = TagsFilter(type=TagsFilterType.TAGS_FILTER_TYPE_UNTAGGED)
my_filter = Filter(
    dataset_id="66db6fe7d93d1ade24cd1dc3",
    tags_filter=tags_filter
)

while True:
    data, count, last = await data_client.binary_data_by_filter(
        my_filter, last=last, include_binary_data=False)
    if not data:
        break
    my_untagged_data.extend(data)
```

For more information, see the [Python SDK Docs](https://python.viam.dev/autoapi/viam/app/data_client/index.html#viam.app.data_client.DataClient.binary_data_by_filter).

{{% /tab %}}
{{% tab name="Go" %}}

**Parameters:**

- `ctx` [(Context)](https://pkg.go.dev/context#Context): A Context carries a deadline, a cancellation signal, and other values across API boundaries.
- `includeBinary` [(bool)](https://pkg.go.dev/builtin#bool)
- `opts` [(*DataByFilterOptions)](https://pkg.go.dev/go.viam.com/rdk/app#DataByFilterOptions)

**Returns:**

- [(*BinaryDataByFilterResponse)](https://pkg.go.dev/go.viam.com/rdk/app#BinaryDataByFilterResponse)
- [(error)](https://pkg.go.dev/builtin#error): An error, if one occurred.

For more information, see the [Go SDK Docs](https://pkg.go.dev/go.viam.com/rdk/app#DataClient.BinaryDataByFilter).

{{% /tab %}}
{{% tab name="TypeScript" %}}

**Parameters:**

- `filter` ([Filter](https://ts.viam.dev/classes/dataApi.Filter.html)) (optional): Optional `pb.Filter` specifying binary data to retrieve. No `filter` implies all
  binary data.
- `limit` (number) (optional): The maximum number of entries to include in a page. Defaults to 50 if unspecfied.
- `sortOrder` ([Order](https://ts.viam.dev/enums/dataApi.Order.html)) (optional): The desired sort order of the data.
- `last` (string) (optional): Optional string indicating the ID of the last-returned data. If provided, the
  server will return the next data entries after the `last` ID.
- `includeBinary` (boolean) (optional): Whether to include binary file data with each retrieved file.
- `countOnly` (boolean) (optional): Whether to return only the total count of entries.
- `includeInternalData` (boolean) (optional): Whether to retun internal data. Internal data is used for
  Viam-specific data ingestion, like cloud SLAM. Defaults to `false`.

**Returns:**

- (Promise<{ count: bigint; data: [BinaryData](https://ts.viam.dev/classes/dataApi.BinaryData.html)[]; last: string }>): An array of data objects, the count (number of entries), and the last-returned page
ID.

**Example:**

```ts {class="line-numbers linkable-line-numbers"}
const data = await dataClient.binaryDataByFilter(
  {
    componentName: 'camera-1',
    componentType: 'rdk:component:camera',
  } as Filter,
  1,
);
```

For more information, see the [TypeScript SDK Docs](https://ts.viam.dev/interfaces/DataClient.html#binarydatabyfilter).

{{% /tab %}}
{{% tab name="Flutter" %}}

**Parameters:**

- `filter` [Filter](https://flutter.viam.dev/viam_protos.app.data/Filter-class.html)? (optional)
- `limit` [int](https://api.flutter.dev/flutter/dart-core/int-class.html)? (optional)
- `sortOrder` [Order](https://flutter.viam.dev/viam_protos.app.data/Order-class.html)? (optional)
- `last` [String](https://api.flutter.dev/flutter/dart-core/String-class.html)? (optional)
- `countOnly` [bool](https://api.flutter.dev/flutter/dart-core/bool-class.html) (optional)
- `includeBinary` [bool](https://api.flutter.dev/flutter/dart-core/bool-class.html) (optional)

**Returns:**

- [Future](https://api.flutter.dev/flutter/dart-async/Future-class.html)<[BinaryDataByFilterResponse](https://flutter.viam.dev/viam_protos.app.data/BinaryDataByFilterResponse-class.html)>

**Example:**

```dart {class="line-numbers linkable-line-numbers"}
_viam = await Viam.withApiKey(
    dotenv.env['API_KEY_ID'] ?? '',
    dotenv.env['API_KEY'] ?? ''
);
final dataClient = _viam.dataClient;

try {
 // Create a filter to target specific binary data
 final filter = Filter(
  componentName: "camera-1",
 );

 final response = await dataClient.binaryDataByFilter(filter: filter, limit: 1);

 print('Number of items: ${response.count.toInt()}');
 print('Total size: ${response.totalSizeBytes.toInt()} bytes');
 for (var dataPoint in response.data) {
   print(dataPoint.binary);
   print(dataPoint.metadata);
 }

 print('Successfully retrieved binary data by filter');
} catch (e) {
 print('Error retrieving binary data by filter: $e');
}
```

For more information, see the [Flutter SDK Docs](https://flutter.viam.dev/viam_sdk/DataClient/binaryDataByFilter.html).

{{% /tab %}}
{{< /tabs >}}

### BinaryDataByIDs

Retrieve binary data from Viam by `BinaryID`.
You can also find your binary data under the **Images**, **Point clouds**, or **Files** subtab of the app's [**Data** tab](https://app.viam.com/data), depending on the type of data that you have uploaded.

{{< tabs >}}
{{% tab name="Python" %}}

**Parameters:**

- `binary_ids` ([List[viam.proto.app.data.BinaryID] | List[str]](https://python.viam.dev/autoapi/viam/proto/app/data/index.html#viam.proto.app.data.BinaryID)) (required): Binary data ID strings specifying the desired data or BinaryID objects. Must be non-empty. DEPRECATED: BinaryID is deprecated and will be removed in a future release. Instead, pass binary data IDs as a list of strings.
- `include_binary_data` ([bool](https://docs.python.org/3/library/stdtypes.html#boolean-type-bool)) (required): Boolean specifying whether to actually include the binary file data with each retrieved file. Defaults to true (that is, both the files’ data and metadata are returned).
- `dest` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (optional): Optional filepath for writing retrieved data.

**Returns:**

- ([List[viam.proto.app.data.BinaryData]](https://python.viam.dev/autoapi/viam/proto/app/data/index.html#viam.proto.app.data.BinaryData)): :   The binary data.

**Raises:**

- (GRPCError): If no binary data ID strings or BinaryID objects are provided.

**Example:**

```python {class="line-numbers linkable-line-numbers"}
binary_metadata, count, last = await data_client.binary_data_by_filter(
    include_binary_data=False
)

my_ids = []

for obj in binary_metadata:
    my_ids.append(obj.metadata.binary_data_id)

binary_data = await data_client.binary_data_by_ids(my_ids)
```

For more information, see the [Python SDK Docs](https://python.viam.dev/autoapi/viam/app/data_client/index.html#viam.app.data_client.DataClient.binary_data_by_ids).

{{% /tab %}}
{{% tab name="Go" %}}

**Parameters:**

- `ctx` [(Context)](https://pkg.go.dev/context#Context): A Context carries a deadline, a cancellation signal, and other values across API boundaries.
- `binaryDataIDs` [([]string)](https://pkg.go.dev/builtin#string)
- `opts` [(...*BinaryDataByIDsOptions)](https://pkg.go.dev/go.viam.com/rdk/app#BinaryDataByIDsOptions)

**Returns:**

- [([]*BinaryData)](https://pkg.go.dev/go.viam.com/rdk/app#BinaryData)
- [(error)](https://pkg.go.dev/builtin#error): An error, if one occurred.

For more information, see the [Go SDK Docs](https://pkg.go.dev/go.viam.com/rdk/app#DataClient.BinaryDataByIDs).

{{% /tab %}}
{{% tab name="TypeScript" %}}

**Parameters:**

- `ids` (string) (required): The IDs of the requested binary data.
- `includeBinary` (boolean) (optional): Whether to include binary file data with each retrieved file.

**Returns:**

- (Promise<[BinaryData](https://ts.viam.dev/classes/dataApi.BinaryData.html)[]>): An array of data objects.

**Example:**

```ts {class="line-numbers linkable-line-numbers"}
const data = await dataClient.binaryDataByIds([
  'ccb74b53-1235-4328-a4b9-91dff1915a50/x5vur1fmps/YAEzj5I1kTwtYsDdf4a7ctaJpGgKRHmnM9bJNVyblk52UpqmrnMVTITaBKZctKEh',
]);
```

For more information, see the [TypeScript SDK Docs](https://ts.viam.dev/interfaces/DataClient.html#binarydatabyids).

{{% /tab %}}
{{% tab name="Flutter" %}}

**Parameters:**

- `binaryIds` [List](https://api.flutter.dev/flutter/dart-core/List-class.html)<[BinaryID](https://flutter.viam.dev/viam_protos.app.data/BinaryID-class.html)> (required)
- `includeBinary` [bool](https://api.flutter.dev/flutter/dart-core/bool-class.html) (optional)

**Returns:**

- [Future](https://api.flutter.dev/flutter/dart-async/Future-class.html)<[BinaryDataByIDsResponse](https://flutter.viam.dev/viam_protos.app.data/BinaryDataByIDsResponse-class.html)>

**Example:**

```dart {class="line-numbers linkable-line-numbers"}
 _viam = await Viam.withApiKey(
     dotenv.env['API_KEY_ID'] ?? '',
     dotenv.env['API_KEY'] ?? ''
 );
 final dataClient = _viam.dataClient;

 try {
  final binaryIDs = [
   BinaryID(fileId: '<YOUR-FILE-ID>', organizationId: '<YOUR-ORG-ID>', locationId: '<YOUR-LOCATION-ID>'),
   BinaryID(fileId: '<YOUR-FILE-ID>', organizationId: '<YOUR-ORG-ID>', locationId: '<YOUR-LOCATION-ID>')
  ];

  final response = await dataClient.binaryDataByIds(
    binaryIDs,
    includeBinary: true
  );

  for (var dataPoint in response.data) {
    print(dataPoint.binary);
    print(dataPoint.metadata);
  }

  print('Successfully retrieved binary data by IDs');
 } catch (e) {
  print('Error retrieving binary data by IDs: $e');
 }
```

For more information, see the [Flutter SDK Docs](https://flutter.viam.dev/viam_sdk/DataClient/binaryDataByIds.html).

{{% /tab %}}
{{< /tabs >}}

### DeleteTabularData

Delete tabular data older than a specified number of days.
If the organization has a [hot data store](/data/hot-data-store/), matching data is deleted from that store as well.

{{< tabs >}}
{{% tab name="Python" %}}

**Parameters:**

- `organization_id` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (required): The ID of the organization to delete the data from. To find your organization ID, visit the organization settings page.
- `delete_older_than_days` ([int](https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex)) (required): Delete data that was captured more than this many days ago. For example, a value of 10 deletes any data that was captured more than 10 days ago. A value of 0 deletes all existing data.
- `filter` ([viam.proto.app.data.DeleteTabularFilter](https://python.viam.dev/autoapi/viam/proto/app/data/index.html#viam.proto.app.data.DeleteTabularFilter)) (optional): Optional filter to further constrain which data is deleted. If provided, only data matching the filter will be deleted. If omitted, data is deleted based on organization_id and delete_older_than_days.

**Returns:**

- ([int](https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex)): :   The number of items deleted.

**Example:**

```python {class="line-numbers linkable-line-numbers"}
tabular_data = await data_client.delete_tabular_data(
    organization_id="<YOUR-ORG-ID>",
    delete_older_than_days=150
)

# Delete with additional filter constraints
from viam.proto.app.data import DeleteTabularFilter
tabular_data = await data_client.delete_tabular_data(
    organization_id="<YOUR-ORG-ID>",
    delete_older_than_days=150,
    filter=DeleteTabularFilter(
        location_ids=["location-id"],
        component_name="camera"
    )
)
```

For more information, see the [Python SDK Docs](https://python.viam.dev/autoapi/viam/app/data_client/index.html#viam.app.data_client.DataClient.delete_tabular_data).

{{% /tab %}}
{{% tab name="Go" %}}

**Parameters:**

- `ctx` [(Context)](https://pkg.go.dev/context#Context): A Context carries a deadline, a cancellation signal, and other values across API boundaries.
- `organizationID` [(string)](https://pkg.go.dev/builtin#string)
- `deleteOlderThanDays` [(int)](https://pkg.go.dev/builtin#int)
- `filter` [(*pb.DeleteTabularFilter)](https://pkg.go.dev/go.viam.com/api/app/data/v1#DeleteTabularFilter)

**Returns:**

- [(int)](https://pkg.go.dev/builtin#int)
- [(error)](https://pkg.go.dev/builtin#error): An error, if one occurred.

For more information, see the [Go SDK Docs](https://pkg.go.dev/go.viam.com/rdk/app#DataClient.DeleteTabularData).

{{% /tab %}}
{{% tab name="TypeScript" %}}

**Parameters:**

- `organizationId` (string) (required): The ID of organization to delete data from.
- `deleteOlderThanDays` (number) (required): Delete data that was captured more than this many days ago. For
  example, a value of 10 deletes any data that was captured more than 10 days ago. A value of 0
  deletes all existing data.
- `filter` (PartialMessage) (optional): Optional filter to further constrain which data is deleted. If provided, only
  data matching the filter will be deleted. If omitted, data is deleted based on
  organization\_id and delete\_older\_than\_days.

**Returns:**

- (Promise<bigint>): The number of items deleted.

**Example:**

```ts {class="line-numbers linkable-line-numbers"}
const data = await dataClient.deleteTabularData(
  '123abc45-1234-5678-90ab-cdef12345678',
  10,
);

// Delete with additional filter constraints
const data = await dataClient.deleteTabularData(
  '123abc45-1234-5678-90ab-cdef12345678',
  10,
  {
    locationIds: ['location-id'],
    componentName: 'camera',
  },
);
```

For more information, see the [TypeScript SDK Docs](https://ts.viam.dev/interfaces/DataClient.html#deletetabulardata).

{{% /tab %}}
{{% tab name="Flutter" %}}

**Parameters:**

- `organizationId` [String](https://api.flutter.dev/flutter/dart-core/String-class.html) (required)
- `olderThanDays` [int](https://api.flutter.dev/flutter/dart-core/int-class.html) (required)
- `filter` [DeleteTabularFilter](https://flutter.viam.dev/viam_protos.app.data/DeleteTabularFilter-class.html)? (optional)

**Returns:**

- [Future](https://api.flutter.dev/flutter/dart-async/Future-class.html)<[int](https://api.flutter.dev/flutter/dart-core/int-class.html)>

**Example:**

```dart {class="line-numbers linkable-line-numbers"}
_viam = await Viam.withApiKey(
    dotenv.env['API_KEY_ID'] ?? '',
    dotenv.env['API_KEY'] ?? ''
);
final dataClient = _viam.dataClient;

try {
  // Delete all data older than 5 days
  dataClient.deleteTabularData("<YOUR-ORG-ID>", 5);

  // Delete data older than 5 days, filtered by location
  final filter = DeleteTabularFilter(locationIds: ["<YOUR-LOCATION-ID>"]);
  dataClient.deleteTabularData("<YOUR-ORG-ID>", 5, filter: filter);

 print('Successfully deleted tabular data');
} catch (e) {
 print('Error deleting tabular data: $e');
}
```

For more information, see the [Flutter SDK Docs](https://flutter.viam.dev/viam_sdk/DataClient/deleteTabularData.html).

{{% /tab %}}
{{< /tabs >}}

### DeleteBinaryDataByFilter

Filter and delete binary data.

{{< tabs >}}
{{% tab name="Python" %}}

**Parameters:**

- `filter` ([viam.proto.app.data.Filter](https://python.viam.dev/autoapi/viam/proto/app/data/index.html#viam.proto.app.data.Filter)) (optional): Optional, specifies binary data to delete. CAUTION: Passing an empty Filter deletes all binary data! You must specify an organization ID with organization_ids when using this option. To find your organization ID, visit the organization settings page.

**Returns:**

- ([int](https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex)): :   The number of items deleted.

**Example:**

```python {class="line-numbers linkable-line-numbers"}
from viam.utils import create_filter

my_filter = create_filter(component_name="left_motor", organization_ids=["<YOUR-ORG-ID>"])

res = await data_client.delete_binary_data_by_filter(my_filter)
```

For more information, see the [Python SDK Docs](https://python.viam.dev/autoapi/viam/app/data_client/index.html#viam.app.data_client.DataClient.delete_binary_data_by_filter).

{{% /tab %}}
{{% tab name="Go" %}}

**Parameters:**

- `ctx` [(Context)](https://pkg.go.dev/context#Context): A Context carries a deadline, a cancellation signal, and other values across API boundaries.
- `filter` [(*Filter)](https://pkg.go.dev/go.viam.com/rdk/app#Filter)

**Returns:**

- [(int)](https://pkg.go.dev/builtin#int)
- [(error)](https://pkg.go.dev/builtin#error): An error, if one occurred.

For more information, see the [Go SDK Docs](https://pkg.go.dev/go.viam.com/rdk/app#DataClient.DeleteBinaryDataByFilter).

{{% /tab %}}
{{% tab name="TypeScript" %}}

**Parameters:**

- `filter` ([Filter](https://ts.viam.dev/classes/dataApi.Filter.html)) (optional): Optional `pb.Filter` specifying binary data to delete. No `filter` implies all
  binary data.
- `includeInternalData` (boolean) (optional): Whether or not to delete internal data. Default is true.

**Returns:**

- (Promise<bigint>): The number of items deleted.

**Example:**

```ts {class="line-numbers linkable-line-numbers"}
const data = await dataClient.deleteBinaryDataByFilter({
  componentName: 'camera-1',
  componentType: 'rdk:component:camera',
  organizationIds: ['123abc45-1234-5678-90ab-cdef12345678'],
  startTime: new Date('2025-03-19'),
  endTime: new Date('2025-03-20'),
} as Filter);
```

For more information, see the [TypeScript SDK Docs](https://ts.viam.dev/interfaces/DataClient.html#deletebinarydatabyfilter).

{{% /tab %}}
{{% tab name="Flutter" %}}

**Parameters:**

- `filter` [Filter](https://flutter.viam.dev/viam_protos.app.data/Filter-class.html)? (required)
- `includeInternalData` [bool](https://api.flutter.dev/flutter/dart-core/bool-class.html) (optional)

**Returns:**

- [Future](https://api.flutter.dev/flutter/dart-async/Future-class.html)<[int](https://api.flutter.dev/flutter/dart-core/int-class.html)>

**Example:**

```dart {class="line-numbers linkable-line-numbers"}
 _viam = await Viam.withApiKey(
     dotenv.env['API_KEY_ID'] ?? '',
     dotenv.env['API_KEY'] ?? ''
 );
 final dataClient = _viam.dataClient;

 try {
  // Create a filter to target specific binary data. Must include at least one org ID.
  final filter = Filter(
   componentName: "camera-1",
   organizationIds: ["<YOUR-ORG-ID>"]
  );

  final deletedCount = await dataClient.deleteBinaryDataByFilter(filter);

  print('Successfully deleted binary data by filter: count $deletedCount');
 } catch (e) {
  print('Error deleting binary data by filter: $e');
 }
```

For more information, see the [Flutter SDK Docs](https://flutter.viam.dev/viam_sdk/DataClient/deleteBinaryDataByFilter.html).

{{% /tab %}}
{{< /tabs >}}

### DeleteBinaryDataByIDs

Filter and delete binary data by ids.

{{< tabs >}}
{{% tab name="Python" %}}

**Parameters:**

- `binary_ids` ([List[viam.proto.app.data.BinaryID] | List[str]](https://python.viam.dev/autoapi/viam/proto/app/data/index.html#viam.proto.app.data.BinaryID)) (required): Binary data ID strings specifying the data to be deleted or BinaryID objects. Must be non-empty. DEPRECATED: BinaryID is deprecated and will be removed in a future release. Instead, pass binary data IDs as a list of strings.

**Returns:**

- ([int](https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex)): :   The number of items deleted.

**Raises:**

- (GRPCError): If no binary data ID strings or BinaryID objects are provided.

**Example:**

```python {class="line-numbers linkable-line-numbers"}
from viam.proto.app.data import BinaryID
from viam.utils import create_filter

my_filter = create_filter(component_name="camera-1", organization_ids=["<YOUR-ORG-ID>"])
binary_metadata, count, last = await data_client.binary_data_by_filter(
    filter=my_filter,
    limit=20,
    include_binary_data=False
)

my_ids = []

for obj in binary_metadata:
    my_ids.append(
        obj.metadata.binary_data_id
    )

binary_data = await data_client.delete_binary_data_by_ids(my_ids)
```

For more information, see the [Python SDK Docs](https://python.viam.dev/autoapi/viam/app/data_client/index.html#viam.app.data_client.DataClient.delete_binary_data_by_ids).

{{% /tab %}}
{{% tab name="Go" %}}

**Parameters:**

- `ctx` [(Context)](https://pkg.go.dev/context#Context): A Context carries a deadline, a cancellation signal, and other values across API boundaries.
- `binaryDataIDs` [([]string)](https://pkg.go.dev/builtin#string)

**Returns:**

- [(int)](https://pkg.go.dev/builtin#int)
- [(error)](https://pkg.go.dev/builtin#error): An error, if one occurred.

For more information, see the [Go SDK Docs](https://pkg.go.dev/go.viam.com/rdk/app#DataClient.DeleteBinaryDataByIDs).

{{% /tab %}}
{{% tab name="TypeScript" %}}

**Parameters:**

- `ids` (string) (required): The IDs of the data to be deleted. Must be non-empty.

**Returns:**

- (Promise<bigint>): The number of items deleted.

**Example:**

```ts {class="line-numbers linkable-line-numbers"}
const data = await dataClient.deleteBinaryDataByIds([
  'ccb74b53-1235-4328-a4b9-91dff1915a50/x5vur1fmps/YAEzj5I1kTwtYsDdf4a7ctaJpGgKRHmnM9bJNVyblk52UpqmrnMVTITaBKZctKEh',
]);
```

For more information, see the [TypeScript SDK Docs](https://ts.viam.dev/interfaces/DataClient.html#deletebinarydatabyids).

{{% /tab %}}
{{% tab name="Flutter" %}}

**Parameters:**

- `binaryDataIds` [List](https://api.flutter.dev/flutter/dart-core/List-class.html)<[String](https://api.flutter.dev/flutter/dart-core/String-class.html)> (required)

**Returns:**

- [Future](https://api.flutter.dev/flutter/dart-async/Future-class.html)<[int](https://api.flutter.dev/flutter/dart-core/int-class.html)>

**Example:**

```dart {class="line-numbers linkable-line-numbers"}
 _viam = await Viam.withApiKey(
     dotenv.env['API_KEY_ID'] ?? '',
     dotenv.env['API_KEY'] ?? ''
 );
 final dataClient = _viam.dataClient;

 try {
  final binaryDataIds = [
  '<YOUR-BINARY-DATA-ID>',
  '<YOUR-BINARY-DATA-ID>'
  ];

  // Call the function to delete binary data
  await dataClient.deleteBinaryDataByIds(binaryDataIds);

  print('Successfully deleted binary data');
 } catch (e) {
  print('Error deleting binary data: $e');
 }
```

For more information, see the [Flutter SDK Docs](https://flutter.viam.dev/viam_sdk/DataClient/deleteBinaryDataByIds.html).

{{% /tab %}}
{{< /tabs >}}

### AddTagsToBinaryDataByIDs

Add tags to binary data by ids.

{{< tabs >}}
{{% tab name="Python" %}}

**Parameters:**

- `tags` (List[[str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)]) (required): List of tags to add to specified binary data. Must be non-empty.
- `binary_ids` ([List[viam.proto.app.data.BinaryID] | List[str]](https://python.viam.dev/autoapi/viam/proto/app/data/index.html#viam.proto.app.data.BinaryID)) (required): Binary data ID strings specifying the data to be tagged or BinaryID objects. Must be non-empty. DEPRECATED: BinaryID is deprecated and will be removed in a future release. Instead, pass binary data IDs as a list of strings.

**Returns:**

- None.

**Raises:**

- (GRPCError): If no binary data ID strings or BinaryID objects are provided.

**Example:**

```python {class="line-numbers linkable-line-numbers"}
from viam.utils import create_filter

tags = ["tag1", "tag2"]

my_filter = create_filter(component_name="camera-1", organization_ids=["<YOUR-ORG-ID>"])
binary_metadata, count, last = await data_client.binary_data_by_filter(
    filter=my_filter,
    limit=20,
    include_binary_data=False
)

my_ids = []

for obj in binary_metadata:
    my_ids.append(
        obj.metadata.binary_data_id
    )

binary_data = await data_client.add_tags_to_binary_data_by_ids(tags, my_ids)
```

For more information, see the [Python SDK Docs](https://python.viam.dev/autoapi/viam/app/data_client/index.html#viam.app.data_client.DataClient.add_tags_to_binary_data_by_ids).

{{% /tab %}}
{{% tab name="Go" %}}

**Parameters:**

- `ctx` [(Context)](https://pkg.go.dev/context#Context): A Context carries a deadline, a cancellation signal, and other values across API boundaries.
- `tags`
- `binaryDataIDs` [([]string)](https://pkg.go.dev/builtin#string)

**Returns:**

- [(error)](https://pkg.go.dev/builtin#error): An error, if one occurred.

For more information, see the [Go SDK Docs](https://pkg.go.dev/go.viam.com/rdk/app#DataClient.AddTagsToBinaryDataByIDs).

{{% /tab %}}
{{% tab name="TypeScript" %}}

**Parameters:**

- `tags` (string) (required): The list of tags to add to specified binary data. Must be non-empty.
- `ids` (string) (required): The IDs of the data to be tagged. Must be non-empty.

**Returns:**

- (Promise<void>)

**Example:**

```ts {class="line-numbers linkable-line-numbers"}
const data = await dataClient.addTagsToBinaryDataByIds(
  ['tag1', 'tag2'],
  [
    'ccb74b53-1235-4328-a4b9-91dff1915a50/x5vur1fmps/YAEzj5I1kTwtYsDdf4a7ctaJpGgKRHmnM9bJNVyblk52UpqmrnMVTITaBKZctKEh',
  ],
);
```

For more information, see the [TypeScript SDK Docs](https://ts.viam.dev/interfaces/DataClient.html#addtagstobinarydatabyids).

{{% /tab %}}
{{% tab name="Flutter" %}}

**Parameters:**

- `tags` [List](https://api.flutter.dev/flutter/dart-core/List-class.html)<[String](https://api.flutter.dev/flutter/dart-core/String-class.html)> (required)
- `binaryDataIds` [List](https://api.flutter.dev/flutter/dart-core/List-class.html)<[String](https://api.flutter.dev/flutter/dart-core/String-class.html)> (required)

**Returns:**

- [Future](https://api.flutter.dev/flutter/dart-async/Future-class.html)<void>

**Example:**

```dart {class="line-numbers linkable-line-numbers"}
 _viam = await Viam.withApiKey(
     dotenv.env['API_KEY_ID'] ?? '',
     dotenv.env['API_KEY'] ?? ''
 );
 final dataClient = _viam.dataClient;

 try {
  // List of tags to add
  final List<String> tags = ['tag_1', 'tag_2'];

  final binaryDataIds = [
  '<YOUR-BINARY-DATA-ID>',
  '<YOUR-BINARY-DATA-ID>'
  ];

  // Call the function with both tags and IDs
  await dataClient.addTagsToBinaryDataByIds(tags, binaryDataIds);

  print('Successfully added tags to binary IDs');
 } catch (e) {
  print('Error adding tags: $e');
 }
```

For more information, see the [Flutter SDK Docs](https://flutter.viam.dev/viam_sdk/DataClient/addTagsToBinaryDataByIds.html).

{{% /tab %}}
{{< /tabs >}}

### RemoveTagsFromBinaryDataByIDs

Remove tags from binary by ids.

{{< tabs >}}
{{% tab name="Python" %}}

**Parameters:**

- `tags` (List[[str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)]) (required): List of tags to remove from specified binary data. Must be non-empty.
- `binary_ids` ([List[viam.proto.app.data.BinaryID] | List[str]](https://python.viam.dev/autoapi/viam/proto/app/data/index.html#viam.proto.app.data.BinaryID)) (required): Binary data ID strings specifying the data to be untagged or BinaryID objects. Must be non-empty. DEPRECATED: BinaryID is deprecated and will be removed in a future release. Instead, pass binary data IDs as a list of strings.

**Returns:**

- ([int](https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex)): :   The number of tags removed.

**Raises:**

- (GRPCError): If no binary data ID strings, BinaryID objects, or tags are provided.

**Example:**

```python {class="line-numbers linkable-line-numbers"}
from viam.utils import create_filter

tags = ["tag1", "tag2"]

my_filter = create_filter(component_name="camera-1")

binary_metadata, count, last = await data_client.binary_data_by_filter(
    filter=my_filter,
    limit=50,
    include_binary_data=False
)

my_ids = []

for obj in binary_metadata:
    my_ids.append(
        obj.metadata.binary_data_id
    )

binary_data = await data_client.remove_tags_from_binary_data_by_ids(
    tags, my_ids)
```

For more information, see the [Python SDK Docs](https://python.viam.dev/autoapi/viam/app/data_client/index.html#viam.app.data_client.DataClient.remove_tags_from_binary_data_by_ids).

{{% /tab %}}
{{% tab name="Go" %}}

**Parameters:**

- `ctx` [(Context)](https://pkg.go.dev/context#Context): A Context carries a deadline, a cancellation signal, and other values across API boundaries.
- `tags`
- `binaryDataIDs` [([]string)](https://pkg.go.dev/builtin#string)

**Returns:**

- [(int)](https://pkg.go.dev/builtin#int)
- [(error)](https://pkg.go.dev/builtin#error): An error, if one occurred.

For more information, see the [Go SDK Docs](https://pkg.go.dev/go.viam.com/rdk/app#DataClient.RemoveTagsFromBinaryDataByIDs).

{{% /tab %}}
{{% tab name="TypeScript" %}}

**Parameters:**

- `tags` (string) (required): List of tags to remove from specified binary data. Must be non-empty.
- `ids` (string) (required): The IDs of the data to be edited. Must be non-empty.

**Returns:**

- (Promise<bigint>): The number of items deleted.

**Example:**

```ts {class="line-numbers linkable-line-numbers"}
const data = await dataClient.removeTagsFromBinaryDataByIds(
  ['tag1', 'tag2'],
  [
    'ccb74b53-1235-4328-a4b9-91dff1915a50/x5vur1fmps/YAEzj5I1kTwtYsDdf4a7ctaJpGgKRHmnM9bJNVyblk52UpqmrnMVTITaBKZctKEh',
  ],
);
```

For more information, see the [TypeScript SDK Docs](https://ts.viam.dev/interfaces/DataClient.html#removetagsfrombinarydatabyids).

{{% /tab %}}
{{% tab name="Flutter" %}}

**Parameters:**

- `tags` [List](https://api.flutter.dev/flutter/dart-core/List-class.html)<[String](https://api.flutter.dev/flutter/dart-core/String-class.html)> (required)
- `binaryDataIds` [List](https://api.flutter.dev/flutter/dart-core/List-class.html)<[String](https://api.flutter.dev/flutter/dart-core/String-class.html)> (required)

**Returns:**

- [Future](https://api.flutter.dev/flutter/dart-async/Future-class.html)<[int](https://api.flutter.dev/flutter/dart-core/int-class.html)>

**Example:**

```dart {class="line-numbers linkable-line-numbers"}
 _viam = await Viam.withApiKey(
     dotenv.env['API_KEY_ID'] ?? '',
     dotenv.env['API_KEY'] ?? ''
 );
 final dataClient = _viam.dataClient;

 try {
  // List of tags to remove
  final List<String> tags = ['tag_1', 'tag_2'];

  final binaryDataIds = [
  '<YOUR-BINARY-DATA-ID>',
  '<YOUR-BINARY-DATA-ID>'
  ];

  // Call the function with both tags and IDs
  await dataClient.removeTagsFromBinaryDataByIds(tags, binaryDataIds);

  print('Successfully removed tags from binary IDs');
 } catch (e) {
  print('Error removing tags: $e');
 }
```

For more information, see the [Flutter SDK Docs](https://flutter.viam.dev/viam_sdk/DataClient/removeTagsFromBinaryDataByIds.html).

{{% /tab %}}
{{< /tabs >}}

### TagsByFilter

Get a list of tags using a filter.

{{< tabs >}}
{{% tab name="Python" %}}

**Parameters:**

- `filter` ([viam.proto.app.data.Filter](https://python.viam.dev/autoapi/viam/proto/app/data/index.html#viam.proto.app.data.Filter)) (optional): Specifies subset ofdata to retrieve tags from. If none is provided, returns all tags.

**Returns:**

- (List[[str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)]): :   The list of tags.

**Example:**

```python {class="line-numbers linkable-line-numbers"}
from viam.utils import create_filter

my_filter = create_filter(component_name="my_camera")
tags = await data_client.tags_by_filter(my_filter)
```

For more information, see the [Python SDK Docs](https://python.viam.dev/autoapi/viam/app/data_client/index.html#viam.app.data_client.DataClient.tags_by_filter).

{{% /tab %}}
{{% tab name="TypeScript" %}}

**Parameters:**

- `filter` ([Filter](https://ts.viam.dev/classes/dataApi.Filter.html)) (optional): Optional `pb.Filter` specifying what data to get tags from. No `filter` implies
  all data.

**Returns:**

- (Promise<string[]>): The list of tags.

**Example:**

```ts {class="line-numbers linkable-line-numbers"}
const data = await dataClient.tagsByFilter({
  componentName: 'camera-1',
} as Filter);
```

For more information, see the [TypeScript SDK Docs](https://ts.viam.dev/interfaces/DataClient.html#tagsbyfilter).

{{% /tab %}}
{{% tab name="Flutter" %}}

**Parameters:**

- `filter` [Filter](https://flutter.viam.dev/viam_protos.app.data/Filter-class.html)? (required)

**Returns:**

- [Future](https://api.flutter.dev/flutter/dart-async/Future-class.html)<[List](https://api.flutter.dev/flutter/dart-core/List-class.html)<[String](https://api.flutter.dev/flutter/dart-core/String-class.html)>\>

**Example:**

```dart {class="line-numbers linkable-line-numbers"}
_viam = await Viam.withApiKey(
     dotenv.env['API_KEY_ID'] ?? '',
     dotenv.env['API_KEY'] ?? ''
);
final dataClient = _viam.dataClient;

try {
 // Create a filter to target specific binary data
 final filter = Filter(
   componentName: "camera-1",
 );

 // Call the function to get tags by filter
 final tags = await dataClient.tagsByFilter(filter);

 print('Successfully got tags: $tags');
} catch (e) {
 print('Error getting tags: $e');
}
```

For more information, see the [Flutter SDK Docs](https://flutter.viam.dev/viam_sdk/DataClient/tagsByFilter.html).

{{% /tab %}}
{{< /tabs >}}

### AddBoundingBoxToImageByID

Add a bounding box to an image specified by its BinaryID.

{{< tabs >}}
{{% tab name="Python" %}}

**Parameters:**

- `binary_id` ([viam.proto.app.data.BinaryID | str](https://python.viam.dev/autoapi/viam/proto/app/data/index.html#viam.proto.app.data.BinaryID)) (required): The binary data ID or BinaryID of the image to add the bounding box to. DEPRECATED: BinaryID is deprecated and will be removed in a future release. Instead, pass binary data IDs as a list of strings.
- `label` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (required): A label for the bounding box.
- `x_min_normalized` ([float](https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex)) (required): Min X value of the bounding box normalized from 0 to 1.
- `y_min_normalized` ([float](https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex)) (required): Min Y value of the bounding box normalized from 0 to 1.
- `x_max_normalized` ([float](https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex)) (required): Max X value of the bounding box normalized from 0 to 1.
- `y_max_normalized` ([float](https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex)) (required): Max Y value of the bounding box normalized from 0 to 1.
- `confidence_score` ([float](https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex)) (optional): Confidence level of the bounding box being correct.

**Returns:**

- ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)): :   The bounding box ID.

**Raises:**

- (GRPCError): If the X or Y values are outside of the [0, 1] range.

**Example:**

```python {class="line-numbers linkable-line-numbers"}
bbox_id = await data_client.add_bounding_box_to_image_by_id(
    binary_id="<YOUR-BINARY-DATA-ID>",
    label="label",
    x_min_normalized=0,
    y_min_normalized=.1,
    x_max_normalized=.2,
    y_max_normalized=.3,
    confidence_score=.95
)

print(bbox_id)
```

For more information, see the [Python SDK Docs](https://python.viam.dev/autoapi/viam/app/data_client/index.html#viam.app.data_client.DataClient.add_bounding_box_to_image_by_id).

{{% /tab %}}
{{% tab name="Go" %}}

**Parameters:**

- `ctx` [(Context)](https://pkg.go.dev/context#Context): A Context carries a deadline, a cancellation signal, and other values across API boundaries.
- `binaryDataID` [(string)](https://pkg.go.dev/builtin#string)
- `label` [(string)](https://pkg.go.dev/builtin#string)
- `xMinNormalized` [(float64)](https://pkg.go.dev/builtin#float64)
- `yMinNormalized` [(float64)](https://pkg.go.dev/builtin#float64)
- `xMaxNormalized` [(float64)](https://pkg.go.dev/builtin#float64)
- `yMaxNormalized` [(float64)](https://pkg.go.dev/builtin#float64)

**Returns:**

- [(string)](https://pkg.go.dev/builtin#string)
- [(error)](https://pkg.go.dev/builtin#error): An error, if one occurred.

For more information, see the [Go SDK Docs](https://pkg.go.dev/go.viam.com/rdk/app#DataClient.AddBoundingBoxToImageByID).

{{% /tab %}}
{{% tab name="TypeScript" %}}

**Parameters:**

- `binaryId` (string) (required): The ID of the image to add the bounding box to.
- `label` (string) (required): A label for the bounding box.
- `xMinNormalized` (number) (required): The min X value of the bounding box normalized from 0 to 1.
- `yMinNormalized` (number) (required): The min Y value of the bounding box normalized from 0 to 1.
- `xMaxNormalized` (number) (required): The max X value of the bounding box normalized from 0 to 1.
- `yMaxNormalized` (number) (required): The max Y value of the bounding box normalized from 0 to 1.
- `confidence` (number) (optional): Model's confidence in a predicted bounding box expressed as a
  normalized value from 0 to 1.

**Returns:**

- (Promise<string>): The bounding box ID.

**Example:**

```ts {class="line-numbers linkable-line-numbers"}
const bboxId = await dataClient.addBoundingBoxToImageById(
  'ccb74b53-1235-4328-a4b9-91dff1915a50/x5vur1fmps/YAEzj5I1kTwtYsDdf4a7ctaJpGgKRHmnM9bJNVyblk52UpqmrnMVTITaBKZctKEh',
  'label1',
  0.3,
  0.3,
  0.6,
  0.6,
  0.4,
);
```

For more information, see the [TypeScript SDK Docs](https://ts.viam.dev/interfaces/DataClient.html#addboundingboxtoimagebyid).

{{% /tab %}}
{{% tab name="Flutter" %}}

**Parameters:**

- `label` [String](https://api.flutter.dev/flutter/dart-core/String-class.html) (required)
- `binaryDataId` [String](https://api.flutter.dev/flutter/dart-core/String-class.html) (required)
- `xMinNormalized` [double](https://api.flutter.dev/flutter/dart-core/double-class.html) (required)
- `yMinNormalized` [double](https://api.flutter.dev/flutter/dart-core/double-class.html) (required)
- `xMaxNormalized` [double](https://api.flutter.dev/flutter/dart-core/double-class.html) (required)
- `yMaxNormalized` [double](https://api.flutter.dev/flutter/dart-core/double-class.html) (required)

**Returns:**

- [Future](https://api.flutter.dev/flutter/dart-async/Future-class.html)<[String](https://api.flutter.dev/flutter/dart-core/String-class.html)>

**Example:**

```dart {class="line-numbers linkable-line-numbers"}
_viam = await Viam.withApiKey(
     dotenv.env['API_KEY_ID'] ?? '',
     dotenv.env['API_KEY'] ?? ''
 );
 final dataClient = _viam.dataClient;

// Example binary ID to add a bounding box to
final binaryDataId = '<YOUR-BINARY-DATA-ID>';

try {
  await dataClient.addBoundingBoxToImageById(
    "label",
    binaryDataId,
    0,
   .1,
   .2,
   .3
  );
  print('Successfully added bounding box');
} catch (e) {
  print('Error adding bounding box: $e');
}
```

For more information, see the [Flutter SDK Docs](https://flutter.viam.dev/viam_sdk/DataClient/addBoundingBoxToImageById.html).

{{% /tab %}}
{{< /tabs >}}

### RemoveBoundingBoxFromImageByID

Removes a bounding box from an image specified by its BinaryID.

{{< tabs >}}
{{% tab name="Python" %}}

**Parameters:**

- `bbox_id` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (required): The ID of the bounding box to remove.
- `binary_id` ([viam.proto.app.data.BinaryID | str](https://python.viam.dev/autoapi/viam/proto/app/data/index.html#viam.proto.app.data.BinaryID)) (required): The binary data ID or BinaryID of the image to remove the bounding box from. DEPRECATED: BinaryID is deprecated and will be removed in a future release. Instead, pass binary data IDs as a list of strings.

**Returns:**

- None.

**Example:**

```python {class="line-numbers linkable-line-numbers"}
await data_client.remove_bounding_box_from_image_by_id(
binary_id="<YOUR-BINARY-DATA-ID>",
bbox_id="your-bounding-box-id-to-delete"
)
```

For more information, see the [Python SDK Docs](https://python.viam.dev/autoapi/viam/app/data_client/index.html#viam.app.data_client.DataClient.remove_bounding_box_from_image_by_id).

{{% /tab %}}
{{% tab name="Go" %}}

**Parameters:**

- `ctx` [(Context)](https://pkg.go.dev/context#Context): A Context carries a deadline, a cancellation signal, and other values across API boundaries.
- `bboxID` [(string)](https://pkg.go.dev/builtin#string)
- `binaryDataID` [(string)](https://pkg.go.dev/builtin#string)

**Returns:**

- [(error)](https://pkg.go.dev/builtin#error): An error, if one occurred.

For more information, see the [Go SDK Docs](https://pkg.go.dev/go.viam.com/rdk/app#DataClient.RemoveBoundingBoxFromImageByID).

{{% /tab %}}
{{% tab name="TypeScript" %}}

**Parameters:**

- `binId` (string) (required): The ID of the image to remove the bounding box from.
- `bboxId` (string) (required): The ID of the bounding box to remove.

**Returns:**

- (Promise<void>)

**Example:**

```ts {class="line-numbers linkable-line-numbers"}
await dataClient.removeBoundingBoxFromImageById(
  'ccb74b53-1235-4328-a4b9-91dff1915a50/x5vur1fmps/YAEzj5I1kTwtYsDdf4a7ctaJpGgKRHmnM9bJNVyblk52UpqmrnMVTITaBKZctKEh',
  '5Z9ryhkW7ULaXROjJO6ghPYulNllnH20QImda1iZFroZpQbjahK6igQ1WbYigXED',
);
```

For more information, see the [TypeScript SDK Docs](https://ts.viam.dev/interfaces/DataClient.html#removeboundingboxfromimagebyid).

{{% /tab %}}
{{% tab name="Flutter" %}}

**Parameters:**

- `bboxId` [String](https://api.flutter.dev/flutter/dart-core/String-class.html) (required)
- `binaryDataId` [String](https://api.flutter.dev/flutter/dart-core/String-class.html) (required)

**Returns:**

- [Future](https://api.flutter.dev/flutter/dart-async/Future-class.html)<void>

**Example:**

```dart {class="line-numbers linkable-line-numbers"}
_viam = await Viam.withApiKey(
     dotenv.env['API_KEY_ID'] ?? '',
     dotenv.env['API_KEY'] ?? ''
 );
 final dataClient = _viam.dataClient;

// Example binary ID to remove a bounding box from
final binaryDataId = '<YOUR-BINARY-DATA-ID>';

// Example bbox ID (label)
final bboxId = "label";
try {
  await dataClient.removeBoundingBoxFromImageById(
    bboxId,
    binaryDataId,
  );

  print('Successfully removed bounding box');
} catch (e) {
  print('Error removing bounding box: $e');
}
```

For more information, see the [Flutter SDK Docs](https://flutter.viam.dev/viam_sdk/DataClient/removeBoundingBoxFromImageById.html).

{{% /tab %}}
{{< /tabs >}}

### BoundingBoxLabelsByFilter

Get a list of bounding box labels using a Filter.

{{< tabs >}}
{{% tab name="Python" %}}

**Parameters:**

- `filter` ([viam.proto.app.data.Filter](https://python.viam.dev/autoapi/viam/proto/app/data/index.html#viam.proto.app.data.Filter)) (optional): Specifies data to retrieve bounding box labels from. If none is provided, returns labels.

**Returns:**

- (List[[str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)]): :   The list of bounding box labels.

**Example:**

```python {class="line-numbers linkable-line-numbers"}
from viam.utils import create_filter

my_filter = create_filter(component_name="my_camera")
bounding_box_labels = await data_client.bounding_box_labels_by_filter(
    my_filter)

print(bounding_box_labels)
```

For more information, see the [Python SDK Docs](https://python.viam.dev/autoapi/viam/app/data_client/index.html#viam.app.data_client.DataClient.bounding_box_labels_by_filter).

{{% /tab %}}
{{% tab name="Go" %}}

**Parameters:**

- `ctx` [(Context)](https://pkg.go.dev/context#Context): A Context carries a deadline, a cancellation signal, and other values across API boundaries.
- `filter` [(*Filter)](https://pkg.go.dev/go.viam.com/rdk/app#Filter)

**Returns:**

- [([]string)](https://pkg.go.dev/builtin#string)
- [(error)](https://pkg.go.dev/builtin#error): An error, if one occurred.

For more information, see the [Go SDK Docs](https://pkg.go.dev/go.viam.com/rdk/app#DataClient.BoundingBoxLabelsByFilter).

{{% /tab %}}
{{% tab name="TypeScript" %}}

**Parameters:**

- `filter` ([Filter](https://ts.viam.dev/classes/dataApi.Filter.html)) (optional): Optional `pb.Filter` specifying what data to get tags from. No `filter` implies
  all labels.

**Returns:**

- (Promise<string[]>): The list of bounding box labels.

**Example:**

```ts {class="line-numbers linkable-line-numbers"}
const data = await dataClient.boundingBoxLabelsByFilter({
  componentName: 'camera-1',
} as Filter);
```

For more information, see the [TypeScript SDK Docs](https://ts.viam.dev/interfaces/DataClient.html#boundingboxlabelsbyfilter).

{{% /tab %}}
{{% tab name="Flutter" %}}

**Parameters:**

- `filter` [Filter](https://flutter.viam.dev/viam_protos.app.data/Filter-class.html)? (required)

**Returns:**

- [Future](https://api.flutter.dev/flutter/dart-async/Future-class.html)<[List](https://api.flutter.dev/flutter/dart-core/List-class.html)<[String](https://api.flutter.dev/flutter/dart-core/String-class.html)>\>

**Example:**

```dart {class="line-numbers linkable-line-numbers"}
_viam = await Viam.withApiKey(
     dotenv.env['API_KEY_ID'] ?? '',
     dotenv.env['API_KEY'] ?? ''
);
final dataClient = _viam.dataClient;

try {
 // Create a filter to target specific binary data
 final filter = Filter(
   componentName: "camera-1",
 );

 // Call the function to get bounding box labels by filter
 final labels = await dataClient.boundingBoxLabelsByFilter(filter);

 print('Successfully got bounding box labels: $labels');
} catch (e) {
 print('Error getting bounding box labels: $e');
}
```

For more information, see the [Flutter SDK Docs](https://flutter.viam.dev/viam_sdk/DataClient/boundingBoxLabelsByFilter.html).

{{% /tab %}}
{{< /tabs >}}

### GetDatabaseConnection

Get a connection to access a MongoDB Atlas Data federation instance.

{{< tabs >}}
{{% tab name="Python" %}}

**Parameters:**

- `organization_id` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (required): The ID of the organization you’d like to connect to. To find your organization ID, visit the organization settings page.

**Returns:**

- ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)): :   The hostname of the federated database.

**Example:**

```python {class="line-numbers linkable-line-numbers"}
hostname = await data_client.get_database_connection(organization_id="<YOUR-ORG-ID>")
```

For more information, see the [Python SDK Docs](https://python.viam.dev/autoapi/viam/app/data_client/index.html#viam.app.data_client.DataClient.get_database_connection).

{{% /tab %}}
{{% tab name="Go" %}}

**Parameters:**

- `ctx` [(Context)](https://pkg.go.dev/context#Context): A Context carries a deadline, a cancellation signal, and other values across API boundaries.
- `organizationID` [(string)](https://pkg.go.dev/builtin#string)

**Returns:**

- [(*GetDatabaseConnectionResponse)](https://pkg.go.dev/go.viam.com/rdk/app#GetDatabaseConnectionResponse)
- [(error)](https://pkg.go.dev/builtin#error): An error, if one occurred.

For more information, see the [Go SDK Docs](https://pkg.go.dev/go.viam.com/rdk/app#DataClient.GetDatabaseConnection).

{{% /tab %}}
{{% tab name="TypeScript" %}}

**Parameters:**

- `organizationId` (string) (required): Organization to retrieve connection for.

**Returns:**

- (Promise<string>): Hostname of the federated database.

**Example:**

```ts {class="line-numbers linkable-line-numbers"}
const hostname = await dataClient.getDatabaseConnection(
  '123abc45-1234-5678-90ab-cdef12345678',
);
```

For more information, see the [TypeScript SDK Docs](https://ts.viam.dev/interfaces/DataClient.html#getdatabaseconnection).

{{% /tab %}}
{{% tab name="Flutter" %}}

**Parameters:**

- `organizationId` [String](https://api.flutter.dev/flutter/dart-core/String-class.html) (required)

**Returns:**

- [Future](https://api.flutter.dev/flutter/dart-async/Future-class.html)<[DatabaseConnection](https://flutter.viam.dev/viam_sdk/DatabaseConnection.html)>

**Example:**

```dart {class="line-numbers linkable-line-numbers"}
_viam = await Viam.withApiKey(
     dotenv.env['API_KEY_ID'] ?? '',
     dotenv.env['API_KEY'] ?? ''
);
final dataClient = _viam.dataClient;

try {
 final String organizationId = "<YOUR-ORG-ID>";
 // Get the database connection
 final connection = await dataClient.getDatabaseConnection(organizationId);

 final hostname = connection.hostname;
 final mongodbUri = connection.mongodbUri;

 print('Successfully got database connection: with hostname $hostname and mongodbUri $mongodbUri');
} catch (e) {
 print('Error getting database connection: $e');
}
```

For more information, see the [Flutter SDK Docs](https://flutter.viam.dev/viam_sdk/DataClient/getDatabaseConnection.html).

{{% /tab %}}
{{< /tabs >}}

### ConfigureDatabaseUser

Configure a database user for the Viam organization’s MongoDB Atlas Data Federation instance.
It can also be used to reset the password of the existing database user.

{{< tabs >}}
{{% tab name="Python" %}}

**Parameters:**

- `organization_id` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (required): The ID of the organization you’d like to configure a database user for. To find your organization ID, visit the organization settings page.
- `password` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (required): The password of the user.

**Returns:**

- None.

**Example:**

```python {class="line-numbers linkable-line-numbers"}
await data_client.configure_database_user(
    organization_id="<YOUR-ORG-ID>",
    password="Your_Password@1234"
)
```

For more information, see the [Python SDK Docs](https://python.viam.dev/autoapi/viam/app/data_client/index.html#viam.app.data_client.DataClient.configure_database_user).

{{% /tab %}}
{{% tab name="Go" %}}

**Parameters:**

- `ctx` [(Context)](https://pkg.go.dev/context#Context): A Context carries a deadline, a cancellation signal, and other values across API boundaries.
- `organizationID` [(string)](https://pkg.go.dev/builtin#string)
- `password` [(string)](https://pkg.go.dev/builtin#string)

**Returns:**

- [(error)](https://pkg.go.dev/builtin#error): An error, if one occurred.

For more information, see the [Go SDK Docs](https://pkg.go.dev/go.viam.com/rdk/app#DataClient.ConfigureDatabaseUser).

{{% /tab %}}
{{% tab name="TypeScript" %}}

**Parameters:**

- `organizationId` (string) (required): The ID of the organization.
- `password` (string) (required): The password of the user.

**Returns:**

- (Promise<void>)

**Example:**

```ts {class="line-numbers linkable-line-numbers"}
await dataClient.configureDatabaseUser(
  '123abc45-1234-5678-90ab-cdef12345678',
  'Password01!',
);
```

For more information, see the [TypeScript SDK Docs](https://ts.viam.dev/interfaces/DataClient.html#configuredatabaseuser).

{{% /tab %}}
{{% tab name="Flutter" %}}

**Parameters:**

- `organizationId` [String](https://api.flutter.dev/flutter/dart-core/String-class.html) (required)
- `password` [String](https://api.flutter.dev/flutter/dart-core/String-class.html) (required)

**Returns:**

- [Future](https://api.flutter.dev/flutter/dart-async/Future-class.html)<void>

**Example:**

```dart {class="line-numbers linkable-line-numbers"}
_viam = await Viam.withApiKey(
     dotenv.env['API_KEY_ID'] ?? '',
     dotenv.env['API_KEY'] ?? ''
);
final dataClient = _viam.dataClient;

try {
 await dataClient.configureDatabaseUser(
   "<YOUR-ORG-ID>",
   "PasswordLikeThis1234",
 );

 print('Successfully configured database user for this organization');
} catch (e) {
 print('Error configuring database user: $e');
}
```

For more information, see the [Flutter SDK Docs](https://flutter.viam.dev/viam_sdk/DataClient/configureDatabaseUser.html).

{{% /tab %}}
{{< /tabs >}}

### AddBinaryDataToDatasetByIDs

Add the `BinaryData` to the provided dataset.
This BinaryData will be tagged with the VIAM_DATASET\_{id} label.

{{< tabs >}}
{{% tab name="Python" %}}

**Parameters:**

- `binary_ids` ([List[viam.proto.app.data.BinaryID] | List[str]](https://python.viam.dev/autoapi/viam/proto/app/data/index.html#viam.proto.app.data.BinaryID)) (required): Unique identifiers for binary data to add to the dataset. To retrieve these IDs, navigate to the DATA page, click on an image, and copy its Binary Data ID from the details tab.
- `dataset_id` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (required): The ID of the dataset to be added to.  To retrieve the dataset ID:  Navigate to the DATASETS tab of the DATA page. Click on the dataset. Click the … menu. Select Copy dataset ID.

**Returns:**

- None.

**Example:**

```python {class="line-numbers linkable-line-numbers"}
binary_metadata, count, last = await data_client.binary_data_by_filter(
    include_binary_data=False
)

my_binary_data_ids = []

for obj in binary_metadata:
    my_binary_data_ids.append(
        obj.metadata.binary_data_id
        )

await data_client.add_binary_data_to_dataset_by_ids(
    binary_ids=my_binary_data_ids,
    dataset_id="abcd-1234xyz-8765z-123abc"
)
```

For more information, see the [Python SDK Docs](https://python.viam.dev/autoapi/viam/app/data_client/index.html#viam.app.data_client.DataClient.add_binary_data_to_dataset_by_ids).

{{% /tab %}}
{{% tab name="Go" %}}

**Parameters:**

- `ctx` [(Context)](https://pkg.go.dev/context#Context): A Context carries a deadline, a cancellation signal, and other values across API boundaries.
- `binaryDataIDs` [([]string)](https://pkg.go.dev/builtin#string)
- `datasetID` [(string)](https://pkg.go.dev/builtin#string)

**Returns:**

- [(error)](https://pkg.go.dev/builtin#error): An error, if one occurred.

For more information, see the [Go SDK Docs](https://pkg.go.dev/go.viam.com/rdk/app#DataClient.AddBinaryDataToDatasetByIDs).

{{% /tab %}}
{{% tab name="TypeScript" %}}

**Parameters:**

- `ids` (string) (required): The IDs of binary data to add to dataset.
- `datasetId` (string) (required): The ID of the dataset to be added to.

**Returns:**

- (Promise<void>)

**Example:**

```ts {class="line-numbers linkable-line-numbers"}
await dataClient.addBinaryDataToDatasetByIds(
  [
    'ccb74b53-1235-4328-a4b9-91dff1915a50/x5vur1fmps/YAEzj5I1kTwtYsDdf4a7ctaJpGgKRHmnM9bJNVyblk52UpqmrnMVTITaBKZctKEh',
  ],
  '12ab3de4f56a7bcd89ef0ab1',
);
```

For more information, see the [TypeScript SDK Docs](https://ts.viam.dev/interfaces/DataClient.html#addbinarydatatodatasetbyids).

{{% /tab %}}
{{% tab name="Flutter" %}}

**Parameters:**

- `binaryDataIds` [List](https://api.flutter.dev/flutter/dart-core/List-class.html)<[String](https://api.flutter.dev/flutter/dart-core/String-class.html)> (required)
- `datasetId` [String](https://api.flutter.dev/flutter/dart-core/String-class.html) (required)

**Returns:**

- [Future](https://api.flutter.dev/flutter/dart-async/Future-class.html)<void>

**Example:**

```dart {class="line-numbers linkable-line-numbers"}
_viam = await Viam.withApiKey(
     dotenv.env['API_KEY_ID'] ?? '',
     dotenv.env['API_KEY'] ?? ''
 );
 final dataClient = _viam.dataClient;

// Example binary IDs to add to the dataset
 final binaryDataIds = [
  '<YOUR-BINARY-DATA-ID>',
  '<YOUR-BINARY-DATA-ID>'
 ];

 // Dataset ID where the binary data will be added
 const datasetId = '<YOUR-DATASET-ID>';

 try {
   // Add the binary data to the dataset
   await dataClient.addBinaryDataToDatasetByIds(
     binaryDataIds,
     datasetId
 );
   print('Successfully added binary data to dataset');
 } catch (e) {
   print('Error adding binary data to dataset: $e');
 }
```

For more information, see the [Flutter SDK Docs](https://flutter.viam.dev/viam_sdk/DataClient/addBinaryDataToDatasetByIds.html).

{{% /tab %}}
{{< /tabs >}}

### RemoveBinaryDataFromDatasetByIDs

Remove the BinaryData from the provided dataset.
This BinaryData will lose the VIAM_DATASET\_{id} tag.

{{< tabs >}}
{{% tab name="Python" %}}

**Parameters:**

- `binary_ids` ([List[viam.proto.app.data.BinaryID] | List[str]](https://python.viam.dev/autoapi/viam/proto/app/data/index.html#viam.proto.app.data.BinaryID)) (required): Unique identifiers for the binary data to remove from the dataset. To retrieve these IDs, navigate to the DATA page, click on an image and copy its Binary Data ID from the details tab. DEPRECATED: BinaryID is deprecated and will be removed in a future release. Instead, pass binary data IDs as a list of strings.
- `dataset_id` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (required): The ID of the dataset to be removed from. To retrieve the dataset ID:  Navigate to the DATASETS tab of the DATA page. Click on the dataset. Click the … menu. Select Copy dataset ID.

**Returns:**

- None.

**Example:**

```python {class="line-numbers linkable-line-numbers"}
binary_metadata, count, last = await data_client.binary_data_by_filter(
    include_binary_data=False
)

my_binary_data_ids = []

for obj in binary_metadata:
    my_binary_data_ids.append(
        obj.metadata.binary_data_id
    )

await data_client.remove_binary_data_from_dataset_by_ids(
    binary_ids=my_binary_data_ids,
    dataset_id="abcd-1234xyz-8765z-123abc"
)
```

For more information, see the [Python SDK Docs](https://python.viam.dev/autoapi/viam/app/data_client/index.html#viam.app.data_client.DataClient.remove_binary_data_from_dataset_by_ids).

{{% /tab %}}
{{% tab name="Go" %}}

**Parameters:**

- `ctx` [(Context)](https://pkg.go.dev/context#Context): A Context carries a deadline, a cancellation signal, and other values across API boundaries.
- `binaryDataIDs` [([]string)](https://pkg.go.dev/builtin#string)
- `datasetID` [(string)](https://pkg.go.dev/builtin#string)

**Returns:**

- [(error)](https://pkg.go.dev/builtin#error): An error, if one occurred.

For more information, see the [Go SDK Docs](https://pkg.go.dev/go.viam.com/rdk/app#DataClient.RemoveBinaryDataFromDatasetByIDs).

{{% /tab %}}
{{% tab name="TypeScript" %}}

**Parameters:**

- `ids` (string) (required): The IDs of the binary data to remove from dataset.
- `datasetId` (string) (required): The ID of the dataset to be removed from.

**Returns:**

- (Promise<void>)

**Example:**

```ts {class="line-numbers linkable-line-numbers"}
await dataClient.removeBinaryDataFromDatasetByIds(
  [
    'ccb74b53-1235-4328-a4b9-91dff1915a50/x5vur1fmps/YAEzj5I1kTwtYsDdf4a7ctaJpGgKRHmnM9bJNVyblk52UpqmrnMVTITaBKZctKEh',
  ],
  '12ab3de4f56a7bcd89ef0ab1',
);
```

For more information, see the [TypeScript SDK Docs](https://ts.viam.dev/interfaces/DataClient.html#removebinarydatafromdatasetbyids).

{{% /tab %}}
{{% tab name="Flutter" %}}

**Parameters:**

- `binaryDataIds` [List](https://api.flutter.dev/flutter/dart-core/List-class.html)<[String](https://api.flutter.dev/flutter/dart-core/String-class.html)> (required)
- `datasetId` [String](https://api.flutter.dev/flutter/dart-core/String-class.html) (required)

**Returns:**

- [Future](https://api.flutter.dev/flutter/dart-async/Future-class.html)<void>

**Example:**

```dart {class="line-numbers linkable-line-numbers"}
_viam = await Viam.withApiKey(
     dotenv.env['API_KEY_ID'] ?? '',
     dotenv.env['API_KEY'] ?? ''
 );
 final dataClient = _viam.dataClient;

// Example binary IDs to remove from the dataset
 final binaryDataIds = [
  '<YOUR-BINARY-DATA-ID>',
  '<YOUR-BINARY-DATA-ID>'
 ];

 // Dataset ID where the binary data will be removed
 const datasetId = '<YOUR-DATASET-ID>';

 try {
   // Remove the binary data from the dataset
   await dataClient.removeBinaryDataFromDatasetByIds(
     binaryDataIds,
     datasetId
 );
   print('Successfully removed binary data from dataset');
 } catch (e) {
   print('Error removing binary data from dataset: $e');
 }
```

For more information, see the [Flutter SDK Docs](https://flutter.viam.dev/viam_sdk/DataClient/removeBinaryDataFromDatasetByIds.html).

{{% /tab %}}
{{< /tabs >}}

### GetDataPipeline

Get the configuration for a [data pipeline](/data/pipelines/create-a-pipeline/).
{{< tabs >}}
{{% tab name="Python" %}}

**Parameters:**

- `id` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (required): The ID of the data pipeline to get.

**Returns:**

- ([DataPipeline](https://python.viam.dev/autoapi/viam/app/data_client/index.html#viam.app.data_client.DataClient.DataPipeline)): :   The data pipeline with the given ID.

**Example:**

```python {class="line-numbers linkable-line-numbers"}
data_pipeline = await data_client.get_data_pipeline(id="<YOUR-DATA-PIPELINE-ID>")
```

For more information, see the [Python SDK Docs](https://python.viam.dev/autoapi/viam/app/data_client/index.html#viam.app.data_client.DataClient.get_data_pipeline).

{{% /tab %}}
{{% tab name="Go" %}}

**Parameters:**

- `ctx` [(Context)](https://pkg.go.dev/context#Context): A Context carries a deadline, a cancellation signal, and other values across API boundaries.
- `id` [(string)](https://pkg.go.dev/builtin#string)

**Returns:**

- [(*DataPipeline)](https://pkg.go.dev/go.viam.com/rdk/app#DataPipeline)
- [(error)](https://pkg.go.dev/builtin#error): An error, if one occurred.

For more information, see the [Go SDK Docs](https://pkg.go.dev/go.viam.com/rdk/app#DataClient.GetDataPipeline).

{{% /tab %}}
{{% tab name="TypeScript" %}}

**Parameters:**

- `pipelineId` (string) (required): The ID of the data pipeline.

**Returns:**

- (Promise<DataPipeline | null>): The data pipeline configuration or null if it does not exist.

**Example:**

```ts {class="line-numbers linkable-line-numbers"}
const pipeline = await dataClient.getPipeline('123abc45-1234-5678-90ab-cdef12345678');
```

For more information, see the [TypeScript SDK Docs](https://ts.viam.dev/interfaces/DataClient.html#getdatapipeline).

{{% /tab %}}
{{< /tabs >}}

### ListDataPipelines

List all of the [data pipelines](/data/pipelines/create-a-pipeline/) in an organization.

{{< tabs >}}
{{% tab name="Python" %}}

**Parameters:**

- `organization_id` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (required): The ID of the organization that owns the pipelines. You can obtain your organization ID from the organization settings page.

**Returns:**

- ([List[DataPipeline]](https://python.viam.dev/autoapi/viam/app/data_client/index.html#viam.app.data_client.DataClient.DataPipeline)): :   A list of all of the data pipelines for the given organization.

**Example:**

```python {class="line-numbers linkable-line-numbers"}
data_pipelines = await data_client.list_data_pipelines(organization_id="<YOUR-ORGANIZATION-ID>")
```

For more information, see the [Python SDK Docs](https://python.viam.dev/autoapi/viam/app/data_client/index.html#viam.app.data_client.DataClient.list_data_pipelines).

{{% /tab %}}
{{% tab name="Go" %}}

**Parameters:**

- `ctx` [(Context)](https://pkg.go.dev/context#Context): A Context carries a deadline, a cancellation signal, and other values across API boundaries.
- `organizationID` [(string)](https://pkg.go.dev/builtin#string)

**Returns:**

- [([]*DataPipeline)](https://pkg.go.dev/go.viam.com/rdk/app#DataPipeline)
- [(error)](https://pkg.go.dev/builtin#error): An error, if one occurred.

For more information, see the [Go SDK Docs](https://pkg.go.dev/go.viam.com/rdk/app#DataClient.ListDataPipelines).

{{% /tab %}}
{{% tab name="TypeScript" %}}

**Parameters:**

- `organizationId` (string) (required): The ID of the organization.

**Returns:**

- (Promise<DataPipeline[]>): The list of data pipelines.

**Example:**

```ts {class="line-numbers linkable-line-numbers"}
const pipelines = await dataClient.listDataPipelines(
  '123abc45-1234-5678-90ab-cdef12345678',
);
```

For more information, see the [TypeScript SDK Docs](https://ts.viam.dev/interfaces/DataClient.html#listdatapipelines).

{{% /tab %}}
{{< /tabs >}}

### CreateDataPipeline

Create a [data pipeline](/data/pipelines/create-a-pipeline/).
{{< tabs >}}
{{% tab name="Python" %}}

**Parameters:**

- `organization_id` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (required): The ID of the organization that will own the pipeline. You can obtain your organization ID from the organization settings page.
- `name` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (required): The name of the pipeline.
- `mql_binary` (List[Dict[[str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str), Any]]) (required): The MQL pipeline to run, as a list of MongoDB aggregation pipeline stages.
- `schedule` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (required): A cron expression representing the expected execution schedule in UTC (note this also defines the input time window; an hourly schedule would process 1 hour of data at a time).
- `enable_backfill` ([bool](https://docs.python.org/3/library/stdtypes.html#boolean-type-bool)) (required): When true, pipeline runs will be scheduled for the organization’s past data.
- `data_source_type` ([viam.proto.app.data.TabularDataSourceType.ValueType](https://python.viam.dev/autoapi/viam/gen/app/data/v1/data_pb2/index.html#viam.gen.app.data.v1.data_pb2.TabularDataSourceType)) (required): The type of data source to use for the pipeline. Defaults to TabularDataSourceType.TABULAR_DATA_SOURCE_TYPE_STANDARD.

**Returns:**

- ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)): :   The ID of the newly created pipeline.

**Example:**

```python {class="line-numbers linkable-line-numbers"}
data_pipeline_id = await data_client.create_data_pipeline(
    organization_id="<YOUR-ORGANIZATION-ID>",
    name="<YOUR-PIPELINE-NAME>",
    mql_binary=[<YOUR-MQL-PIPELINE-AGGREGATION>],
    schedule="<YOUR-SCHEDULE>",
    enable_backfill=False,
    data_source_type=TabularDataSourceType.TABULAR_DATA_SOURCE_TYPE_STANDARD,
)
```

For more information, see the [Python SDK Docs](https://python.viam.dev/autoapi/viam/app/data_client/index.html#viam.app.data_client.DataClient.create_data_pipeline).

{{% /tab %}}
{{% tab name="Go" %}}

**Parameters:**

- `ctx` [(Context)](https://pkg.go.dev/context#Context): A Context carries a deadline, a cancellation signal, and other values across API boundaries.
- `organizationID`
- `name` [(string)](https://pkg.go.dev/builtin#string)
- `query` [([]map[string]any)](https://pkg.go.dev/builtin#any)
- `schedule` [(string)](https://pkg.go.dev/builtin#string)
- `enableBackfill` [(bool)](https://pkg.go.dev/builtin#bool)
- `opts` [(*CreateDataPipelineOptions)](https://pkg.go.dev/go.viam.com/rdk/app#CreateDataPipelineOptions)

**Returns:**

- [(string)](https://pkg.go.dev/builtin#string)
- [(error)](https://pkg.go.dev/builtin#error): An error, if one occurred.

For more information, see the [Go SDK Docs](https://pkg.go.dev/go.viam.com/rdk/app#DataClient.CreateDataPipeline).

{{% /tab %}}
{{% tab name="TypeScript" %}}

**Parameters:**

- `organizationId` (string) (required): The ID of the organization.
- `name` (string) (required): The name of the data pipeline.
- `query` (Uint8Array) (required): The MQL query to run as a list of BSON documents.
- `schedule` (string) (required): The schedule to run the query on (cron expression).
- `enableBackfill` (boolean) (required): Whether to enable backfill for the data pipeline.
- `dataSourceType` ([TabularDataSourceType](https://ts.viam.dev/enums/dataApi.TabularDataSourceType.html)) (optional): The type of data source to use for the data pipeline.

**Returns:**

- (Promise<string>): The ID of the created data pipeline.

**Example:**

```ts {class="line-numbers linkable-line-numbers"}
// {@link JsonValue} is imported from @bufbuild/protobuf
const mqlQuery: Record<string, JsonValue>[] = [
  {
    $match: {
      component_name: 'sensor-1',
    },
  },
  {
    $limit: 5,
  },
];

const pipelineId = await dataClient.createDataPipeline(
  '123abc45-1234-5678-90ab-cdef12345678',
  'my-pipeline',
  mqlQuery,
  '0 0 * * *'
  false,
  0
);
```

For more information, see the [TypeScript SDK Docs](https://ts.viam.dev/interfaces/DataClient.html#createdatapipeline).

{{% /tab %}}
{{< /tabs >}}

### DeleteDataPipeline

Delete a [data pipeline](/data/pipelines/create-a-pipeline/), its execution history, and all of its output data.
{{< tabs >}}
{{% tab name="Python" %}}

**Parameters:**

- `id` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (required): The ID of the data pipeline to delete.

**Returns:**

- None.

**Example:**

```python {class="line-numbers linkable-line-numbers"}
await data_client.delete_data_pipeline(id="<YOUR-DATA-PIPELINE-ID>")
```

For more information, see the [Python SDK Docs](https://python.viam.dev/autoapi/viam/app/data_client/index.html#viam.app.data_client.DataClient.delete_data_pipeline).

{{% /tab %}}
{{% tab name="Go" %}}

**Parameters:**

- `ctx` [(Context)](https://pkg.go.dev/context#Context): A Context carries a deadline, a cancellation signal, and other values across API boundaries.
- `id` [(string)](https://pkg.go.dev/builtin#string)

**Returns:**

- [(error)](https://pkg.go.dev/builtin#error): An error, if one occurred.

For more information, see the [Go SDK Docs](https://pkg.go.dev/go.viam.com/rdk/app#DataClient.DeleteDataPipeline).

{{% /tab %}}
{{% tab name="TypeScript" %}}

**Parameters:**

- `pipelineId` (string) (required): The ID of the data pipeline.

**Returns:**

- (Promise<void>)

**Example:**

```ts {class="line-numbers linkable-line-numbers"}
await dataClient.deleteDataPipeline('123abc45-1234-5678-90ab-cdef12345678');
```

For more information, see the [TypeScript SDK Docs](https://ts.viam.dev/interfaces/DataClient.html#deletedatapipeline).

{{% /tab %}}
{{< /tabs >}}

### ListDataPipelineRuns

Get information about individual executions of a [data pipeline](/data/pipelines/create-a-pipeline/).
{{< tabs >}}
{{% tab name="Python" %}}

**Parameters:**

- `id` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (required): The ID of the pipeline to list runs for.
- `page_size` ([int](https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex)) (required): The number of runs to return per page. Defaults to 10.

**Returns:**

- ([DataPipelineRunsPage](https://python.viam.dev/autoapi/viam/app/data_client/index.html#viam.app.data_client.DataClient.DataPipelineRunsPage)): :   A page of data pipeline runs with pagination support.

**Example:**

```python {class="line-numbers linkable-line-numbers"}
data_pipeline_runs = await data_client.list_data_pipeline_runs(id="<YOUR-DATA-PIPELINE-ID>")
while len(data_pipeline_runs.runs) > 0:
    data_pipeline_runs = await data_pipeline_runs.next_page()
```

For more information, see the [Python SDK Docs](https://python.viam.dev/autoapi/viam/app/data_client/index.html#viam.app.data_client.DataClient.list_data_pipeline_runs).

{{% /tab %}}
{{% tab name="Go" %}}

**Parameters:**

- `ctx` [(Context)](https://pkg.go.dev/context#Context): A Context carries a deadline, a cancellation signal, and other values across API boundaries.
- `id` [(string)](https://pkg.go.dev/builtin#string)
- `pageSize` [(uint32)](https://pkg.go.dev/builtin#uint32)

**Returns:**

- [(*ListDataPipelineRunsPage)](https://pkg.go.dev/go.viam.com/rdk/app#ListDataPipelineRunsPage)
- [(error)](https://pkg.go.dev/builtin#error): An error, if one occurred.

For more information, see the [Go SDK Docs](https://pkg.go.dev/go.viam.com/rdk/app#DataClient.ListDataPipelineRuns).

{{% /tab %}}
{{% tab name="TypeScript" %}}

**Parameters:**

- `pipelineId` (string) (required): The ID of the data pipeline.
- `pageSize` (number) (optional): The number of runs to return per page.

**Returns:**

- (Promise<ListDataPipelineRunsPage>): A page of data pipeline runs.

**Example:**

```ts {class="line-numbers linkable-line-numbers"}
const page = await dataClient.listDataPipelineRuns('123abc45-1234-5678-90ab-cdef12345678');
page.runs.forEach((run) => {
  console.log(run);
});
page = await page.nextPage();
page.runs.forEach((run) => {
  console.log(run);
});
```

For more information, see the [TypeScript SDK Docs](https://ts.viam.dev/interfaces/DataClient.html#listdatapipelineruns).

{{% /tab %}}
{{< /tabs >}}

### RenameDataPipeline

Rename a [data pipeline](/data/pipelines/create-a-pipeline/).

{{< tabs >}}
{{% tab name="Go" %}}

**Parameters:**

- `ctx` [(Context)](https://pkg.go.dev/context#Context): A Context carries a deadline, a cancellation signal, and other values across API boundaries.
- `id`
- `name` [(string)](https://pkg.go.dev/builtin#string)

**Returns:**

- [(error)](https://pkg.go.dev/builtin#error): An error, if one occurred.

For more information, see the [Go SDK Docs](https://pkg.go.dev/go.viam.com/rdk/app#DataClient.RenameDataPipeline).

{{% /tab %}}
{{< /tabs >}}

### AddTagsToBinaryDataByFilter

Add tags to binary data by filter.

{{< tabs >}}
{{% tab name="Python" %}}

**Parameters:**

- `tags` (List[[str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)]) (required): List of tags to add to specified binary data. Must be non-empty.
- `filter` ([viam.proto.app.data.Filter](https://python.viam.dev/autoapi/viam/proto/app/data/index.html#viam.proto.app.data.Filter)) (optional): Specifies binary data to tag. If none is provided, tags all data.

**Returns:**

- None.

**Raises:**

- (GRPCError): If no tags are provided.

**Example:**

```python {class="line-numbers linkable-line-numbers"}
from viam.utils import create_filter

my_filter = create_filter(component_name="my_camera")
tags = ["tag1", "tag2"]
await data_client.add_tags_to_binary_data_by_filter(tags, my_filter)
```

For more information, see the [Python SDK Docs](https://python.viam.dev/autoapi/viam/app/data_client/index.html#viam.app.data_client.DataClient.add_tags_to_binary_data_by_filter).

{{% /tab %}}
{{< /tabs >}}

### CreateBinaryDataSignedURL

Create a signed URL for accessing binary data without authentication. The URL expires after the specified duration.
{{< tabs >}}
{{% tab name="Python" %}}

**Parameters:**

- `binary_data_id` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (required): The binary data ID of the file to create a signed URL for.
- `expiration_minutes` ([int](https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex)) (optional): Expiration time in minutes. Defaults to 15 minutes if not specified. Maximum allowed is 10080 minutes (7 days).

**Returns:**

- (Tuple[[str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str), [datetime.datetime](https://docs.python.org/3/library/datetime.html)]): :   A tuple containing:
    :   * `signed_url` (*str*): The signed URL for the binary data file.
        * `expires_at` (*datetime*): The expiration time of the signed URL token.

**Example:**

```python {class="line-numbers linkable-line-numbers"}
signed_url, expires_at = await data_client.create_binary_data_signed_url(
    binary_data_id="<YOUR-BINARY-DATA-ID>",
    expiration_minutes=60
)

print(f"Signed URL: {signed_url}")
print(f"Expires at: {expires_at}")
```

For more information, see the [Python SDK Docs](https://python.viam.dev/autoapi/viam/app/data_client/index.html#viam.app.data_client.DataClient.create_binary_data_signed_url).

{{% /tab %}}
{{< /tabs >}}

### CreateIndex

Create a custom index on your data to speed up queries. You specify the organization, the collection type (tabular or binary), and the fields to index.
{{< tabs >}}
{{% tab name="Python" %}}

**Parameters:**

- `organization_id` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (required): The ID of the organization that owns the data. To find your organization ID, visit the organization settings page.
- `collection_type` (viam.proto.app.data.IndexableCollection.ValueType) (required): The type of collection the index is on.
- `index_spec` (Dict[[str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str), Any]) (required): The MongoDB index specification defined in JSON format.
- `pipeline_name` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (optional): The name of the pipeline if the collection type is PIPELINE_SINK.

**Returns:**

- None.

For more information, see the [Python SDK Docs](https://python.viam.dev/autoapi/viam/app/data_client/index.html#viam.app.data_client.DataClient.create_index).

{{% /tab %}}
{{< /tabs >}}

### DeleteIndex

Delete a custom index from your data.
{{< tabs >}}
{{% tab name="Python" %}}

**Parameters:**

- `organization_id` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (required): The ID of the organization that owns the data. To find your organization ID, visit the organization settings page.
- `collection_type` (viam.proto.app.data.IndexableCollection.ValueType) (required): The type of collection the index is on.
- `index_name` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (required): The name of the index to delete.
- `pipeline_name` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (optional): The name of the pipeline if the collection type is PIPELINE_SINK.

**Returns:**

- None.

For more information, see the [Python SDK Docs](https://python.viam.dev/autoapi/viam/app/data_client/index.html#viam.app.data_client.DataClient.delete_index).

{{% /tab %}}
{{< /tabs >}}

### ListIndexes

List all custom indexes for an organization.
{{< tabs >}}
{{% tab name="Python" %}}

**Parameters:**

- `organization_id` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (required): The ID of the organization that owns the data. To find your organization ID, visit the organization settings page.
- `collection_type` (viam.proto.app.data.IndexableCollection.ValueType) (required): The type of collection the index is on.
- `pipeline_name` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (optional): The name of the pipeline if the collection type is PIPELINE_SINK.

**Returns:**

- ([Sequence[viam.proto.app.data.Index]](https://python.viam.dev/autoapi/viam/gen/app/data/v1/data_pb2/index.html#viam.gen.app.data.v1.data_pb2.Sequence)): :   A list of indexes.

For more information, see the [Python SDK Docs](https://python.viam.dev/autoapi/viam/app/data_client/index.html#viam.app.data_client.DataClient.list_indexes).

{{% /tab %}}
{{< /tabs >}}

### RemoveTagsFromBinaryDataByFilter

Remove tags from binary data by filter.

{{< tabs >}}
{{% tab name="Python" %}}

**Parameters:**

- `tags` (List[[str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)]) (required): List of tags to remove from specified binary data.
- `filter` ([viam.proto.app.data.Filter](https://python.viam.dev/autoapi/viam/proto/app/data/index.html#viam.proto.app.data.Filter)) (optional): Specifies binary data to untag. If none is provided, removes tags from all data.

**Returns:**

- ([int](https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex)): :   The number of tags removed.

**Raises:**

- (GRPCError): If no tags are provided.

**Example:**

```python {class="line-numbers linkable-line-numbers"}
from viam.utils import create_filter

my_filter = create_filter(component_name="my_camera")
tags = ["tag1", "tag2"]
res = await data_client.remove_tags_from_binary_data_by_filter(tags, my_filter)
```

For more information, see the [Python SDK Docs](https://python.viam.dev/autoapi/viam/app/data_client/index.html#viam.app.data_client.DataClient.remove_tags_from_binary_data_by_filter).

{{% /tab %}}
{{< /tabs >}}

### UpdateBoundingBox

Update an existing bounding box on an image. You can change the label, position, or dimensions of the bounding box.
{{< tabs >}}
{{% tab name="Python" %}}

**Parameters:**

- `binary_id` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (required): The binary data ID of the image to add the bounding box to.
- `bbox_id` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (required): The ID of the bounding box to be updated.
- `label` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (required): A label for the bounding box.
- `x_min_normalized` ([float](https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex)) (required): Min X value of the bounding box normalized from 0 to 1.
- `y_min_normalized` ([float](https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex)) (required): Min Y value of the bounding box normalized from 0 to 1.
- `x_max_normalized` ([float](https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex)) (required): Max X value of the bounding box normalized from 0 to 1.
- `y_max_normalized` ([float](https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex)) (required): Max Y value of the bounding box normalized from 0 to 1.
- `confidence_score` ([float](https://docs.python.org/3/library/stdtypes.html#numeric-types-int-float-complex)) (optional): Confidence level of the bounding box being correct.

**Returns:**

- None.

**Raises:**

- (GRPCError): If the X or Y values are outside of the [0, 1] range.

**Example:**

```python {class="line-numbers linkable-line-numbers"}
bbox_id = await data_client.update_bounding_box_to_image_by_id(
    binary_id="<YOUR-BINARY-DATA-ID>",
    bbox_id="2"
    label="label",
    x_min_normalized=0,
    y_min_normalized=.1,
    x_max_normalized=.2,
    y_max_normalized=.3,
    confidence_score=.95
)
```

For more information, see the [Python SDK Docs](https://python.viam.dev/autoapi/viam/app/data_client/index.html#viam.app.data_client.DataClient.update_bounding_box).

{{% /tab %}}
{{< /tabs >}}


### CreateDataset

Create a new dataset.

{{< tabs >}}
{{% tab name="Python" %}}

**Parameters:**

- `name` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (required): The name of the dataset being created.
- `organization_id` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (required): The ID of the organization where the dataset is being created. To find your organization ID, visit the organization settings page.
- `type` (viam.proto.app.dataset.DatasetType.ValueType) (optional): The membership kind for the new dataset. Defaults to DATASET_TYPE_BINARY_DATA when unset.

**Returns:**

- ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)): :   The dataset ID of the created dataset.

**Example:**

```python {class="line-numbers linkable-line-numbers"}
dataset_id = await data_client.create_dataset(
    name="<DATASET-NAME>",
    organization_id="<YOUR-ORG-ID>"
)
print(dataset_id)
```

For more information, see the [Python SDK Docs](https://python.viam.dev/autoapi/viam/app/data_client/index.html#viam.app.data_client.DataClient.create_dataset).

{{% /tab %}}
{{% tab name="Go" %}}

**Parameters:**

- `ctx` [(Context)](https://pkg.go.dev/context#Context): A Context carries a deadline, a cancellation signal, and other values across API boundaries.
- `name`
- `organizationID` [(string)](https://pkg.go.dev/builtin#string)

**Returns:**

- [(string)](https://pkg.go.dev/builtin#string)
- [(error)](https://pkg.go.dev/builtin#error): An error, if one occurred.

For more information, see the [Go SDK Docs](https://pkg.go.dev/go.viam.com/rdk/app#DataClient.CreateDataset).

{{% /tab %}}
{{% tab name="TypeScript" %}}

**Parameters:**

- `name` (string) (required): The name of the new dataset.
- `organizationId` (string) (required): The ID of the organization the dataset is being created in.

**Returns:**

- (Promise<string>): The ID of the dataset.

**Example:**

```ts {class="line-numbers linkable-line-numbers"}
const datasetId = await dataClient.createDataset(
  'my-new-dataset',
  '123abc45-1234-5678-90ab-cdef12345678',
);
```

For more information, see the [TypeScript SDK Docs](https://ts.viam.dev/interfaces/DataClient.html#createdataset).

{{% /tab %}}
{{% tab name="Flutter" %}}

**Parameters:**

- `orgId` [String](https://api.flutter.dev/flutter/dart-core/String-class.html) (required)
- `name` [String](https://api.flutter.dev/flutter/dart-core/String-class.html) (required)

**Returns:**

- [Future](https://api.flutter.dev/flutter/dart-async/Future-class.html)<[String](https://api.flutter.dev/flutter/dart-core/String-class.html)>

**Example:**

```dart {class="line-numbers linkable-line-numbers"}
_viam = await Viam.withApiKey(
     dotenv.env['API_KEY_ID'] ?? '',
     dotenv.env['API_KEY'] ?? ''
 );
 final dataClient = _viam.dataClient;

 // Org ID to create dataset in
 const orgId = '<YOUR-ORG-ID>';

 try {
   // Create the dataset
   final datasetId = await dataClient.createDataset(orgId, "example-dataset");
   print('Successfully created dataset');
 } catch (e) {
   print('Error creating dataset: $e');
 }
```

For more information, see the [Flutter SDK Docs](https://flutter.viam.dev/viam_sdk/DataClient/createDataset.html).

{{% /tab %}}
{{< /tabs >}}

### DeleteDataset

Delete a dataset.

{{< tabs >}}
{{% tab name="Python" %}}

**Parameters:**

- `id` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (required): The ID of the dataset. To retrieve the dataset ID:  Navigate to the DATASETS tab of the DATA page. Click on the dataset. Click the … menu. Select Copy dataset ID.

**Returns:**

- None.

**Example:**

```python {class="line-numbers linkable-line-numbers"}
await data_client.delete_dataset(
    id="<YOUR-DATASET-ID>"
)
```

For more information, see the [Python SDK Docs](https://python.viam.dev/autoapi/viam/app/data_client/index.html#viam.app.data_client.DataClient.delete_dataset).

{{% /tab %}}
{{% tab name="Go" %}}

**Parameters:**

- `ctx` [(Context)](https://pkg.go.dev/context#Context): A Context carries a deadline, a cancellation signal, and other values across API boundaries.
- `id` [(string)](https://pkg.go.dev/builtin#string)

**Returns:**

- [(error)](https://pkg.go.dev/builtin#error): An error, if one occurred.

For more information, see the [Go SDK Docs](https://pkg.go.dev/go.viam.com/rdk/app#DataClient.DeleteDataset).

{{% /tab %}}
{{% tab name="TypeScript" %}}

**Parameters:**

- `id` (string) (required): The ID of the dataset.

**Returns:**

- (Promise<void>)

**Example:**

```ts {class="line-numbers linkable-line-numbers"}
await dataClient.deleteDataset('12ab3de4f56a7bcd89ef0ab1');
```

For more information, see the [TypeScript SDK Docs](https://ts.viam.dev/interfaces/DataClient.html#deletedataset).

{{% /tab %}}
{{% tab name="Flutter" %}}

**Parameters:**

- `id` [String](https://api.flutter.dev/flutter/dart-core/String-class.html) (required)

**Returns:**

- [Future](https://api.flutter.dev/flutter/dart-async/Future-class.html)<void>

**Example:**

```dart {class="line-numbers linkable-line-numbers"}
_viam = await Viam.withApiKey(
     dotenv.env['API_KEY_ID'] ?? '',
     dotenv.env['API_KEY'] ?? ''
 );
 final dataClient = _viam.dataClient;

 // Dataset ID to delete
 const datasetId = '<YOUR-DATASET-ID>';

 try {
   // Delete the dataset
   await dataClient.deleteDataset(datasetId);
   print('Successfully deleted dataset');
 } catch (e) {
   print('Error deleting dataset: $e');
 }
```

For more information, see the [Flutter SDK Docs](https://flutter.viam.dev/viam_sdk/DataClient/deleteDataset.html).

{{% /tab %}}
{{< /tabs >}}

### RenameDataset

Rename a dataset specified by the dataset ID.

{{< tabs >}}
{{% tab name="Python" %}}

**Parameters:**

- `id` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (required): The ID of the dataset. To retrieve the dataset ID:  Navigate to the DATASETS tab of the DATA page. Click on the dataset. Click the … menu. Select Copy dataset ID.
- `name` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (required): The new name of the dataset.

**Returns:**

- None.

**Example:**

```python {class="line-numbers linkable-line-numbers"}
await data_client.rename_dataset(
    id="<YOUR-DATASET-ID>",
    name="MyDataset"
)
```

For more information, see the [Python SDK Docs](https://python.viam.dev/autoapi/viam/app/data_client/index.html#viam.app.data_client.DataClient.rename_dataset).

{{% /tab %}}
{{% tab name="Go" %}}

**Parameters:**

- `ctx` [(Context)](https://pkg.go.dev/context#Context): A Context carries a deadline, a cancellation signal, and other values across API boundaries.
- `id`
- `name` [(string)](https://pkg.go.dev/builtin#string)

**Returns:**

- [(error)](https://pkg.go.dev/builtin#error): An error, if one occurred.

For more information, see the [Go SDK Docs](https://pkg.go.dev/go.viam.com/rdk/app#DataClient.RenameDataset).

{{% /tab %}}
{{% tab name="TypeScript" %}}

**Parameters:**

- `id` (string) (required): The ID of the dataset.
- `name` (string) (required): The new name of the dataset.

**Returns:**

- (Promise<void>)

**Example:**

```ts {class="line-numbers linkable-line-numbers"}
await dataClient.renameDataset('12ab3de4f56a7bcd89ef0ab1', 'my-new-dataset');
```

For more information, see the [TypeScript SDK Docs](https://ts.viam.dev/interfaces/DataClient.html#renamedataset).

{{% /tab %}}
{{% tab name="Flutter" %}}

**Parameters:**

- `id` [String](https://api.flutter.dev/flutter/dart-core/String-class.html) (required)
- `name` [String](https://api.flutter.dev/flutter/dart-core/String-class.html) (required)

**Returns:**

- [Future](https://api.flutter.dev/flutter/dart-async/Future-class.html)<void>

**Example:**

```dart {class="line-numbers linkable-line-numbers"}
_viam = await Viam.withApiKey(
     dotenv.env['API_KEY_ID'] ?? '',
     dotenv.env['API_KEY'] ?? ''
 );
 final dataClient = _viam.dataClient;

 // Dataset ID to rename
 const datasetId = '<YOUR-DATASET-ID>';

 try {
   // Rename the dataset
   await dataClient.renameDataset(datasetId, "new-name");
   print('Successfully renamed dataset');
 } catch (e) {
   print('Error renaming dataset: $e');
 }
```

For more information, see the [Flutter SDK Docs](https://flutter.viam.dev/viam_sdk/DataClient/renameDataset.html).

{{% /tab %}}
{{< /tabs >}}

### ListDatasetsByOrganizationID

Get the datasets in an organization.

{{< tabs >}}
{{% tab name="Python" %}}

**Parameters:**

- `organization_id` ([str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)) (required): The ID of the organization you’d like to retrieve datasets from. To find your organization ID, visit the organization settings page.
- `dataset_type` (viam.proto.app.dataset.DatasetType.ValueType) (optional): Optional filter on dataset type. If not provided, all dataset types will be returned.

**Returns:**

- ([Sequence[viam.proto.app.dataset.Dataset]](https://python.viam.dev/autoapi/viam/gen/app/data/v1/data_pb2/index.html#viam.gen.app.data.v1.data_pb2.Sequence)): :   The list of datasets in the organization.

**Example:**

```python {class="line-numbers linkable-line-numbers"}
datasets = await data_client.list_datasets_by_organization_id(
    organization_id="<YOUR-ORG-ID>"
)
print(datasets)
```

For more information, see the [Python SDK Docs](https://python.viam.dev/autoapi/viam/app/data_client/index.html#viam.app.data_client.DataClient.list_datasets_by_organization_id).

{{% /tab %}}
{{% tab name="Go" %}}

**Parameters:**

- `ctx` [(Context)](https://pkg.go.dev/context#Context): A Context carries a deadline, a cancellation signal, and other values across API boundaries.
- `organizationID` [(string)](https://pkg.go.dev/builtin#string)

**Returns:**

- [([]*Dataset)](https://pkg.go.dev/go.viam.com/rdk/app#Dataset)
- [(error)](https://pkg.go.dev/builtin#error): An error, if one occurred.

For more information, see the [Go SDK Docs](https://pkg.go.dev/go.viam.com/rdk/app#DataClient.ListDatasetsByOrganizationID).

{{% /tab %}}
{{% tab name="TypeScript" %}}

**Parameters:**

- `organizationId` (string) (required): The ID of the organization.
- `type` ([DatasetType](https://ts.viam.dev/enums/DatasetType.html)) (optional): Optional dataset type to filter on.

**Returns:**

- (Promise<Dataset[]>): The list of datasets in the organization.

**Example:**

```ts {class="line-numbers linkable-line-numbers"}
const datasets = await dataClient.listDatasetsByOrganizationID(
  '123abc45-1234-5678-90ab-cdef12345678',
);
```

For more information, see the [TypeScript SDK Docs](https://ts.viam.dev/interfaces/DataClient.html#listdatasetsbyorganizationid).

{{% /tab %}}
{{% tab name="Flutter" %}}

**Parameters:**

- `orgId` [String](https://api.flutter.dev/flutter/dart-core/String-class.html) (required)

**Returns:**

- [Future](https://api.flutter.dev/flutter/dart-async/Future-class.html)<[List](https://api.flutter.dev/flutter/dart-core/List-class.html)<[Dataset](https://flutter.viam.dev/viam_protos.app.dataset/Dataset-class.html)>\>

**Example:**

```dart {class="line-numbers linkable-line-numbers"}
_viam = await Viam.withApiKey(
     dotenv.env['API_KEY_ID'] ?? '',
     dotenv.env['API_KEY'] ?? ''
 );
 final dataClient = _viam.dataClient;

 // Org ID to list datasets from
 const orgId = '<YOUR-ORG-ID>';

 try {
   // List datasets from org
   final datasets = await dataClient.listDatasetsByOrganizationID(orgId);
   print('Successfully retrieved list of datasets: $datasets');
 } catch (e) {
   print('Error retrieving list of datasets: $e');
 }
```

For more information, see the [Flutter SDK Docs](https://flutter.viam.dev/viam_sdk/DataClient/listDatasetsByOrganizationID.html).

{{% /tab %}}
{{< /tabs >}}

### ListDatasetsByIDs

Get a list of datasets using their IDs.

{{< tabs >}}
{{% tab name="Python" %}}

**Parameters:**

- `ids` (List[[str](https://docs.python.org/3/library/stdtypes.html#text-sequence-type-str)]) (required): The IDs of the datasets that you would like to retrieve information about. To retrieve a dataset ID:  Navigate to the DATASETS tab of the DATA page. Click on the dataset. Click the … menu. Select Copy dataset ID.

**Returns:**

- ([Sequence[viam.proto.app.dataset.Dataset]](https://python.viam.dev/autoapi/viam/gen/app/data/v1/data_pb2/index.html#viam.gen.app.data.v1.data_pb2.Sequence)): :   The list of datasets.

**Example:**

```python {class="line-numbers linkable-line-numbers"}
datasets = await data_client.list_dataset_by_ids(
    ids=["<YOUR-DATASET-ID-1>, <YOUR-DATASET-ID-2>"]
)
print(datasets)
```

For more information, see the [Python SDK Docs](https://python.viam.dev/autoapi/viam/app/data_client/index.html#viam.app.data_client.DataClient.list_dataset_by_ids).

{{% /tab %}}
{{% tab name="Go" %}}

**Parameters:**

- `ctx` [(Context)](https://pkg.go.dev/context#Context): A Context carries a deadline, a cancellation signal, and other values across API boundaries.
- `ids` [([]string)](https://pkg.go.dev/builtin#string)

**Returns:**

- [([]*Dataset)](https://pkg.go.dev/go.viam.com/rdk/app#Dataset)
- [(error)](https://pkg.go.dev/builtin#error): An error, if one occurred.

For more information, see the [Go SDK Docs](https://pkg.go.dev/go.viam.com/rdk/app#DataClient.ListDatasetsByIDs).

{{% /tab %}}
{{% tab name="TypeScript" %}}

**Parameters:**

- `ids` (string) (required): The list of IDs of the datasets.

**Returns:**

- (Promise<Dataset[]>): The list of datasets.

**Example:**

```ts {class="line-numbers linkable-line-numbers"}
const datasets = await dataClient.listDatasetsByIds(['12ab3de4f56a7bcd89ef0ab1']);
```

For more information, see the [TypeScript SDK Docs](https://ts.viam.dev/interfaces/DataClient.html#listdatasetsbyids).

{{% /tab %}}
{{% tab name="Flutter" %}}

**Parameters:**

- `ids` [List](https://api.flutter.dev/flutter/dart-core/List-class.html)<[String](https://api.flutter.dev/flutter/dart-core/String-class.html)> (required)

**Returns:**

- [Future](https://api.flutter.dev/flutter/dart-async/Future-class.html)<[List](https://api.flutter.dev/flutter/dart-core/List-class.html)<[Dataset](https://flutter.viam.dev/viam_protos.app.dataset/Dataset-class.html)>\>

**Example:**

```dart {class="line-numbers linkable-line-numbers"}
_viam = await Viam.withApiKey(
     dotenv.env['API_KEY_ID'] ?? '',
     dotenv.env['API_KEY'] ?? ''
 );
 final dataClient = _viam.dataClient;

 const datasetIds = ["<YOUR-DATASET-ID>", "<YOUR-DATASET-ID-2>"];

 try {
   // List datasets by ids
   final datasets = await dataClient.listDatasetsByIDs(datasetIds);
   print('Successfully listed datasets by ids: $datasets');
 } catch (e) {
   print('Error retrieving datasets by ids: $e');
 }
```

For more information, see the [Flutter SDK Docs](https://flutter.viam.dev/viam_sdk/DataClient/listDatasetsByIDs.html).

{{% /tab %}}
{{< /tabs >}}


