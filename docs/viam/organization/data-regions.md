# Choose data region

Configure where in the world Viam stores your cloud data.
> Source: https://docs.viam.com/organization/data-regions/


When you specify a data region, Viam stores all data captured by your machines in that region.
This includes sensor readings, images, and other captured data.
Choosing the right region helps you meet data residency requirements and can reduce latency for data queries.

By default, new organizations store data in North America.
Locations shared across multiple organizations store data in the primary organization's region.

## Supported regions

Viam supports the following data regions:

- **North America** (`us-central`): Data is stored in Google Cloud Platform's `us-central1` region. This is the default for new organizations.
- **Europe** (`eu-west`): Data is stored in Google Cloud Platform's `europe-west4` region. Choose this region if you need to keep data within the EU to meet GDPR or other data residency requirements.

## Set organization data region

> **Caution: You cannot change region if you have already synced data:**
> 
> 
> 
> You must set the region before syncing data.
> Once you sync data in an organization, you cannot change the data region.
> 
> 




### Web UI

<ol>
<li>Open the organization dropdown in the top right of Viam, next to your initials.</li>
<li>Click **Settings and invites** to open the organization settings menu.</li>
<li>From the **Data region** dropdown, choose the geographic location where you would like to store data.</li>
<li>A dialog will appear at the bottom of the screen containing the text **Region updated**.</li>
</ol>

### Python

You can check your organization’s data region using [`get_organization`](/reference/apis/fleet/), and set your organization’s data region using [`update_organization`](/reference/apis/fleet/):

```python
import asyncio
import os

from viam.rpc.dial import DialOptions, Credentials
from viam.app.viam_client import ViamClient

# Configuration constants – replace with your actual values
API_KEY = ""  # API key, find or create in your organization settings
API_KEY_ID = ""  # API key ID, find or create in your organization settings
ORG_ID = ""  # Organization ID, find or create in your organization settings

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

async def main() -> int:
    async with await connect() as viam_client:
        # Check organization region
        org = await viam_client.app_client.get_organization(org_id=ORG_ID)
        print(f"Current region: {org.default_region}")

        # Update organization region
        try:
            updated_org = await viam_client.app_client.update_organization(
                org_id=ORG_ID,
                region="us-central"  # or "us-central"
            )
            print(f"Organization region updated to: {updated_org.default_region}")
        except Exception as e:
            print(f"Error updating organization region: {e}")

        return 0

if __name__ == "__main__":
    asyncio.run(main())
```

### Go

You can check your organization’s data region using [`GetOrganization`](/reference/apis/fleet/), and set your organization’s data region using [`UpdateOrganization`](/reference/apis/fleet/):

```python
package main

import (
	"context"
	"fmt"

	"go.viam.com/rdk/app"
	"go.viam.com/rdk/logging"
)

func main() {
	apiKey := ""
	apiKeyID := ""
	orgID := ""

	logger := logging.NewDebugLogger("client")
	ctx := context.Background()
	viamClient, err := app.CreateViamClientWithAPIKey(
		ctx, app.Options{}, apiKey, apiKeyID, logger)
	if err != nil {
		logger.Fatal(err)
	}
	defer viamClient.Close()

	// Get the app client from the viam client
	appClient := viamClient.AppClient()

	// Check organization region
	org, err := appClient.GetOrganization(ctx, orgID)
	if err != nil {
		logger.Fatal(err)
	}
	fmt.Printf("Current region: %s\n", org.DefaultRegion)

	// Configure UpdateOrganizationOptions for European region
	newRegion := "eu-west"  // or "us-central"
	updateOptions := &app.UpdateOrganizationOptions{
		Name:   nil,
		Region: &newRegion,
	}

	// Update organization region
	updatedOrg, err := appClient.UpdateOrganization(ctx, orgID, updateOptions)
	if err != nil {
		logger.Fatal(err)
	}

	fmt.Printf("Organization region updated to: %s\n", updatedOrg.DefaultRegion)

}
```

### TypeScript

You can check your organization’s data region using [`getOrganization`](/reference/apis/fleet/), and set your organization’s data region using [`UpdateOrganization`](/reference/apis/fleet/):

```python
import { createViamClient } from "@viamrobotics/sdk";

// Configuration constants – replace with your actual values
let API_KEY = "";  // API key, find or create in your organization settings
let API_KEY_ID = "";  // API key ID, find or create in your organization settings
let ORG_ID = "";  // Organization ID, find or create in your organization settings

async function main(): Promise<void> {
    // Create Viam client
    const client = await createViamClient({
        credentials: {
            type: "api-key",
            authEntity: API_KEY_ID,
            payload: API_KEY,
        },
    });

    // Check organization region
    const org = await client.appClient.getOrganization(ORG_ID);
    console.log(`Current region: ${org.defaultRegion}`);

    // Update organization region
    try {
        const updatedOrg = await client.appClient.updateOrganization(ORG_ID, "us-central");
        console.log(`Organization region updated to: ${updatedOrg?.defaultRegion}`);
    } catch (e) {
        console.log(`Error updating organization region: ${e}`);
    }
}

// Run the script
main().catch((error) => {
    console.error("Script failed:", error);
    process.exit(1);
});
```



