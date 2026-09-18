# Raspberry Pi Setup Guide

Image a Raspberry Pi to prepare it for viam-server installation.
> Source: https://docs.viam.com/reference/device-setup/rpi-setup/


We recommend using Viam on a 64-bit Linux distribution.
Support for older Raspberry Pis running on 32-bit ARM v7 is in beta.

If you already have a Linux distribution installed on your [Pi](/reference/glossary/#term-pi)
, you can skip ahead to [install `viam-server`](/set-up-a-machine/first-machine/).

**Click to check whether the Linux installation on your Raspberry Pi is 64-bit or 32-bit**



To check whether the Linux installation on your Raspberry Pi is 64-bit or 32-bit, `ssh` into your Pi and then run `lscpu`.

Example output:






    
    
    
<picture>

  
  
<source srcset="/installation/rpi-setup/lscpu-output_hu_4508b099f1c04fdf.webp" type="image/webp" width="800" height="509">
<img src="/installation/rpi-setup/lscpu-output.png" width="800" height="509" alt="Screenshot of a terminal running the &#39;lscpu&#39; command. The output lists of this command on a Raspberry Pi. A red box highlights the command and the top of the output which reads &#39;Architecture: aarch64.&#39;" class="shadow" id="" style="" loading="lazy">
  

</picture>




If the value of "Architecture: _'xxxxxx'_" ends in "64", you can skip ahead to [install `viam-server`](/set-up-a-machine/first-machine/).




## Hardware requirements

- A [Raspberry Pi single-board computer](https://www.raspberrypi.com/products/raspberry-pi-4-model-b/)
- A microSD card
- An internet-connected computer
- A way to connect the microSD card to the computer (microSD slot or microSD reader)

## Install Raspberry Pi OS

The Raspberry Pi boots from a microSD card.
You need to install Raspberry Pi OS (formerly called Raspbian) on the microSD card you will use with your Pi:

1. Connect the microSD card to your computer.

1. Download the [Raspberry Pi Imager](https://www.raspberrypi.com/software/) and launch it.

   
   
   
   
   
       
       
       
   <picture>
   
     
     
   <source srcset="/installation/rpi-setup/imager-launch-screen_hu_672872cb311e2bca.webp" type="image/webp" width="800" height="596">
   <img src="/installation/rpi-setup/imager-launch-screen.png" width="800" height="596" alt="Raspberry Pi Imager launcher window showing a &#39;Choose OS&#39; and &#39;Choose Storage&#39; buttons." class="shadow" id="" style="" loading="lazy">
     
   
   </picture>
   
   


1. Click **CHOOSE DEVICE**.
   Select your model of Pi.

   
   
   
   
   
       
       
       
   <picture>
   
     
     
   <source srcset="/installation/rpi-setup/select-pi-models_hu_a37346df9c2eacce.webp" type="image/webp" width="800" height="596">
   <img src="/installation/rpi-setup/select-pi-models.png" width="800" height="596" alt="Raspberry Pi Imager window showing available pi models." class="shadow" id="" style="" loading="lazy">
     
   
   </picture>
   
   


1. Click **CHOOSE OS**.
   Select **Raspberry Pi OS (other)**.

   
   
   
   
   
       
       
       
   <picture>
   
     
     
   <source srcset="/installation/rpi-setup/select-other-custom-os_hu_d353a8a13683f59a.webp" type="image/webp" width="800" height="596">
   <img src="/installation/rpi-setup/select-other-custom-os.png" width="800" height="596" alt="Raspberry Pi Imager window showing Raspberry Pi OS (Other) is selected." class="shadow" id="" style="" loading="lazy">
     
   
   </picture>
   
   


   Select **Raspberry Pi OS Full (64-bit)** or **Raspberry Pi OS Full (32-bit)** from the menu.

   
   
   
   
   
       
       
       
   <picture>
   
     
     
   <source srcset="/installation/rpi-setup/select-other-rpi_hu_5c5d04574b00800e.webp" type="image/webp" width="800" height="596">
   <img src="/installation/rpi-setup/select-other-rpi.png" width="800" height="596" alt="Raspberry Pi Imager window showing Raspberry Pi OS (Legacy, 64-bit) Full is selected." class="shadow" id="" style="" loading="lazy">
     
   
   </picture>
   
   


   You should be brought back to the initial launch screen.

1. Click **CHOOSE STORAGE**.
   From the list of devices, select the microSD card you intend to use in your Raspberry Pi.

   If no devices are listed, make sure your microSD card is connected to your computer correctly.

   
   
   
   
   
       
       
       
   <picture>
   
     
     
   <source srcset="/installation/rpi-setup/imager-select-storage_hu_10339b7f2e696365.webp" type="image/webp" width="800" height="596">
   <img src="/installation/rpi-setup/imager-select-storage.png" width="800" height="596" alt="The storage screen is shown with a generic SD card available as an option." class="shadow" id="" style="" loading="lazy">
     
   
   </picture>
   
   


1. Configure your Raspberry Pi for remote access.
   Click **Next**.
   When prompted to apply OS customization settings, select **EDIT SETTINGS**.

   
   
   
   
   
       
       
       
   <picture>
   
     
     
   <source srcset="/installation/rpi-setup/advanced-options_hu_10215808a80e42ab.webp" type="image/webp" width="800" height="596">
   <img src="/installation/rpi-setup/advanced-options.png" width="800" height="596" alt="Raspberry Pi Imager window showing gear-shaped settings icon is selected." class="shadow" id="" style="" loading="lazy">
     
   
   </picture>
   
   


   > **Important:**
> 
> If you are using a non-Raspberry Pi OS, altering the OS customization settings will cause the initial boot to fail.

   Check **Set hostname** and enter the name you would like to access the Pi by in that field:

   
   
   
   
   
       
       
       
   <picture>
   
     
     
   <source srcset="/installation/rpi-setup/imager-set-hostname_hu_60dd7484112c831.webp" type="image/webp" width="600" height="706">
   <img src="/installation/rpi-setup/imager-set-hostname.png" width="600" height="706" alt="Raspberry Pi Imager window showing the advanced options menu with set hostname checked and set to my-machine.local." class="shadow" id="" style="" loading="lazy">
     
   
   </picture>
   
   


   There are two ways you can secure your Raspberry Pi: with an SSH key or with password authentication.

   - For a learning project or a fun hobby project, we recommend using password authentication because it is easiest to set up for first-time users.
   - For production use, we recommend using SSH keys for more secure authentication; only someone with the private SSH key will be able to authenticate to your system.

   


### Password

<ol>
<li>
Select the checkbox next to **Set username and password** and set a username (for example, your first name) and a unique password that you will use to log into the Pi:

<picture>
<source srcset="/installation/rpi-setup/imager-set-passwordauthentication_hu_b203ac20df07d770.webp" type="image/webp" width="550" height="647">
<img src="/installation/rpi-setup/imager-set-passwordauthentication.png" width="550" height="647" alt="Raspberry Pi Imager window showing the 'Set username and password' option is selected. The user has entered username 'Robota' and some hidden password." class="shadow" id="" style="" loading="lazy">
</picture>
</li>
<li>
Select the **SERVICES** tab.

</li>
<li>
Check **Enable SSH**.

</li>
</ol>
<blockquote>
**IMPORTANT:**

Be sure that you remember the `hostname`, `username`, and `password` you set, as you will need them when you SSH into your Pi.

Do not use the default username and password on a Raspberry Pi, as this poses a [security risk](https://www.zdnet.com/article/linux-malware-enslaves-raspberry-pi-to-mine-cryptocurrency/).

</blockquote>

### SSH

To set up SSH authentication:

<ol>
<li>
Select the checkbox for **Set username and password** and set a username (for example, your first name) that you will use to log into the Pi.
If you skip this step, the default username will be `pi` (not recommended for security reasons).
You do not need to specify a password.

<picture>
<source srcset="/installation/rpi-setup/imager-set-username_hu_bad5a09743097c1.webp" type="image/webp" width="500" height="588">
<img src="/installation/rpi-setup/imager-set-username.png" width="500" height="588" alt="Raspberry Pi Imager with username specified as 'Robota' and the password field left blank." class="shadow" id="" style="" loading="lazy">
</picture>
</li>
<li>
Select the **SERVICES** tab.

</li>
<li>
Check **Enable SSH**.

</li>
<li>
Select **Allow public-key authentication only**.

If you select **Allow public-key authentication only**, and the section **Set authorized_ keys for ‘’** is pre-populated, that means you have a public SSH key that is ready to use.
In that case, you can leave the pre-populated key as-is.
If this section is empty, you can either generate a new SSH key using [these instructions](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent), or you can use password authentication instead.

<picture>
<source srcset="/installation/rpi-setup/imager-set-ssh_hu_f13b3008737cf48b.webp" type="image/webp" width="500" height="588">
<img src="/installation/rpi-setup/imager-set-ssh.png" width="500" height="588" alt="Raspberry Pi Imager window showing 'Set Hostname' and 'Enable SSH' both selected." class="shadow" id="" style="" loading="lazy">
</picture>
</li>
</ol>
<blockquote>
**IMPORTANT:**

Be sure that you remember the `hostname` and `username` you set, as you will need this when you SSH into your Pi.

</blockquote>



    Lastly, connect your Pi to Wi-Fi so that you can run `viam-server` wirelessly.
    Check **Configure wireless LAN** and enter your wireless network credentials.
    SSID (short for Service Set Identifier) is your Wi-Fi network name, and password is the network password.
    Change the section `Wireless LAN country` to where your router is currently being operated:

    
    
    
    
    
        
        
        
    <picture>
    
      
      
    <source srcset="/installation/rpi-setup/imager-set-wifi_hu_23a65078ca009bd1.webp" type="image/webp" width="550" height="647">
    <img src="/installation/rpi-setup/imager-set-wifi.png" width="550" height="647" alt="Raspberry Pi Imager window showing the &#39;Configure wireless LAN&#39; option selected with SSID and password information for a wireless network." class="shadow" id="" style="" loading="lazy">
      
    
    </picture>
    
    


    Click **SAVE**.

1.  Double check your OS and Storage settings and then click `YES`:

    
    
    
    
    
        
        
        
    <picture>
    
      
      
    <source srcset="/installation/rpi-setup/apply-settings-yes_hu_51776232fc034fc.webp" type="image/webp" width="800" height="596">
    <img src="/installation/rpi-setup/apply-settings-yes.png" width="800" height="596" alt="Edit image customization options window" class="shadow" id="" style="" loading="lazy">
      
    
    </picture>
    
    


    You will be prompted to confirm erasing your microSD card: select `YES`.

    
    
    
    
    
        
        
        
    <picture>
    
      
      
    <source srcset="/installation/rpi-setup/imager-write-confirm_hu_339c58fcbd7a23ab.webp" type="image/webp" width="800" height="596">
    <img src="/installation/rpi-setup/imager-write-confirm.png" width="800" height="596" alt="Edit image customization options window" class="shadow" id="" style="" loading="lazy">
      
    
    </picture>
    
    


    You may also be prompted by your operating system to enter an administrator password:

    
    
    
    
    
        
        
        
    <picture>
    
      
      
    <source srcset="/installation/rpi-setup/imager-permission_hu_7feb3fd23054fb8e.webp" type="image/webp" width="300" height="350">
    <img src="/installation/rpi-setup/imager-permission.png" width="300" height="350" alt="macOS admin password confirmation screen." class="shadow" id="" style="" loading="lazy">
      
    
    </picture>
    
    


    After granting permissions to the Imager, it will begin writing and then verifying the Linux installation to the MicroSD card.

    Remove the microSD card from your computer when the installation is complete.

    > **Tip: How to think about building a machine:**
> 
> 
> 
> While the Imager is flashing your microSD card, we recommend reading [How to think about building a machine](/set-up-a-machine/first-machine/).
> 
>     

2.  Place the SD card into your Raspberry Pi and boot the Pi by plugging it in to an outlet.
    A red LED will turn on to indicate that the Pi is connected to power.

## Update WiFi credentials

If you move your Raspberry Pi to a different WiFi network, you need to update the WiFi credentials.

You can update the WiFi configuration by creating a new `wpa_supplicant.conf` file on the boot partition:

1. Remove the microSD card from the Pi and plug it into your computer.
1. Create a plain text file called `wpa_supplicant.conf` on the boot partition.
1. Paste the following into the file, replacing the SSID and password values with your credentials.
   Use UNIX (LF) line breaks.

   ```bash {class="line-numbers linkable-line-numbers"}
   ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
   update_config=1
   country=us

   network={
    ssid="Name of your wireless LAN"
    psk="Password for your wireless LAN"
    priority=10
   }
   ```

   You can duplicate the `network` section to add multiple WiFi networks (for example, work and home).
   The `priority` attribute is optional: higher numbers are preferred when multiple configured networks are available.

1. Save the file and eject the microSD card.
1. Put the microSD card back into the Pi and boot it.

The Pi reads and removes `wpa_supplicant.conf` on boot, updating the stored WiFi credentials.

## Next steps

Continue setting up `viam-server` on your Raspberry Pi in [the Viam app](https://app.viam.com/):

<div class="card-container">
  <div class="row-no-margin">
<div class="col hover-card "><a href="/set-up-a-machine/first-machine/"><div ><div>Set up your first machine</div><p>Create a machine in the Viam app and install Viam on your compute device.</p></div>
    </a></div>

</div>
</div>

