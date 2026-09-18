# Odroid C4 Setup Guide

Image a Odroid-C4 to prepare it for viam-server installation.
> Source: https://docs.viam.com/reference/device-setup/odroid-c4-setup/


The [Odroid-C4](https://wiki.odroid.com/odroid-c4/odroid-c4#odroid-c4) is a single-board computer that features an Amlogic S905x3 CPU and runs a variety of Linux or Android distributions.






    
    
    
<picture>

  
  
<source srcset="/installation/thumbnails/odroid-c4_hu_917a87debb80f1a6.webp" type="image/webp" width="350" height="275">
<img src="/installation/thumbnails/odroid-c4.png" width="350" height="275" alt="The Odroid-C4 single-board computer." class="" id="" style="" loading="lazy">
  

</picture>




Follow this guide to set up your Odroid-C4.

## Hardware requirements

- An [Odroid-C4 board](https://www.hardkernel.com/shop/odroid-c4/)
- A 12V/2A power supply
- An ethernet cable and/or USB Wi-Fi dongle, for network connectivity
- A computer, for development
- A microSD card, if you plan to boot from SD instead of eMMC
- (Optional) An HDMI cable, for display

## Power your Odroid C4

Before you power the board, you need to install an operating system.
Visit [Odroid's OS Installation Guide](https://wiki.odroid.com/getting_started/os_installation_guide#os_installation_guide) to choose the right OS for your needs and follow the instructions to flash the OS to your microSD card or eMMC.

To power your Odroid-C4, connect your power adapter to the Odroid-C4's power jack.
The red LED should light up, which indicates that the board is powered.

To connect to a display, connect one end of your HDMI cable to the Odroid and the other end to your monitor.

## Establish a network connection

Plug the Ethernet cable into your Odroid-C4for a wired internet connection.
For a wireless connection, you can connect a USB Wi-Fi dongle and configure Wi-Fi settings through your operating system.

## Access and update your Odroid-C4

To access your Odroid remotely, use an SSH client like [TeraTerm](https://teratermproject.github.io/index-en.html).
You'll also need the IP address of your Odroid-C4 board to connect remotely.
Alternatively, connect a keyboard and mouse to interact with the board directly using a connected monitor.

Once you're connected, open a terminal and run the following commands

```sh {class="command-line" data-prompt="$"}
sudo apt update && sudo apt upgrade
```

## Install `viam-server`

`viam-server` is the open-source software that drives your hardware and connects your device to the cloud.
Install `viam-server` on the computer or single-board computer (SBC) that is directly connected to your hardware (for example sensors, cameras, or motors):

1. Make sure your computer or SBC is powered on and connected to the internet.

1. Create a Viam account on [app.viam.com](https://app.viam.com).
   You can configure and manage devices and data collection in the web UI.

1. Create a new {{< glossary_tooltip term_id="machine" text="machine" >}} using the **Add machine** button in the top right corner of the **LOCATIONS** tab in the app.
   A machine represents your device.

1. On your machine's page, click **Set up**.

1. Select the appropriate architecture for your machine: **Linux / Aarch64**, **Linux / x86_64**, or **Linux / Armv7l**.

   On most Linux operating systems, you can run `uname -m` to confirm your computer's architecture.

   If you selected **Linux / Aarch 64** or **Linux / x86** also select your installation method:

   - `viam-agent` (recommended): installs viam-agent, which will automatically install (and update) viam-server **and** provide additional functionality such as [provisioning](/fleet/provision-devices/) and operating system update configuration.
   - `manual`: installs only `viam-server` on your machine.

1. Follow the instructions on the page to install `viam-server` and connect it to the cloud with your machine’s unique credentials.

1. After you install `viam-server`, a secure connection is automatically established between your machine and Viam.
   When you update your machine's configuration, `viam-server` automatically gets the updates.

   You are ready to [configure supported hardware](/hardware/configure-hardware/) on your machine.


## Try an example

Once you've installed `viam-server` and your machine has come online, if your machine has a webcam, you can try an example project:

1. Click the **+** icon next to your machine part in the left-hand menu and select **Insert Fragment**.

   Add the [`DeskSafariGame` fragment](https://app.viam.com/fragment/0161c5da-48fa-4a23-8e7f-95fb85cfb3f8) by the `Robot Land` organization and click **Insert Fragment**.
   This adds a number of {{< glossary_tooltip term_id="resource" text="resources" >}} to your machine:

   - a camera component which connects to the webcam
   - machine learning resources to run a model and apply it to the camera stream
   - control logic that implements a game

1. **Save** your config and review the available resources on the **CONFIGURE** tab.
1. Log into [this Viam application](https://hello-world-game-web-app_naomi.viamapplications.com/) with your Viam credentials and select your machine.
   The application provides a UI for playing the game
1. Select a camera and press the Start Game button.
   The goal of the game is to find and show specific objects to the camera.

Should the game not work, return to your machine in the Viam web UI and check the **LOGS** tab for errors.


## Next steps

<div class="card-container">
  <div class="row-no-margin">
<div class="col hover-card "><a href="/hardware/configure-hardware/"><div ><div>Overview</div><p>Understand how Viam represents hardware, add components to your machine, and configure them.</p></div>
    </a></div>

<div class="col hover-card "><a href="/try/"><div ><div>Try</div><p>Hands-on guided tutorials to experience Viam end-to-end.</p></div>
    </a></div>

<div class="col hover-card "><a href="/tutorials/"><div ><div>Tutorials</div><p>Browse tutorials that walk through building complete robots and smart machines with Viam.</p></div>
    </a></div>

</div>
</div>

## Troubleshooting

Visit the [Odroid Forum](https://forum.odroid.com/index.php) for troubleshooting tips and tricks specific to the Odroid-C4.

