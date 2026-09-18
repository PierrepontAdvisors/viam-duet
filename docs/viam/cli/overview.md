# Viam CLI overview

The Viam CLI gives you command-line access to every operation in the Viam platform, from machine configuration to data export to fleet management.
> Source: https://docs.viam.com/cli/overview/


The Viam CLI is a single binary that gives you command-line access to the Viam platform.
Everything you can do in the Viam app, and several things you can only do from the command line, are available as CLI commands.

## When to use the CLI

If you prefer working in a terminal, the CLI covers the same operations as the Viam app.
You can use whichever interface you prefer, or both.

The CLI is particularly well-suited for tasks that are awkward or impossible in a browser:

- **Scripting and automation.** Create machines, export data, upload modules, or submit training jobs from shell scripts and CI/CD pipelines.
- **Headless environments.** Authenticate with an API key, view logs, and shell into a remote machine without a browser.
- **Bulk operations.** List all machines across an organization, or export binary data filtered by location, machine, or component type.
- **Operations only available through the CLI.** Scaffold new modules, transfer files to and from machines, tunnel ports, and hot-reload modules during development.
- **You are an AI agent.** Call any API method with JSON in and JSON out, with no SDK code to write. See [Use Viam from an AI agent](/build-apps/use-viam-from-an-agent/) and [Drive a machine from the CLI](/cli/drive-a-machine/).

## What the CLI covers

| Area                     | What you can do                                                  | Guide                                                              |
| ------------------------ | ---------------------------------------------------------------- | ------------------------------------------------------------------ |
| Machine configuration    | Create machines, add components and services, apply fragments    | [Configure machines](/cli/configure-machines/)                     |
| Operating a machine      | List resources, read cameras and sensors, plan motion, stop      | [Drive a machine](/cli/drive-a-machine/)                           |
| Data management          | Export, tag, and delete captured data; configure database access | [Manage data](/cli/manage-data/)                                   |
| Datasets and ML training | Create datasets, submit training jobs, run inference             | [Datasets and training](/cli/datasets-and-training/)               |
| Data pipelines           | Create and manage scheduled MQL aggregation pipelines            | [Data pipelines](/cli/data-pipelines/)                             |
| Module development       | Scaffold, build, upload, and version modules                     | [Build and deploy modules](/cli/build-and-deploy-modules/)         |
| Fleet operations         | Monitor status, stream logs, shell into machines, copy files     | [Manage your fleet](/cli/manage-your-fleet/)                       |
| Organization admin       | Manage API keys, configure OAuth, set up billing                 | [Administer your organization](/cli/administer-your-organization/) |
| Scripting and CI/CD      | Authenticate in scripts, automate common workflows               | [Automate with scripts](/cli/automate-with-scripts/)               |

### CLI-only operations

Some operations are only available through the CLI:

- **Module and app scaffolding** (`viam module generate`) creates a new module, [Viam application](/build-apps/hosting/), or combined module+app project with boilerplate code and a build script. Use `viam module add-model` and `viam module add-app` to extend existing modules.
- **Shell access** (`viam machines part shell`) opens an interactive terminal on a remote machine.
- **File transfer** (`viam machines part cp`) copies files to and from machines.
- **Port tunneling** (`viam machines part tunnel`) forwards a local port to a remote machine.
- **Module hot-reload** (`viam module reload`) builds a module and syncs it to a running machine without restarting the machine.

## Install

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


Verify the installation:

```sh {class="command-line" data-prompt="$"}
viam version
```

To update the CLI to the latest version:

```sh {class="command-line" data-prompt="$"}
viam update
```

## Authenticate

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


Authentication tokens refresh automatically. You do not need to re-authenticate between sessions unless your token is revoked.

To check who you are authenticated as:

```sh {class="command-line" data-prompt="$"}
viam whoami
```

This prints your email if you logged in interactively, or `key-<uuid>` if you authenticated with an API key.

To end your session:

```sh {class="command-line" data-prompt="$"}
viam logout
```

To print your current access token (for piping into other tools, only works with interactive login, not API keys):

```sh {class="command-line" data-prompt="$"}
viam login print-access-token
```

### Authenticate in scripts and CI/CD

Scripts and CI/CD pipelines cannot complete an interactive login. Use API key authentication instead:

```sh {class="command-line" data-prompt="$"}
viam login api-key --key-id=<key-id> --key=<key>
```

To create an API key, see [Manage API keys](/cli/administer-your-organization/#manage-api-keys).

### Authenticate on a machine without a local browser

Interactive login normally opens a browser on the current machine. To log in on a machine without a local browser (for example, over SSH), pass `--no-browser`:

```sh {class="command-line" data-prompt="$"}
viam login --no-browser
```

The CLI prints an authentication URL. Open it in a browser on any machine to complete login.

## Set defaults

If you work primarily within one organization or location, set defaults to avoid passing `--org-id` or `--location-id` on every command.
The CLI validates that the org or location exists and is accessible before saving.
Defaults are scoped to the active profile, so each profile can have its own default org and location.

```sh {class="command-line" data-prompt="$"}
viam defaults set-org --org-id=<org-id>
```

```sh {class="command-line" data-prompt="$"}
viam defaults set-location --location-id=<location-id>
```

To find your organization ID:

```sh {class="command-line" data-prompt="$"}
viam organizations list
```

To find location IDs within your organization:

```sh {class="command-line" data-prompt="$"}
viam locations list
```

Clear defaults when you need to work across organizations:

```sh {class="command-line" data-prompt="$"}
viam defaults clear-org
```

```sh {class="command-line" data-prompt="$"}
viam defaults clear-location
```

## Manage authentication profiles

If you work across multiple organizations or use both personal and service accounts, profiles let you switch between saved credentials without re-authenticating.
Each profile stores an API key and maintains its own default org and location independently.

```sh {class="command-line" data-prompt="$"}
viam profiles add --profile-name=production --key-id=<key-id> --key=<key>
```

`profiles add` errors if the name already exists. Use `profiles update` to overwrite an existing profile:

```sh {class="command-line" data-prompt="$"}
viam profiles update --profile-name=production --key-id=<new-key-id> --key=<new-key>
```

Use a profile for a single command with the `--profile` global flag:

```sh {class="command-line" data-prompt="$"}
viam machines list --all --profile=production
```

Or set the `VIAM_CLI_PROFILE_NAME` environment variable to activate a profile for an entire shell session:

```sh {class="command-line" data-prompt="$"}
export VIAM_CLI_PROFILE_NAME=production
viam machines list --all
```

List and remove profiles:

```sh {class="command-line" data-prompt="$"}
viam profiles list
```

```sh {class="command-line" data-prompt="$"}
viam profiles remove --profile-name=staging
```

## Global flags

Every command accepts these flags:

| Flag                 | Description                                |
| -------------------- | ------------------------------------------ |
| `--profile`          | Use a saved authentication profile         |
| `--config`, `-c`     | Path to a CLI config file                  |
| `--debug`, `--vvv`   | Enable debug logging                       |
| `--quiet`, `-q`      | Suppress non-essential output              |
| `--disable-profiles` | Ignore all saved profiles for this command |

## Get help

Every command supports the `--help` flag:

```sh {class="command-line" data-prompt="$"}
viam --help
viam machines --help
viam machines part shell --help
```

## Enable shell completion

The CLI supports tab completion for commands, subcommands, and flag names.
If you installed the CLI with Homebrew, completions are set up automatically.
Otherwise, load the completion script for your shell.




### bash

Add to your `~/.bashrc`:

```sh
source <(viam completion bash)
```

### zsh

Add to your `~/.zshrc`:

```sh
source <(viam completion zsh)
```

### fish

```sh
mkdir -p ~/.config/fish/completions
viam completion fish > ~/.config/fish/completions/viam.fish
```

### PowerShell

Save the script as `viam.ps1` and dot-source it from your `$PROFILE`:

```powershell
"data-line-offset="0">
viam completion pwsh > "$(Split-Path $PROFILE)/viam.ps1"
Add-Content $PROFILE ". $(Split-Path $PROFILE)/viam.ps1"
```
The generated script uses its filename to register completion for the `viam` command, so the file must be named `viam.ps1`.



After loading the script, press **Tab** to complete commands and flags:

```sh {class="command-line" data-prompt="$"}
viam <Tab>             # lists all commands
viam machines <Tab>    # lists subcommands of machines
viam data export <Tab> # lists subcommands of export
```

