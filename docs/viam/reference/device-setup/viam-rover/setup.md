# Unbox and set up your Viam Rover 2

A list of the contents of the Viam Rover 2 kit, instructions for wiring your rover, and links for additional hardware.
> Source: https://docs.viam.com/reference/device-setup/viam-rover/setup/


> **Tip:**
> 
> Viam no longer sells the Viam Rover 2.
> This guide remains available for everyone who already has a rover.
> 
> Another version of the Viam Rover was sold until January 2024.
> If you have a Viam Rover 1, follow [these instructions](/reference/device-setup/viam-rover/rover-1-setup/) instead.

The [Viam Rover 2](https://www.viam.com/resources/rover) comes preassembled with two encoded motors with suspension, a webcam with a microphone unit, a 6 axis IMU, power management and more.
It is primarily designed for use with a Raspberry Pi 4.
You can use it with [other types of boards](#motherboard) with some additional setup.

> **Important:**
> 
> 
> You must purchase the following hardware separately:
> 
> - A Raspberry Pi 4
> - Four 18650 batteries or an RC-type battery with dimensions no greater than 142mm x 47mm x 60mm (LxWxH), with charger
> - A MicroSD card and an adapter/reader
>   

This guide covers what's inside the kit and provides instructions for [setting up your rover](#setup).

> **Note:**
> 
> 
> The design for this rover is open source.
> Find the details on [GitHub](https://github.com/viamrobotics/Viam-Rover-2).
> 

## What's inside the kit

1. One assembled Viam Rover.

   
   
   
   
   
       
       
       
   <picture>
   
     
     
   <source srcset="/appendix/try-viam/rover-resources/viam-rover-2/rover-side_hu_a4dd1c80c99e7567.webp" type="image/webp" width="400" height="266">
   <img src="/appendix/try-viam/rover-resources/viam-rover-2/rover-side.png" width="400" height="266" alt="The side of the assembled Viam Rover" class="" id="" style="" loading="lazy">
     
   
   </picture>
   
   


1. Four M2.5 screws for mounting your Raspberry Pi.

   
   
   
   
   
       
       
       
   <picture>
   
     
     
   <source srcset="/appendix/try-viam/rover-resources/viam-rover/screws_hu_8be428b3e25aee39.webp" type="image/webp" width="200" height="205">
   <img src="/appendix/try-viam/rover-resources/viam-rover/screws.jpg" width="200" height="205" alt="Four screws" class="" id="" style="" loading="lazy">
     
   
   </picture>
   
   


1. Two spare stiffer suspension springs.
   You can swap them out with the springs that come with the rover if you need stiffer suspension for higher payload applications.

   
   
   
   
   
       
       
       
   <picture>
   
     
     
   <source srcset="/appendix/try-viam/rover-resources/viam-rover/suspension-springs_hu_b0d66189a3e221a.webp" type="image/webp" width="200" height="214">
   <img src="/appendix/try-viam/rover-resources/viam-rover/suspension-springs.jpg" width="200" height="214" alt="Two suspension springs" class="" id="" style="" loading="lazy">
     
   
   </picture>
   
   


1. Three different Allen wrenches (1.5 mm, 2 mm, and 2.5 mm) to unscrew the top and mount the Raspberry Pi.

   
   
   
   
   
       
       
       
   <picture>
   
     
     
   <source srcset="/appendix/try-viam/rover-resources/viam-rover/allen-wrenches_hu_61d0a81861b13e63.webp" type="image/webp">
   <img src="/appendix/try-viam/rover-resources/viam-rover/allen-wrenches.png" alt="Three allen wrenches" class="" id="" style="" loading="lazy">
     
   
   </picture>
   
   


1. Four extenders to increase the height of the rover to house larger internal single-board computers (such as a Jetson Orin Nano).

   
   
   
   
   
       
       
       
   <picture>
   
     
     
   <source srcset="/appendix/try-viam/rover-resources/viam-rover-2/extenders_hu_5465173c18bab1e0.webp" type="image/webp" width="400" height="274">
   <img src="/appendix/try-viam/rover-resources/viam-rover-2/extenders.png" width="400" height="274" alt="Four extenders" class="" id="" style="" loading="lazy">
     
   
   </picture>
   
   


1. Ribbon cable for connecting the Raspberry Pi 4 to the Viam Rover 2 printed circuit board.

   
   
   
   
   
       
       
       
   <picture>
   
     
     
   <source srcset="/appendix/try-viam/rover-resources/viam-rover-2/ribbon-cable_hu_31cfda23d6004e12.webp" type="image/webp" width="400" height="182">
   <img src="/appendix/try-viam/rover-resources/viam-rover-2/ribbon-cable.png" width="400" height="182" alt="Ribbon cable" class="" id="" style="" loading="lazy">
     
   
   </picture>
   
   


All together, your kit looks like this:






    
    
    
<picture>

  
  
<source srcset="/appendix/try-viam/rover-resources/viam-rover-2/box-contents_hu_dff2a97c9d7010d.webp" type="image/webp" width="400" height="443">
<img src="/appendix/try-viam/rover-resources/viam-rover-2/box-contents.png" width="400" height="443" alt="A Viam Rover shipping box contents" class="" id="" style="" loading="lazy">
  

</picture>




## Rover components

### Dual drive motors with suspension and integrated motor encoders






    
    
    
<picture>

  
  
<source srcset="/appendix/try-viam/rover-resources/viam-rover/encoder-motors_hu_37d653d8e2fbc63d.webp" type="image/webp" width="400" height="270">
<img src="/appendix/try-viam/rover-resources/viam-rover/encoder-motors.jpg" width="400" height="270" alt="two motors with encoders" class="" id="" style="" loading="lazy">
  

</picture>




The motors come with integrated encoders.
For information on encoders, see [Encoder Component](/reference/components/encoder/).
For more information on encoded DC motors, see [Encoded Motors](/reference/components/motor/encoded-motor/).

The kit also includes stiffer suspension springs that you can substitute for the ones on the rover.
Generally, a stiff suspension helps with precise steering control.
In contrast, a soft suspension allows the wheels to move up and down to absorb small bumps on the rover's path.

### Motor driver






    
    
    
<picture>

  
  
<source srcset="/appendix/try-viam/rover-resources/viam-rover/motor-driver_hu_622edf6b3699ea33.webp" type="image/webp" width="400" height="394">
<img src="/appendix/try-viam/rover-resources/viam-rover/motor-driver.png" width="400" height="394" alt="A L298N motor driver" class="" id="" style="" loading="lazy">
  

</picture>




The kit comes with an L298N driver dual H-Bridge DC motor driver.
L298 is a high voltage and high current motor drive chip, and H-Bridge is typically used to control the rotating direction and speed of DC motors.

### 720p webcam with integrated microphone






    
    
    
<picture>

  
  
<source srcset="/appendix/try-viam/rover-resources/viam-rover/webcam_hu_6c8e703f0b2b605a.webp" type="image/webp" width="400" height="300">
<img src="/appendix/try-viam/rover-resources/viam-rover/webcam.jpg" width="400" height="300" alt="Webcam with cables" class="" id="" style="" loading="lazy">
  

</picture>




The webcam that comes with the kit is a standard USB camera device and the rover has a custom camera mount for it.
For more information, see [Camera Component](/reference/components/camera/).

### Motherboard






    
    
    
<picture>

  
  
<source srcset="/appendix/try-viam/rover-resources/viam-rover-2/motherboard_hu_a8dacf83f66efd11.webp" type="image/webp" width="400" height="441">
<img src="/appendix/try-viam/rover-resources/viam-rover-2/motherboard.png" width="400" height="441" alt="Viam rover 2 motherboard" class="" id="" style="" loading="lazy">
  

</picture>




The Viam Rover 2 uses a motherboard to which all ancillary components (buck converter, motor driver, IMU, INA219) are mounted.
This board includes an auxiliary Raspberry Pi 4 pinout that dupont connectors can be connected to, an auxiliary power input terminal, 5V, 3.3V and Ground pins.

The motherboard also incorporates hole patterns for the following alternative single-board computers:

- Jetson Nano and Orin Nano
- Rock Pi S
- Raspberry Pi Zero 2W
- Raspberry Pi 5
- Orange Pi Zero 2

See [Alternative Board Configurations](#alternative-board-configurations) for a diagram of this.
Note that these boards require additional parts to be purchased and will not work out of the box with the Viam Rover 2.

### 6DOF IMU






    
    
    
<picture>

  
  
<source srcset="/appendix/try-viam/rover-resources/viam-rover-2/mpu6050_hu_607f4e644f8d0a99.webp" type="image/webp" width="400" height="306">
<img src="/appendix/try-viam/rover-resources/viam-rover-2/mpu6050.png" width="400" height="306" alt="An MPU6050 gyroscope" class="" id="" style="" loading="lazy">
  

</picture>




The MPU6050 sensor is a digital 6-axis accelerometer or gyroscope that can read acceleration and angular velocity.
You can access it through the I2C digital interface.
You configure it with Viam on your machine as a [movement sensor](https://github.com/viam-modules/tdk-invensense/).

### INA219 power monitoring unit






    
    
    
<picture>

  
  
<source srcset="/appendix/try-viam/rover-resources/viam-rover-2/ina219_hu_644bcc430190c8ca.webp" type="image/webp" width="400" height="353">
<img src="/appendix/try-viam/rover-resources/viam-rover-2/ina219.png" width="400" height="353" alt="An INA219 unit" class="" id="" style="" loading="lazy">
  

</picture>




The INA219 unit measures the voltage and current from the power supply.
You can use it to measure battery life status and power consumption.
It connects to the Raspberry Pi 4 through the I2C bus.
You configure it with Viam on your machine as a [power sensor](https://github.com/viam-modules/texas-instruments/).

### DC-DC 5V converter






    
    
    
<picture>

  
  
<source srcset="/appendix/try-viam/rover-resources/viam-rover-2/buck-converter_hu_f74ccb2a80742539.webp" type="image/webp" width="300" height="498">
<img src="/appendix/try-viam/rover-resources/viam-rover-2/buck-converter.png" width="300" height="498" alt="A OKY3502-4 buck converter" class="" id="" style="" loading="lazy">
  

</picture>




The DC-to-DC power converter, or, buck converter, steps down voltage from its input to its output.
The OKY3502-4 has a USB output that can provide an additional 5V supply to auxiliary components.

### Switch and low voltage cutoff circuit






    
    
    
<picture>

  
  
<source srcset="/appendix/try-viam/rover-resources/viam-rover-2/slide-switch_hu_fb62155b9f9ab247.webp" type="image/webp" width="400" height="265">
<img src="/appendix/try-viam/rover-resources/viam-rover-2/slide-switch.png" width="400" height="265" alt="The switch mounted on the Viam rover 2" class="" id="" style="" loading="lazy">
  

</picture>




A slide switch is connected to the rover.
Use it to turn the power on and off.






    
    
    
<picture>

  
  
<source srcset="/appendix/try-viam/rover-resources/viam-rover-2/circuit_hu_9392469397137645.webp" type="image/webp" width="400" height="356">
<img src="/appendix/try-viam/rover-resources/viam-rover-2/circuit.png" width="400" height="356" alt="Low-voltage cutoff circuit" class="" id="" style="" loading="lazy">
  

</picture>




Mounted above the switch is a low voltage cutoff circuit that can be set to turn off power to the rover when the input voltage drops below a pre-set threshold.
This can be helpful for preventing batteries fully discharging which can damage lithium ion batteries.

### Battery holders

The Viam Rover 2 comes with two battery holder options.
The rover nominally operates with four 18650 batteries, but a higher capacity RC-type battery can be mounted into the rear of the rover.

> **Note:**
> 
> With either battery option, you must purchase a charger separately.

#### 18650 battery pack






    
    
    
<picture>

  
  
<source srcset="/appendix/try-viam/rover-resources/viam-rover-2/battery-pack_hu_cb303388eed1e7f6.webp" type="image/webp" width="400" height="308">
<img src="/appendix/try-viam/rover-resources/viam-rover-2/battery-pack.png" width="400" height="308" alt="A battery pack" class="" id="" style="" loading="lazy">
  

</picture>




18650 batteries are the nominal power supply recommended for use with the Viam Rover 2.
An 18650 battery is a lithium-ion rechargeable battery.
We recommend the button-top type, though either button or flat top can work.
Any brand is suitable as long as you comply with the battery safety requirements.

#### Mount for RC-type battery






    
    
    
<picture>

  
  
<source srcset="/appendix/try-viam/rover-resources/viam-rover-2/RC-mount_hu_cc46a72999602f4d.webp" type="image/webp" width="400" height="154">
<img src="/appendix/try-viam/rover-resources/viam-rover-2/RC-mount.png" width="400" height="154" alt="RC battery mount" class="" id="" style="" loading="lazy">
  

</picture>




You can mount a larger capacity RC-type battery into the rover.
You must wire the appropriate connector into the switch circuit.

RC-batteries are lithium-ion rechargeable batteries.
Caution should always be taken when using such batteries, always comply with the battery safety requirements.
Check the [safety](#safety) section for more information.

## Safety

Read all instructions fully before using this product.

This product is not a toy and is not suitable for children under 12.

Switch the rover off when not in use.

> **Warning:**
> 
> 
> Lithium-ion batteries may pose a flammable hazard.
> This product requires four 18650 lithium-ion batteries OR an RC-type battery.
> DO NOT connect multiple power sources simultaneously.
> Refer to the battery manufacturer's operating instructions to ensure safe operation of the Viam Rover.
> Dispose of lithium-ion batteries per manufacturer instructions.
> 

> **Caution:**
> 
> 
> Damage may occur to the Raspberry Pi and/or Viam Rover if wired incorrectly.
> Refer to the manufacturer's instructions for correct wiring.
> 

Disclaimer: This product is preliminary and experimental in nature, and is provided "AS IS" without any representation or warranty of any kind.
Viam does not make any promise or warranty that the product will meet your requirements or be error free.
Some states do not allow the exclusion or disclaimer of implied warranties, so the above exclusions may not apply to you.

## Setup

> **Important:**
> 
> If you wish to use a Jetson Nano or Jetson Orin Nano, follow [this guide](/reference/device-setup/viam-rover/jetson-setup/) instead.

### Install Raspberry Pi OS

> **Tip:**
> 
> If you are using another board, you can skip this step.

Install a 64-bit Raspberry Pi OS onto your Pi following our [Raspberry Pi installation guide](/reference/device-setup/rpi-setup/).
Follow all steps as listed.
You must also enable I<sup>2</sup>C on your Pi using `sudo raspi-config` so that your Pi can communicate with the accelerometer and power sensor on your rover.
Once you have installed Raspberry Pi OS and `viam-server`, put your SD card in the slot on your Pi.

### Add the power supply

You can power the Viam Rover 2 using 18650 batteries or RC-type batteries.
18650 batteries are the nominal power supply recommended for use with the rover, but RC-type batteries are higher capacity.




### 18650 Batteries

<picture>
<source srcset="/appendix/try-viam/rover-resources/viam-rover-2/rover-underview_hu_31e6cf9ae3e229bd.webp" type="image/webp" width="400" height="313">
<img src="/appendix/try-viam/rover-resources/viam-rover-2/rover-underview.png" width="400" height="313" alt="Under view of rover with battery pack." class="" id="" style="" loading="lazy">
</picture>
<p>The Viam Rover 2 arrives with the 18650 battery pack wired into the power input terminal block.
The battery pack works with batteries 67.5 mm in length, but the battery housing includes a spring to accommodate most batteries of that approximate length.</p>
<ul>
<li>Turn the rover over so that you can see the battery housing.</li>
<li>Place four 18650 batteries (taking care to ensure correct polarity orientation) inside the battery pack to provide power to the rover, which can be turned on and off through the power switch.</li>
</ul>
<blockquote>
<p><strong>Tip:</strong></p>
<p>Ensure that the batteries are making contact with the terminals inside the battery pack.
Some shorter batteries might need to be pushed along to ensure that contact is being made.</p>
</blockquote>


### RC-Type Battery

<picture>
<source srcset="/appendix/try-viam/rover-resources/viam-rover-2/rcbattery-underneath_hu_1f116857be582135.webp" type="image/webp" width="400" height="304">
<img src="/appendix/try-viam/rover-resources/viam-rover-2/rcbattery-underneath.png" width="400" height="304" alt="Under view of rover with battery pack." class="" id="" style="" loading="lazy">
</picture>
<p>For users who prefer a higher capacity battery option, the Viam Rover 2 can house RC-type batteries that do not exceed the following dimensions: 142mm x 47mm x 60mm (LxWxH).
Using an RC-type battery requires some re-wiring of the Viam Rover 2 which should only be undertaken by users who are comfortable handling electrical assemblies.
Improper configuration of the power supply could result in damage to the battery and poses a fire hazard.
A 4S RC-type battery is recommended (14.8V).
We make no recommendations regarding specific RC battery brands.</p>
<p>To change the rover&rsquo;s power supply configuration for a RC-battery:</p>
<ol>
<li>
<p>Ensure the 18650 battery holder contains no batteries</p>
</li>
<li>
<p>Unscrew the 18650 battery leads from the power input terminal.
Move these wires out of the way.</p>
</li>
<li>
<p>Screw in a power lead that matches that of the selected battery.
Common options include: EC-type connectors, XT-connectors or T-plugs.
Ensure lead is long enough to reach the battery.</p>
</li>
<li>
<p>Ensure that the polarity is correct (the polarity is marked on the PCB).
<strong>Failure to do so may result in permanent damage to your Viam Rover 2 when powered on.</strong></p>
</li>
<li>
<p>Ensure that there is no short between the terminals (for example, due to a stray strand of wire). Use a multimeter to check continuity across the terminal to verify this.
Failure to do so may result in damage to the battery and may pose a fire hazard.</p>
</li>
<li>
<p>Place the battery in the receptacle between the two caster wheels:</p>
<picture>
<source srcset="/appendix/try-viam/rover-resources/viam-rover-2/RC-mount_hu_cc46a72999602f4d.webp" type="image/webp" width="400" height="154">
<img src="/appendix/try-viam/rover-resources/viam-rover-2/RC-mount.png" width="400" height="154" alt="RC battery mount" class="" id="" style="" loading="lazy">
</picture>
<p>Connect the battery to the lead that is wired into the power input terminal.
Although not necessary, slots in the bottom plate of the rover allow a velcro strap to be placed around the battery to secure it.</p>
</li>
</ol>




> **Caution:**
> 
> DO NOT connect both power supplies at the same time.
> These suggestions are alternative configurations.
> Connecting multiple batteries together may result in damage to the batteries and rover, it may also pose a fire hazard.

### Configure the low voltage cutoff circuit

Now that you have connected your power supply to your rover, you need to configure the [low voltage cutoff circuit](#switch-and-low-voltage-cutoff-circuit).
You must configure two settings:

1.  The low voltage cutoff
2.  The reconnect voltage

The reconnect voltage is the voltage increment above the cutoff point that is needed for the power to reconnect.
For both 18650 and RC-type battery inputs, the nominal voltage is 14.8V, so you should set the low voltage threshold to 14.7.
You can adjust this value if using a battery that has an alternative nominal voltage.

To set the low voltage cutoff and reconnect voltage:

1.  Turn on the circuit using the switch.
    The LED indicator should indicate a current voltage level of 14.8-16V depending on the battery charge status:

    
    
    
    
    
        
        
        
    <picture>
    
      
      
    <source srcset="/appendix/try-viam/rover-resources/viam-rover-2/circuit-led_hu_65ad06b7fc81a3f4.webp" type="image/webp" width="300" height="214">
    <img src="/appendix/try-viam/rover-resources/viam-rover-2/circuit-led.png" width="300" height="214" alt="LED with voltage level displayed on low voltage cutoff circuit" class="" id="" style="" loading="lazy">
      
    
    </picture>
    
    


2.  Hold down the left button until the LED display starts flashing with the low cutoff value.
    The factory default low cutoff value is 12V.
3.  Use the left (+) and right (-) buttons to set the voltage to 14.7V (or whatever you want the cutoff to be).
4.  Wait for the indicator to stop flashing.
5.  Hold down the right button until the LED display starts flashing with the reconnect voltage value. The factory default reconnect voltage is 2.0V.
6.  Use the left (+) and right (-) buttons to set the reconnect voltage to 0.2V.
7.  Wait for the indicator to stop flashing.

Your voltage cutoff circuit is now configured.
When the voltage drops below 14.8V (or reaches the cutoff point you chose), a relay will disconnect the motherboard.
A minimum voltage of 14.9V will be needed to reconnect the power (that is, after charging the batteries).

### Connect the ribbon cable, Pi, and camera

> **Tip:**
> 
> If you are using another board, follow the instructions in [Alternative board configurations](#alternative-board-configurations) in place of this step.

To be able to attach the Raspberry Pi, unscrew the top of the rover with the biggest Allen key.
Then use the smallest Allen key and the provided M2.5 screws to attach the Raspberry Pi to your rover through the standoffs on the motherboard.
The Raspberry Pi 4 should be mounted such that the USB ports are to the right, as viewed from above.

Use the ribbon cable to connect the Raspberry Pi 4 to the motherboard.
The ribbon cable comes connected to the motherboard out of the box, wrap it over the top of the Raspberry Pi 4 and connect with the GPIO pins as shown:






    
    
    
<picture>

  
  
<source srcset="/appendix/try-viam/rover-resources/viam-rover-2/ribbon-cable1_hu_5a34a7ae21becf07.webp" type="image/webp" width="400" height="353">
<img src="/appendix/try-viam/rover-resources/viam-rover-2/ribbon-cable1.png" width="400" height="353" alt="Ribbon cable attached to pi" class="" id="" style="" loading="lazy">
  

</picture>



<br>





    
    
    
<picture>

  
  
<source srcset="/appendix/try-viam/rover-resources/viam-rover-2/ribbon-cable2_hu_ceaba2e74566acd9.webp" type="image/webp" width="400" height="240">
<img src="/appendix/try-viam/rover-resources/viam-rover-2/ribbon-cable2.png" width="400" height="240" alt="Ribbon cable attached to pi" class="" id="" style="" loading="lazy">
  

</picture>




Also, connect the webcam's USB lead to any USB port on your Pi.

Assuming you are using a Raspberry Pi 4, you can skip the following section and move to [Screw the top plate back on and switch the rover on](#screw-the-top-plate-back-on-and-switch-the-rover-on).

### Alternative board configurations

This guide assumes you are using a Raspberry Pi 4, but you can use [different boards](#motherboard) with your Viam Rover 2 with some modifications while attaching the boards.

> **Tip:**
> 
> If you are using a Jetson board, you should be following [this guide](/reference/device-setup/viam-rover/jetson-setup/).

Reference the appropriate alternative hole pattern provided on the motherboard:






    
    
    
<picture>

  
  
<source srcset="/appendix/try-viam/rover-resources/viam-rover-2/hole-patterning_hu_fd36f1c61952287c.webp" type="image/webp" width="400" height="395">
<img src="/appendix/try-viam/rover-resources/viam-rover-2/hole-patterning.png" width="400" height="395" alt="Viam rover 2 motherboard hole patterns" class="" id="" style="" loading="lazy">
  

</picture>




Detach the motherboard, unscrew the standoffs, and move them to the correct holes.
Then, use the smallest Allen key and the provided M2.5 screws to attach your board to your rover through these standoffs.

**Raspberry Pi Zero 2W**


If you are using a Raspberry Pi Zero 2W, you should be able to connect your ribbon cable straight to the board.
If not, you will have to take off the ribbon cable and use [dupont connectors](https://www.amazon.com/IWISS-1550PCS-Connector-Headers-Balancer/dp/B08X6C7PZM/) to wire a connection from the motherboard to the single-board computer's GPIO pins.



**Raspberry Pi 5**


If you are using a Raspberry Pi 5, use the same screw placements as for the Raspberry Pi 4.
The hardware setup is the same.
The only difference is in the [configuration](/reference/device-setup/viam-rover/fragments/).



Then connect the webcam's USB lead to any USB port on your board.

If you need to increase the height of your rover to accommodate your board being larger than a Raspberry Pi 4, place the [height extender standoffs](#whats-inside-the-kit) now.

### Screw the top plate back on and switch the rover on

Screw the top plate back on with the biggest Allen key and use the power switch to turn the rover on.
Wait a second for the low voltage cutoff relay to trip and provide power to the rover motherboard.
If the Pi has power, the lights on the Raspberry Pi will light up.

### Control your rover on Viam

If you followed the instructions in the [Pi installation guide](/reference/device-setup/rpi-setup/), you should have already made a Viam account, installed `viam-server` on the board, and added a new machine.

If not, add a new machine and follow the [setup instructions](/reference/glossary/#term-setup)
 until your machine is connected.

To configure your rover so you can start driving it, [add a Viam Rover 2 fragment to your machine](/reference/device-setup/viam-rover/fragments/).

## Next steps

Before you can use your Viam rover with the Viam platform you need to configure your rover:

<div class="card-container">
  <div class="row-no-margin">
<div class="col hover-card "><a href="/reference/device-setup/viam-rover/fragments/"><div ><div>Configure your Viam Rover</div><p>Configure your rover by adding the Viam-provided configuration fragment to your rover.</p></div>
    </a></div>

</div>
</div>

After you have configured your rover, follow this tutorial:

<div class="card-container">
  <div class="row-no-margin">
<div class="col hover-card "><a href="/tutorials/control/drive-rover/"><div class="hover-card-video">
          
          
          
          



  
  
    
    
    
  


  
  
    
    
    
  



<div class="gif">
  <video autoplay loop muted playsinline alt="A Viam Rover driving in a square" width="100%" style="width: 100%" class=" lozad"><source data-src="/tutorials/try-viam-sdk/image1.webm" type="video/webm"><source data-src="/tutorials/try-viam-sdk/image1.mp4" type="video/mp4">There should have been a video here but your browser does not seem to support it.
  </video>
  <noscript>
    <video autoplay loop muted playsinline alt="A Viam Rover driving in a square" width="100%" style="width: 100%" class=""><source data-src="/tutorials/try-viam-sdk/image1.webm" type="video/webm"><source data-src="/tutorials/try-viam-sdk/image1.mp4" type="video/mp4">There should have been a video here but your browser does not seem to support it.
    </video>
  </noscript>
</div></div><div class="small-hover-card-div"class="small-hover-card-div"><div>Drive your rover</div><p>Use a Viam SDK to program a rover to move in a square.</p></div>
    </a></div>

</div>
</div>

### Extensibility

Due to the aluminum chassis and its expandable mounting features, you can extend the Viam Rover.
With it, you can customize your rover by mounting additional sensors, LiDAR, robot arms, or other components.
The following are just a few ideas, but you can expand or modify the rover kit with any components you want:

- For GPS navigation, we support NMEA (using serial and I<sup>2</sup>C) and RTK.
  Make and model don't make a difference as long as you use these protocols.
  See [Movement Sensor Component](/reference/components/movement-sensor/) for more information.
- For LiDAR laser range scanning, we recommend RPlidar (including the A1).
- For robot arms, we tried the [Yahboom DOFBOT robotics arm](https://category.yahboom.net/products/dofbot-jetson_nano) with success.

### Mount an RPlidar to the rover

If you are mounting an RPlidar to your rover, be sure to position the RPlidar so that it faces forward in the direction of travel, facing in the same direction as the included webcam.
For example, if you are using the [RPlidar A1](https://www.slamtec.com/en/Lidar/A1) model, mount it to the Rover so that the pointed end of the RPlidar mount housing points in the direction of the front of the Rover.
This ensures that the generated SLAM map is oriented in the expected direction relative to the Rover, with the top of the generated map corresponding to the direction the RPlidar is facing when you initiate mapping.

If you need a mount plate for your RPlidar A1 model, you can 3D print an adapter plate using the following:

- [RPlidar A1 adapter STL](https://github.com/viamrobotics/Viam-Rover-2/blob/main/CAD/RPIidar_adapter_v2.STL)

