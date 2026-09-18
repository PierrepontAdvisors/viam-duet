# Set up machines with the CLI

Create and connect machines from the command line.
> Source: https://docs.viam.com/set-up-a-machine/with-cli/


Create and connect a machine to the Viam platform from the command line, instead of clicking through the Viam app.

You'll need:

- An organization and a location in the Viam app. New to Viam? Use [Set up your first machine](/set-up-a-machine/first-machine/) to create them, then come back.
- An API key for the CLI. See [Manage API keys](/cli/administer-your-organization/#manage-api-keys).
- A Linux or macOS device to run `viam-agent`. For Windows or ESP32, use [Set up your first machine](/set-up-a-machine/first-machine/).

## 1. Install and authenticate the CLI

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


In a script, authenticate with an API key:

```sh {class="command-line" data-prompt="$"}
viam login api-key --key-id=<key-id> --key=<key>
```

## 2. Create the machine

```sh {class="command-line" data-prompt="$"}
viam machines create --name=my-first-machine --location=<location-id>
```

The CLI prints the new machine's ID:

```sh {class="command-line" data-prompt="$" data-output="1"}
created new machine with id abc12345-1234-abcd-5678-ef1234567890
```

To find your location ID:

```sh {class="command-line" data-prompt="$"}
viam locations list
```

## 3. Get the part ID

Every machine has at least one part. To install `viam-agent` on the device, you need the part ID:

```sh {class="command-line" data-prompt="$"}
viam machines part list --machine=<machine-id>
```

## 4. Install viam-agent on the device

On the compute device that will run the machine, run:

```sh {class="command-line" data-prompt="$"}
sudo /bin/sh -c "VIAM_API_KEY_ID=<key-id> VIAM_API_KEY=<key> VIAM_PART_ID=<part-id>; $(curl -fsSL https://storage.googleapis.com/packages.viam.com/apps/viam-agent/install.sh)"
```

The install script downloads `viam-agent`, fetches the machine's cloud config to `/etc/viam.json` using the credentials above, and starts the agent service.

## 5. Verify the machine is online

```sh {class="command-line" data-prompt="$"}
viam machines status --machine=<machine-id>
```

If the machine is connected, the CLI prints its part list and status. If not, see [Troubleshoot problems](/monitor/troubleshoot/).

## 6. Apply a baseline configuration (optional)

If you have a fragment defining your standard component setup, attach it to the machine's main part:

```sh {class="command-line" data-prompt="$"}
viam machines part fragments add --part=<part-id> --fragment=<fragment-name-or-id>
```

See [Reuse machine configuration](/fleet/reuse-configuration/) for the fragment authoring workflow.

## Set up multiple machines

The pattern above handles one machine. To do this for many machines, wrap steps 2-6 in a script. See [Automate with scripts](/cli/automate-with-scripts/#provisioning-create-and-configure-a-machine) for a complete provisioning script.

## What's next

- [Configure hardware](/hardware/configure-hardware/) to add components and services.
- [Reuse machine configuration](/fleet/reuse-configuration/) to author the fragments your machines apply.
- [Automate with scripts](/cli/automate-with-scripts/) for bulk operations and CI/CD.

