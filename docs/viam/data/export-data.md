# Export data

Download data from Viam using the data client API or the CLI.
> Source: https://docs.viam.com/data/export-data/ · Last updated: 2025-09-12


You can download machine data to your computer with the Viam CLI.

If you prefer to manage your data with code, see the [data client API documentation](/reference/apis/data-client/).

## Prerequisites

**Install the Viam CLI and authenticate**


Install the Viam CLI using the option below that matches your system architecture:

{{< tabs >}}
{{% tab name="macOS" %}}

To download the Viam CLI on a macOS computer, install [brew](https://brew.sh/) and run the following commands:

```sh {class="command-line" data-prompt="$"}
brew trust viamrobotics/brews
brew tap viamrobotics/brews
brew install viam
```

{{% /tab %}}
{{% tab name="Linux aarch64" %}}

On Debian-based distributions (Debian, Ubuntu, Raspberry Pi OS 64-bit), install the Viam CLI from Viam's apt repository so `apt upgrade` keeps it up to date:

```sh {class="command-line" data-prompt="$"}
curl -fsSL https://us-apt.pkg.dev/doc/repo-signing-key.gpg | sudo gpg --dearmor -o /usr/share/keyrings/viam.gpg
echo "deb [signed-by=/usr/share/keyrings/viam.gpg] https://us-apt.pkg.dev/projects/static-file-server-310021 viam main" | sudo tee /etc/apt/sources.list.d/viam.list
sudo apt update && sudo apt install viam-cli
```

The package is named `viam-cli`; the installed command is `viam` (a `viam-cli` alias also works).

On other distributions, download the binary directly:

```sh {class="command-line" data-prompt="$"}
sudo curl --compressed -o /usr/local/bin/viam https://storage.googleapis.com/packages.viam.com/apps/viam-cli/viam-cli-stable-linux-arm64
sudo chmod a+rx /usr/local/bin/viam
```

{{% /tab %}}
{{% tab name="Linux x86_64" %}}

On Debian-based distributions (Debian, Ubuntu), install the Viam CLI from Viam's apt repository so `apt upgrade` keeps it up to date:

```sh {class="command-line" data-prompt="$"}
curl -fsSL https://us-apt.pkg.dev/doc/repo-signing-key.gpg | sudo gpg --dearmor -o /usr/share/keyrings/viam.gpg
echo "deb [signed-by=/usr/share/keyrings/viam.gpg] https://us-apt.pkg.dev/projects/static-file-server-310021 viam main" | sudo tee /etc/apt/sources.list.d/viam.list
sudo apt update && sudo apt install viam-cli
```

The package is named `viam-cli`; the installed command is `viam` (a `viam-cli` alias also works).

On other distributions, download the binary directly:

```sh {class="command-line" data-prompt="$"}
sudo curl --compressed -o /usr/local/bin/viam https://storage.googleapis.com/packages.viam.com/apps/viam-cli/viam-cli-stable-linux-amd64
sudo chmod a+rx /usr/local/bin/viam
```

{{% /tab %}}
{{% tab name="Windows" %}}

[Download the binary](https://storage.googleapis.com/packages.viam.com/apps/viam-cli/viam-cli-stable-windows-amd64.exe) and run it directly to use the Viam CLI on a Windows computer.

{{% /tab %}}
{{% tab name="Source" %}}

If you have [Go installed](https://go.dev/doc/install), you can build the Viam CLI from source. Clone the repository and build it with `make`:

```sh {class="command-line" data-prompt="$"}
git clone --depth 1 https://github.com/viamrobotics/rdk.git
cd rdk
make cli
sudo cp "bin/$(go env GOOS)-$(go env GOARCH)/viam-cli" /usr/local/bin/viam
```

To confirm `viam` is installed and ready to use, run `viam version` from your terminal.

{{< alert title="Why not `go install`?" color="caution" >}}
The RDK module replaces one of its dependencies, and Go refuses `go install <package>@<version>` for a module carrying replace directives.
{{< /alert >}}

{{% /tab %}}
{{< /tabs >}}

For more information see [install the Viam CLI](/cli/).


Then authenticate your CLI session with Viam using one of the following options:

{{< tabs >}}
{{% tab name="Personal access token" %}}

```sh {class="command-line" data-prompt="$"}
viam login
```

This will open a new browser window with a prompt to start the authentication process. If a browser window does not open, the CLI will present a URL for you to manually open in your browser. Follow the instructions to complete the authentication process.

{{% /tab %}}
{{% tab name="API key" %}}

Use your organization, location, or machine part API key and corresponding API key ID in the following command:

```sh {class="command-line" data-prompt="$"}
viam login api-key --key-id <api-key-id> --key <organization-api-key-secret>
```

{{% /tab %}}
{{< /tabs >}}





## Export data with the Viam CLI

To export your data from the cloud using the Viam CLI:


### Step 1

**Filter the data you want to download**

Navigate to the [**DATA**](https://app.viam.com/data/all) page.

Use the filters on the left side of the page to filter the data you wish to export.

### Step 2

**Copy the export command from the DATA page**

In the upper right corner of the **DATA** page, click the **Export** button.

Click **Copy export command**.
This copies the command, including your org ID and the filters you selected, to your clipboard.

### Step 3

**Run the command**

Run the copied command in a terminal:

<h3 id="binary-data" class="main-content-heading">
    Binary data
    
</h3>
```sh
viam data export binary filter --org-ids=<org-id> --destination=.
```
By default, the command creates two new directories named `data` and `metadata` in the destination directory.
It downloads binary files into the `data` folder and metadata (bounding box information, labels) in JSON format into the `metadata` folder.

Since data is downloaded in parallel, the order is not guaranteed to be chronological.
Sort your files by filename to see them in chronological order.

<h3 id="tabular-data" class="main-content-heading">
    Tabular data
    
</h3>
```sh
viam data export tabular --destination=. --part-id=<part-id> --resource-name=<resource-name> --resource-subtype=<resource-subtype> --method=<method>
```
The tabular export command writes a single `data.ndjson` file in [NDJSON](https://github.com/ndjson/ndjson-spec) (newline-delimited JSON) format to the destination directory.

If you want to store the data in a different location, change the destination with the [`--destination` flag](/cli/).



You can see more information about exporting data in the [Viam CLI documentation](/cli/).

