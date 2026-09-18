# Pumpkin Board Setup Guide

Configure the pin mappings to use a pumpkin board.
> Source: https://docs.viam.com/reference/device-setup/pumpkin/


To use a [Mediatek Genio 500 Pumpkin single-board computer](https://ologicinc.com/portfolio/mediateki500/) with Viam:

1. [Install `viam-server`](/set-up-a-machine/first-machine/) on your machine.
1. [Create a board definitions file](#create-a-board-definitions-file), specifying the mapping between your board's GPIO pins and connected hardware.
1. [Configure a `customlinux` board](#configure-a-customlinux-board) on your machine, specifying the path to the definitions file in the board configuration.

## Create a board definitions file

The board definitions file describes the location of each GPIO pin on the board so that `viam-server` can access the pins correctly.

On your Pumpkin board, create a JSON file in the <file>/home/root</file> directory named <file>board.json</file>, and provide the mappings between your GPIO pins and connected hardware.
Use the template and example below to populate the JSON file with a single key, `"pins"`, whose value is a list of objects that each represent a pin on the board.

```json
{
  "pins": [
    {
      "name": "3",
      "device_name": "gpiochip0",
      "line_number": 81,
      "pwm_id": -1
    },
    {
      "name": "5",
      "device_name": "gpiochip0",
      "line_number": 84,
      "pwm_id": -1
    },
    {
      "name": "7",
      "device_name": "gpiochip0",
      "line_number": 150,
      "pwm_id": -1
    },
    {
      "name": "11",
      "device_name": "gpiochip0",
      "line_number": 173,
      "pwm_id": -1
    },
    {
      "name": "13",
      "device_name": "gpiochip0",
      "line_number": 152,
      "pwm_id": -1
    },
    {
      "name": "15",
      "device_name": "gpiochip0",
      "line_number": 94,
      "pwm_id": -1
    },
    {
      "name": "19",
      "device_name": "gpiochip0",
      "line_number": 163,
      "pwm_id": -1
    },
    {
      "name": "21",
      "device_name": "gpiochip0",
      "line_number": 161,
      "pwm_id": -1
    },
    {
      "name": "23",
      "device_name": "gpiochip0",
      "line_number": 164,
      "pwm_id": -1
    },
    {
      "name": "27",
      "device_name": "gpiochip0",
      "line_number": 82,
      "pwm_id": -1
    },
    {
      "name": "29",
      "device_name": "gpiochip0",
      "line_number": 98,
      "pwm_id": -1
    },
    {
      "name": "31",
      "device_name": "gpiochip0",
      "line_number": 12,
      "pwm_id": -1
    },
    {
      "name": "33",
      "device_name": "gpiochip0",
      "line_number": 101,
      "pwm_id": -1
    },
    {
      "name": "35",
      "device_name": "gpiochip0",
      "line_number": 171,
      "pwm_id": -1
    },
    {
      "name": "37",
      "device_name": "gpiochip0",
      "line_number": 169,
      "pwm_id": -1
    },
    {
      "name": "8",
      "device_name": "gpiochip0",
      "line_number": 115,
      "pwm_id": -1
    },
    {
      "name": "10",
      "device_name": "gpiochip0",
      "line_number": 121,
      "pwm_id": -1
    },
    {
      "name": "12",
      "device_name": "gpiochip0",
      "line_number": 170,
      "pwm_id": -1
    },
    {
      "name": "16",
      "device_name": "gpiochip0",
      "line_number": 165,
      "pwm_id": -1
    },
    {
      "name": "18",
      "device_name": "gpiochip0",
      "line_number": 1,
      "pwm_id": -1
    },
    {
      "name": "22",
      "device_name": "gpiochip0",
      "line_number": 2,
      "pwm_id": -1
    },
    {
      "name": "24",
      "device_name": "gpiochip0",
      "line_number": 162,
      "pwm_id": -1
    },
    {
      "name": "26",
      "device_name": "gpiochip0",
      "line_number": 0,
      "pwm_id": -1
    },
    {
      "name": "28",
      "device_name": "gpiochip0",
      "line_number": 83,
      "pwm_id": -1
    },
    {
      "name": "32",
      "device_name": "gpiochip0",
      "line_number": 97,
      "pwm_id": -1
    },
    {
      "name": "36",
      "device_name": "gpiochip0",
      "line_number": 151,
      "pwm_id": -1
    },
    {
      "name": "38",
      "device_name": "gpiochip0",
      "line_number": 174,
      "pwm_id": -1
    },
    {
      "name": "40",
      "device_name": "gpiochip0",
      "line_number": 172,
      "pwm_id": -1
    }
  ]
}
```

## Configure a `customlinux` board

Configure your board as a [`customlinux`](https://app.viam.com/module/viam/customlinux) board to use your board definitions file:




### Config Builder

Navigate to the **CONFIGURE** tab of your machine’s page.
Click the **+** icon next to your machine part in the left-hand menu and select **Blocks**.
Select the `board` type, then select the `customlinux` model.
Enter a name or use the suggested name for your `customlinux` board and click **Add to machine**.

[Example configuration for a pumpkin board using customlinux](https://github.com/viam-modules/customlinux/blob/main/README.md#example-configuration-for-a-pumpkin-board)

Copy and paste the following json object into your board’s attributes field.

```json
{
  "board_defs_file_path": "/home/root/board.json"
}
```

### JSON Template

```json
{
  "components": [
    {
      "name": "myCustomBoard",
      "model": "customlinux",
      "api": "rdk:component:board",
      "attributes": {
        "board_defs_file_path": "/home/root/board.json"
      },
      "depends_on": []
    }
  ]
}
```



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

## Need assistance?

You can also ask questions in the [Community Discord](https://discord.gg/viam) and we will be happy to help.


