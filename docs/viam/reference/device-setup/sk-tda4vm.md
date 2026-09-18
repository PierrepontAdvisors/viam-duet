# SK-TDA4VM Setup Guide

Image a Texas Instruments TDA4VM starter kit board to prepare it for viam-server installation.
> Source: https://docs.viam.com/reference/device-setup/sk-tda4vm/


## Hardware requirements

- A [Texas Instruments TDA4VM single-board computer](https://www.ti.com/tool/SK-TDA4VM)
- A USB-C power cable to power the TDA4VM board
- A microSD card
- A desktop or laptop computer for flashing the microSD card
- A way to connect the microSD card to the computer (a microSD slot or microSD reader)
- An Ethernet cable
- An HDMI cable

## Required downloads

Download the following files to your computer:

- Download the <a href="https://www.ti.com/tool/download/PROCESSOR-SDK-LINUX-SK-TDA4VM" target="_blank">PROCESSOR-SDK-LINUX-SK-TDA4VM — Linux SDK for edge AI applications on TDA4VM Jacinto™ processors</a> image.

- Next, download and install the <a href="https://etcher.balena.io/#download-etcher" target="_blank">Balena Etcher</a> for your desktop/laptop OS.
  You will use the Balena Etcher to flash the microSD card.

## Flash the image

> **Important:**
> 
> You must extract the image from the zip file before flashing the microSD card.






    
    
    
<picture>

  
  
<source srcset="/installation/sk-tda4vm/etcher_hu_677dab0edc7f2cc7.webp" type="image/webp" width="600" height="379">
<img src="/installation/sk-tda4vm/etcher.png" width="600" height="379" alt="The Balena Etcher interface." class="" id="" style="" loading="lazy">
  

</picture>




<br>
<br>

1. Insert the microSD card into a reader connected to your computer.

2. Launch Balena Etcher.

3. Click **Flash from File** to open the file selector.

4. Navigate to and select the image you downloaded.

5. Click **Select Target** to choose the storage device corresponding to your microSD card from the selector window.

6. Click on the desired device, then click **Select** to continue.

7. Click **Flash!**.
   If you receive a warning concerning the size of the microSD card, ensure that you have inserted the proper microSD and also selected the proper device, then click, **Yes, I'm sure** to flash the board.
   The flashing and verification process may take 10-20 minutes, depending on your system.

   > **Tip: How to think about building a machine:**
> 
> 
>    While the Etcher is flashing your microSD card, we recommend reading [How to think about building a machine](/set-up-a-machine/first-machine/).
>    

8. On completion of the flashing and validation process, remove the microSD card from your computer and insert it into the TDA4VM.






    
    
    
<picture>

  
  
<source srcset="/installation/sk-tda4vm/completed_hu_9e21f3ed8bff2bd3.webp" type="image/webp" width="600" height="360">
<img src="/installation/sk-tda4vm/completed.png" width="600" height="360" alt="Successful image flash completion screen." class="shadow" id="" style="" loading="lazy">
  

</picture>




## Install Viam dependencies on the TDA4VM

1. Connect the board to Ethernet.

2. Connect the board to a monitor with the HDMI cable.

3. Connect the board to power using the USB-C power cable.

4. Use the credentials and IP address displayed in the upper right-hand corner of the monitor to SSH into the board.

From the SSH session on the TDA4VM board:

1. Clone the TDA4VM repo:

   ```sh {class="command-line" data-prompt="$"}
   git clone https://github.com/viam-labs/tda4vm-setup.git
   ```

2. Navigate to the setup directory:

   ```sh {class="command-line" data-prompt="$"}
   cd tda4vm-setup/
   ```

3. Make the server setup script executable:

   ```sh {class="command-line" data-prompt="$"}
   chmod +x tda4vm-viam-setup.sh
   ```

4. Launch the setup script to install `viam-server` dependencies:

   ```sh {class="command-line" data-prompt="$"}
   ./tda4vm-viam-setup.sh
   ```

   Once this process completes, the board will reboot.

## Next steps

You have now installed an operating system on your board.
To use your board, follow the [setup guide](/set-up-a-machine/first-machine/):

<div class="card-container">
  <div class="row-no-margin">
<div class="col hover-card "><a href="/set-up-a-machine/first-machine/"><div ><div>Set up your first machine</div><p>Create a machine in the Viam app and install Viam on your compute device.</p></div>
    </a></div>

</div>
</div>

## Need assistance?

You can also ask questions in the [Community Discord](https://discord.gg/viam) and we will be happy to help.


