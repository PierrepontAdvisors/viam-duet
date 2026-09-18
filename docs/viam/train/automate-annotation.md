# Automate annotation

Use ML models to auto-label images and programmatically build annotated datasets.
> Source: https://docs.viam.com/train/automate-annotation/


Manually labeling hundreds of images is slow. If you already have a trained ML
model -- even a rough first version -- you can use it to generate label
predictions automatically. You review and correct the predictions instead of
labeling from scratch.

You can also use the SDKs to annotate images programmatically, or combine
capture, annotation, and dataset management into a single script for continuous
dataset improvement.

## Auto-predict labels

Use an existing ML model to generate predictions for images in a dataset,
then review each prediction. This works with both classification models
(which generate tags) and object detection models (which generate bounding boxes).

1. Navigate to your [dataset's page](https://app.viam.com/datasets/).
1. Click **Get auto-predictions**.
1. **Select** a model to generate predictions with.
1. Set the **confidence threshold** above which to create a label prediction.
1. Click **Get predictions**.
1. Once predictions have finished generating, click **Review predictions**.
1. For each image, **Accept (A)** or **Reject (R)** each prediction.

## Programmatic tagging with SDKs

Use an ML model to generate tags for images, then pass the tags and image IDs
to the data client API.




### Python

```python
import asyncio

from viam.rpc.dial import DialOptions, Credentials
from viam.app.viam_client import ViamClient
from viam.media.video import ViamImage
from viam.robot.client import RobotClient
from viam.services.vision import VisionClient
from grpclib.exceptions import GRPCError

# Configuration constants – replace with your actual values
API_KEY = ""  # API key, find or create in your organization settings
API_KEY_ID = ""  # API key ID, find or create in your organization settings
MACHINE_ADDRESS = ""  # the address of the machine you want to capture images from
CLASSIFIER_NAME = ""  # the name of the classifier you want to use
BINARY_DATA_ID = ""  # the ID of the image you want to label

async def connect() -> ViamClient:
    """Establish a connection to the Viam client using API credentials."""
    dial_options = DialOptions(
        credentials=Credentials(
            type="api-key",
            payload=API_KEY,
        ),
        auth_entity=API_KEY_ID
    )
    return await ViamClient.create_from_dial_options(dial_options)

async def connect_machine() -> RobotClient:
    """Establish a connection to the robot using the robot address."""
    machine_opts = RobotClient.Options.with_api_key(
        api_key=API_KEY,
        api_key_id=API_KEY_ID
    )
    return await RobotClient.at_address(MACHINE_ADDRESS, machine_opts)

async def main() -> int:
    viam_client = await connect()
    data_client = viam_client.data_client
    machine = await connect_machine()

    classifier = VisionClient.from_robot(machine, CLASSIFIER_NAME)

    # Get image from data in Viam
    data = await data_client.binary_data_by_ids([BINARY_DATA_ID])
    binary_data = data[0]

    # Convert binary data to ViamImage
    image = ViamImage(binary_data.binary, binary_data.metadata.capture_metadata.mime_type)

    # Get tags using the image
    tags = await classifier.get_classifications(image=image, image_format=binary_data.metadata.capture_metadata.mime_type, count=2)

    if not len(tags):
        print("No tags found")
        return 1
    else:
        for tag in tags:
            await data_client.add_tags_to_binary_data_by_ids(
                tags=[tag.class_name],
                binary_ids=[BINARY_DATA_ID]
            )
            print(f"Added tag to image: {tag}")

    viam_client.close()
    await machine.close()

    return 0

if __name__ == "__main__":
    asyncio.run(main())
```

### Go

```go
package main

import (
	"context"
	"fmt"

	"go.viam.com/rdk/app"
	"go.viam.com/rdk/components/camera"
	rdkdata "go.viam.com/rdk/data"
	"go.viam.com/rdk/logging"
	"go.viam.com/rdk/robot/client"
	"go.viam.com/rdk/services/vision"
)

func main() {
	apiKey := ""
	apiKeyID := ""
	machineAddress := ""
	classifierName := ""
	binaryDataID := ""

	logger := logging.NewDebugLogger("client")
	ctx := context.Background()

	viamClient, err := app.CreateViamClientWithAPIKey(
		ctx, app.Options{}, apiKey, apiKeyID, logger)
	if err != nil {
		logger.Fatal(err)
	}
	defer viamClient.Close()

	machine, err := client.New(
		context.Background(),
		machineAddress,
		logger,
		client.WithDialOptions(client.WithEntityCredentials(
			apiKeyID,
			client.Credentials{
				Type:    client.CredentialsTypeAPIKey,
				Payload: apiKey,
			})),
	)

	if err != nil {
		logger.Fatal(err)
	}

	dataClient := viamClient.DataClient()

	data, err := dataClient.BinaryDataByIDs(ctx, []string{binaryDataID})
	if err != nil {
		logger.Fatal(err)
	}
	binaryData := data[0]

	// Convert binary data to a named image
	img, err := camera.NamedImageFromBytes(binaryData.Binary, "camera", "image/jpeg", rdkdata.Annotations{})
	if err != nil {
		logger.Fatal(err)
	}

	// Get classifications using the image
	classifier, err := vision.FromProvider(machine, classifierName)
	if err != nil {
		logger.Fatal(err)
	}

	classifications, err := classifier.Classifications(ctx, &img, 2, nil)
	if err != nil {
		logger.Fatal(err)
	}

    if len(classifications) == 0 {
        logger.Fatal(err)
    } else {
        for _, classification := range classifications {
			err := dataClient.AddTagsToBinaryDataByIDs(ctx, []string{classification.Label()}, []string{binaryDataID})
			if err != nil {
				logger.Fatal(err)
			}
			fmt.Printf("Added tag to image: %s\n", classification.Label())
		}
	}

}
```

### TypeScript

```ts
import { createViamClient, createRobotClient, RobotClient, VisionClient } from "@viamrobotics/sdk";

// Configuration constants – replace with your actual values
let API_KEY = "";  // API key, find or create in your organization settings
let API_KEY_ID = "";  // API key ID, find or create in your organization settings
let MACHINE_ADDRESS = "";  // the address of the machine you want to capture images from
let CLASSIFIER_NAME = "";  // the name of the classifier you want to use
let BINARY_DATA_ID = "";  // the ID of the image you want to label

async function connect(): Promise<any> {
    // Establish a connection to the Viam client using API credentials
    return await createViamClient({
        credentials: {
            type: "api-key",
            authEntity: API_KEY_ID,
            payload: API_KEY,
        },
    });
}

async function connectMachine(): Promise<RobotClient> {
    // Establish a connection to the robot using the machine address
    return await createRobotClient({
        host: MACHINE_ADDRESS,
        credentials: {
          type: 'api-key',
          payload: API_KEY,
          authEntity: API_KEY_ID,
        },
        signalingAddress: 'https://app.viam.com:443',
      });
}

async function main(): Promise<number> {
    const viamClient = await connect();
    const dataClient = viamClient.dataClient;
    const machine = await connectMachine();
    const classifier = new VisionClient(machine, CLASSIFIER_NAME);

    // Get image from data in Viam
    const data = await dataClient.binaryDataByIds([BINARY_DATA_ID]);
    const binaryData = data[0];

    // Convert binary data to image
    const image = binaryData.binary; // This should be Uint8Array

    // Get tags using the image
    const tags = await classifier.getClassifications(
        image,
        binaryData.metadata.captureMetadata.width ?? 0,
        binaryData.metadata.captureMetadata.height ?? 0,
        binaryData.metadata.captureMetadata.mimeType ?? "",
        2
    );

    if (tags.length === 0) {
        console.log("No tags found");
        return 1;
    } else {
        for (const tag of tags) {
            await dataClient.addTagsToBinaryDataByIds(
                [tag.className ?? ""],
                [BINARY_DATA_ID]
            );
            console.log(`Added tag to image: ${tag.className}`);
        }
    }

    return 0;
}

main().catch((error) => {
    console.error("Script failed:", error);
    process.exit(1);
});
```



## Programmatic bounding boxes with SDKs

Use an ML model to generate bounding boxes for images, then pass each bounding
box and image ID to the data client API.




### Python

```python
import asyncio

from viam.rpc.dial import DialOptions, Credentials
from viam.app.viam_client import ViamClient
from viam.media.video import ViamImage
from viam.robot.client import RobotClient
from viam.services.vision import VisionClient
from grpclib.exceptions import GRPCError

# Configuration constants – replace with your actual values
API_KEY = ""  # API key, find or create in your organization settings
API_KEY_ID = ""  # API key ID, find or create in your organization settings
MACHINE_ADDRESS = ""  # the address of the machine you want to capture images from
DETECTOR_NAME = ""  # the name of the detector you want to use
BINARY_DATA_ID = ""  # the ID of the image you want to label

async def connect() -> ViamClient:
    """Establish a connection to the Viam client using API credentials."""
    dial_options = DialOptions(
        credentials=Credentials(
            type="api-key",
            payload=API_KEY,
        ),
        auth_entity=API_KEY_ID
    )
    return await ViamClient.create_from_dial_options(dial_options)

async def connect_machine() -> RobotClient:
    """Establish a connection to the robot using the robot address."""
    machine_opts = RobotClient.Options.with_api_key(
        api_key=API_KEY,
        api_key_id=API_KEY_ID
    )
    return await RobotClient.at_address(MACHINE_ADDRESS, machine_opts)

async def main() -> int:
    viam_client = await connect()
    data_client = viam_client.data_client
    machine = await connect_machine()

    detector = VisionClient.from_robot(machine, DETECTOR_NAME)

    # Get image from data in Viam
    data = await data_client.binary_data_by_ids([BINARY_DATA_ID])
    binary_data = data[0]

    # Convert binary data to ViamImage
    image = ViamImage(binary_data.binary, binary_data.metadata.capture_metadata.mime_type)

    # Get detections using the image
    detections = await detector.get_detections(
        image=image, image_format=binary_data.metadata.capture_metadata.mime_type)

    if not len(detections):
        print("No detections found")
        return 1
    else:
        for detection in detections:
            # Ensure bounding box is big enough to be useful
            if detection.x_max_normalized - detection.x_min_normalized <= 0.01 or \
                detection.y_max_normalized - detection.y_min_normalized <= 0.01:
                    continue
            bbox_id = await data_client.add_bounding_box_to_image_by_id(
                binary_id=BINARY_DATA_ID,
                label=detection.class_name,
                x_min_normalized=detection.x_min_normalized,
                y_min_normalized=detection.y_min_normalized,
                x_max_normalized=detection.x_max_normalized,
                y_max_normalized=detection.y_max_normalized
            )
            print(f"Added bounding box to image: {bbox_id}")

    viam_client.close()
    await machine.close()

    return 0

if __name__ == "__main__":
    asyncio.run(main())
```

### Go

```go
package main

import (
	"context"
	"fmt"

	"go.viam.com/rdk/app"
	"go.viam.com/rdk/components/camera"
	rdkdata "go.viam.com/rdk/data"
	"go.viam.com/rdk/logging"
	"go.viam.com/rdk/robot/client"
	"go.viam.com/rdk/services/vision"
)

func main() {
	apiKey := ""
	apiKeyID := ""
	machineAddress := ""
	detectorName := ""
	binaryDataID := ""

	logger := logging.NewDebugLogger("client")
	ctx := context.Background()

	viamClient, err := app.CreateViamClientWithAPIKey(
		ctx, app.Options{}, apiKey, apiKeyID, logger)
	if err != nil {
		logger.Fatal(err)
	}
	defer viamClient.Close()

	machine, err := client.New(
		context.Background(),
		machineAddress,
		logger,
		client.WithDialOptions(client.WithEntityCredentials(
			apiKeyID,
			client.Credentials{
				Type:    client.CredentialsTypeAPIKey,
				Payload: apiKey,
			})),
	)
	if err != nil {
		logger.Fatal(err)
	}

	dataClient := viamClient.DataClient()

	detector, err := vision.FromProvider(machine, detectorName)
	if err != nil {
		logger.Fatal(err)
	}

	data, err := dataClient.BinaryDataByIDs(ctx, []string{binaryDataID})
	if err != nil {
		logger.Fatal(err)
	}
	binaryData := data[0]

	// Convert binary data to a named image
	img, err := camera.NamedImageFromBytes(binaryData.Binary, "camera", "image/jpeg", rdkdata.Annotations{})
	if err != nil {
		logger.Fatal(err)
	}

	// Get detections using the image
	detections, err := detector.Detections(ctx, &img, nil)
	if err != nil {
		logger.Fatal(err)
	}

    if len(detections) == 0 {
        logger.Fatal(err)
    } else {
        for _, detection := range detections {
            // Ensure bounding box is big enough to be useful
			if float64(detection.NormalizedBoundingBox()[2]-detection.NormalizedBoundingBox()[0]) <= 0.01 ||
				float64(detection.NormalizedBoundingBox()[3]-detection.NormalizedBoundingBox()[1]) <= 0.01 {
				continue
			}
			bboxID, err := dataClient.AddBoundingBoxToImageByID(
				ctx,
				binaryDataID,
				detection.Label(),
				float64(detection.NormalizedBoundingBox()[0]),
				float64(detection.NormalizedBoundingBox()[1]),
				float64(detection.NormalizedBoundingBox()[2]),
				float64(detection.NormalizedBoundingBox()[3]),
			)
			if err != nil {
				logger.Fatal(err)
			}
			fmt.Printf("Added bounding box to image: %s\n", bboxID)
		}
	}

}
```

### TypeScript

```ts
import { createViamClient, createRobotClient, RobotClient, VisionClient } from "@viamrobotics/sdk";

// Configuration constants – replace with your actual values
let API_KEY = "";  // API key, find or create in your organization settings
let API_KEY_ID = "";  // API key ID, find or create in your organization settings
let MACHINE_ADDRESS = "";  // the address of the machine you want to capture images from
let DETECTOR_NAME = "";  // the name of the detector you want to use
let BINARY_DATA_ID = "";  // the ID of the image you want to label

async function connect(): Promise<any> {
    // Establish a connection to the Viam client using API credentials
    return await createViamClient({
        credentials: {
            type: "api-key",
            authEntity: API_KEY_ID,
            payload: API_KEY,
        },
    });
}

async function connectMachine(): Promise<RobotClient> {
    // Establish a connection to the robot using the robot address
    return await createRobotClient({
        host: MACHINE_ADDRESS,
        credentials: {
          type: 'api-key',
          payload: API_KEY,
          authEntity: API_KEY_ID,
        },
        signalingAddress: 'https://app.viam.com:443',
      });
}

async function main(): Promise<number> {
    const viamClient = await connect();
    const dataClient = viamClient.dataClient;
    const machine = await connectMachine();
    const detector = new VisionClient(machine, DETECTOR_NAME);

    // Get image from data in Viam
    const data = await dataClient.binaryDataByIds([BINARY_DATA_ID]);
    const binaryData = data[0];

    // Convert binary data to image
    const image = binaryData.binary; // This should be Uint8Array

    // Get detections using the image
    const detections = await detector.getDetections(
        image,
        binaryData.metadata.captureMetadata.width ?? 0,
        binaryData.metadata.captureMetadata.height ?? 0,
        binaryData.metadata.captureMetadata.mimeType ?? ""
    );

    if (detections.length === 0) {
        console.log("No detections found");
        return 1;
    } else {
        for (const detection of detections) {
            // Ensure bounding box is big enough to be useful
            if (detection.xMaxNormalized - detection.xMinNormalized <= 0.01 ||
                detection.yMaxNormalized - detection.yMinNormalized <= 0.01) {
                continue;
            }
            const bboxId = await dataClient.addBoundingBoxToImageById(
                BINARY_DATA_ID,
                detection.className,
                detection.xMinNormalized,
                detection.yMinNormalized,
                detection.xMaxNormalized,
                detection.yMaxNormalized
            );
            console.log(`Added bounding box to image: ${bboxId}`);
        }
    }

    return 0;
}

main().catch((error) => {
    console.error("Script failed:", error);
    process.exit(1);
});
```



## Capture, annotate, and add to dataset in one script

The following example captures an image, uses an ML model to generate
annotations, and adds the image to a dataset -- all in a single script. Use
this pattern to expand and improve your datasets continuously over time.
Check annotation accuracy in the **DATA** tab, then retrain your ML model on
the improved dataset.




### Python

```python
import asyncio
import time

from datetime import datetime
from viam.rpc.dial import DialOptions, Credentials
from viam.app.viam_client import ViamClient
from viam.components.camera import Camera
from viam.media.video import ViamImage
from viam.robot.client import RobotClient
from viam.services.vision import VisionClient

# Configuration constants – replace with your actual values
API_KEY = ""  # API key, find or create in your organization settings
API_KEY_ID = ""  # API key ID, find or create in your organization settings
DATASET_ID = ""  # the ID of the dataset you want to add the image to
MACHINE_ADDRESS = ""  # the address of the machine you want to capture images from
CLASSIFIER_NAME = ""  # the name of the classifier you want to use
CAMERA_NAME = ""  # the name of the camera you want to capture images from
PART_ID = ""  # the part ID of the machine part that captured the images

async def connect() -> ViamClient:
    """Establish a connection to the Viam client using API credentials."""
    dial_options = DialOptions(
        credentials=Credentials(
            type="api-key",
            payload=API_KEY,
        ),
        auth_entity=API_KEY_ID
    )
    return await ViamClient.create_from_dial_options(dial_options)

async def connect_machine() -> RobotClient:
    """Establish a connection to the robot using the robot address."""
    machine_opts = RobotClient.Options.with_api_key(
        api_key=API_KEY,
        api_key_id=API_KEY_ID
    )
    return await RobotClient.at_address(MACHINE_ADDRESS, machine_opts)

async def main() -> int:
    viam_client = await connect()
    data_client = viam_client.data_client
    machine = await connect_machine()

    camera = Camera.from_robot(machine, CAMERA_NAME)
    classifier = VisionClient.from_robot(machine, CLASSIFIER_NAME)

    # Capture image
    images, _ = await camera.get_images()
    image_frame = images[0]

    # Upload data
    file_id = await data_client.binary_data_capture_upload(
        part_id=PART_ID,
        component_type="camera",
        component_name=CAMERA_NAME,
        method_name="GetImages",
        data_request_times=[datetime.utcnow(), datetime.utcnow()],
        file_extension=".jpg",
        binary_data=image_frame.data
    )
    print(f"Uploaded image: {file_id}")

    # Annotate image
    await data_client.add_tags_to_binary_data_by_ids(
        tags=["test"],
        binary_ids=[file_id]
    )

    # Get image from data in Viam
    data = await data_client.binary_data_by_ids([file_id])
    binary_data = data[0]

    # Convert binary data to ViamImage
    image = ViamImage(binary_data.binary, binary_data.metadata.capture_metadata.mime_type)

    # Get tags using the image
    tags = await classifier.get_classifications(
        image=image, image_format=binary_data.metadata.capture_metadata.mime_type, count=2)

    if not len(tags):
        print("No tags found")
        return 1

    for tag in tags:
        await data_client.add_tags_to_binary_data_by_ids(
            tags=[tag.class_name],
            binary_ids=[file_id]
        )
        print(f"Added tag to image: {tag}")

    print("Adding image to dataset...")
    await data_client.add_binary_data_to_dataset_by_ids(
        binary_ids=[file_id],
        dataset_id=DATASET_ID
    )
    print(f"Added image to dataset: {file_id}")

    viam_client.close()
    await machine.close()
    return 0

if __name__ == "__main__":
    asyncio.run(main())
```

### Go

```go
package main

import (
	"context"
	"fmt"
	"time"

	"go.viam.com/rdk/app"
	"go.viam.com/rdk/logging"
	"go.viam.com/rdk/robot/client"
	"go.viam.com/rdk/services/vision"
	"go.viam.com/rdk/components/camera"
)

func main() {
	apiKey := ""
	apiKeyID := ""
	datasetID := ""
	machineAddress := ""
	classifierName := ""
	cameraName := ""
	partID := ""

	logger := logging.NewDebugLogger("client")
	ctx := context.Background()

	viamClient, err := app.CreateViamClientWithAPIKey(
		ctx, app.Options{}, apiKey, apiKeyID, logger)
	if err != nil {
		logger.Fatal(err)
	}
	defer viamClient.Close()

	machine, err := client.New(
		context.Background(),
		machineAddress,
		logger,
		client.WithDialOptions(client.WithEntityCredentials(
			apiKeyID,
			client.Credentials{
				Type:    client.CredentialsTypeAPIKey,
				Payload: apiKey,
			})),
	)
	if err != nil {
		logger.Fatal(err)
	}

	// Capture image from camera
	cam, err := camera.FromProvider(machine, cameraName)
	if err != nil {
		logger.Fatal(err)
	}

	images, _, err := cam.Images(ctx, nil, nil)
	if err != nil {
		logger.Fatal(err)
	}
	image := images[0]
	imageData, err := image.Bytes(ctx)
	if err != nil {
		logger.Fatal(err)
	}

	dataClient := viamClient.DataClient()

	// Upload image to Viam
	binaryDataID, err := dataClient.BinaryDataCaptureUpload(
		ctx,
		imageData,
		partID,
		"camera",
		cameraName,
		"GetImages",
		".jpg",
		&app.BinaryDataCaptureUploadOptions{
			DataRequestTimes: &[2]time.Time{time.Now(), time.Now()},
		},
	)

	fmt.Printf("Uploaded image: %s\n", binaryDataID)

	// Get classifications using the image
	classifier, err := vision.FromProvider(machine, classifierName)
	if err != nil {
		logger.Fatal(err)
	}

	classifications, err := classifier.Classifications(ctx, &image, 2, nil)
	if err != nil {
		logger.Fatal(err)
	}

    if len(classifications) == 0 {
        logger.Fatal(err)
    } else {
        for _, classification := range classifications {
			err := dataClient.AddTagsToBinaryDataByIDs(ctx, []string{classification.Label()}, []string{binaryDataID})
			if err != nil {
				logger.Fatal(err)
			}
			fmt.Printf("Added tag to image: %s\n", classification.Label())
		}
	}

	// Add image to dataset
	err = dataClient.AddBinaryDataToDatasetByIDs(ctx, []string{binaryDataID}, datasetID)
	if err != nil {
		logger.Fatal(err)
	}
	fmt.Printf("Added image to dataset: %s\n", binaryDataID)

}
```

### TypeScript

```ts
import { createViamClient, createRobotClient, RobotClient, VisionClient, CameraClient } from "@viamrobotics/sdk";

// Configuration constants – replace with your actual values
let API_KEY = "";  // API key, find or create in your organization settings
let API_KEY_ID = "";  // API key ID, find or create in your organization settings
let DATASET_ID = "";  // the ID of the dataset you want to add the image to
let MACHINE_ADDRESS = "";  // the address of the machine you want to capture images from
let CLASSIFIER_NAME = "";  // the name of the classifier you want to use
let CAMERA_NAME = "";  // the name of the camera you want to capture images from
let PART_ID = "";  // the part ID of the machine part that captured the images

async function connect(): Promise<any> {
    // Establish a connection to the Viam client using API credentials
    return await createViamClient({
        credentials: {
            type: "api-key",
            authEntity: API_KEY_ID,
            payload: API_KEY,
        },
    });
}

async function connectMachine(): Promise<RobotClient> {
    // Establish a connection to the robot using the machine address
    return await createRobotClient({
        host: MACHINE_ADDRESS,
        credentials: {
          type: 'api-key',
          payload: API_KEY,
          authEntity: API_KEY_ID,
        },
        signalingAddress: 'https://app.viam.com:443',
      });
}

async function main(): Promise<number> {
    const viamClient = await connect();
    const dataClient = viamClient.dataClient;
    const machine = await connectMachine();
    const camera = new CameraClient(machine, CAMERA_NAME);
    const classifier = new VisionClient(machine, CLASSIFIER_NAME);

    // Capture image
    const {images, metadata} = await camera.getImages();
    const imageFrame = images[0].image;

    // Upload data
    const fileId = await dataClient.binaryDataCaptureUpload(
        imageFrame,
        PART_ID,
        "camera",
        CAMERA_NAME,
        "GetImages",
        ".jpg",
        [new Date(), new Date()]
    );
    console.log(`Uploaded image: ${fileId}`);

    // Annotate image
    await dataClient.addTagsToBinaryDataByIds(
        ["test"],
        [fileId]
    );

    // Get image from data in Viam
    const data = await dataClient.binaryDataByIds([fileId]);
    const binaryData = data[0];

    // Convert binary data to image
    const image = binaryData.binary; // This should be Uint8Array

    // Get tags using the image
    const tags = await classifier.getClassifications(
        image,
        binaryData.metadata.captureMetadata.width ?? 0,
        binaryData.metadata.captureMetadata.height ?? 0,
        binaryData.metadata.captureMetadata.mimeType ?? "",
        2
    );

    if (tags.length === 0) {
        console.log("No tags found");
        return 1;
    }

    for (const tag of tags) {
        await dataClient.addTagsToBinaryDataByIds(
            [tag.className ?? ""],
            [fileId]
        );
        console.log(`Added tag to image: ${tag}`);
    }

    console.log("Adding image to dataset...");
    await dataClient.addBinaryDataToDatasetByIds(
        [fileId],
        DATASET_ID
    );
    console.log(`Added image to dataset: ${fileId}`);

    return 0;
}

main().catch((error) => {
    console.error("Script failed:", error);
    process.exit(1);
});
```



## What's next

- [Train a model](/train/train-a-model/) -- use your labeled dataset to
  train a classification or object detection model.

