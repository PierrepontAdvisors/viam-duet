# Configure your Viam Rover with a fragment

Configure your rover by adding the Viam-provided configuration fragment to your rover.
> Source: https://docs.viam.com/reference/device-setup/viam-rover/fragments/


To be able to drive your rover, you need to configure it.
Viam provides reusable [*fragments*](/manage/fleet/reuse-configuration/)
 for [Viam rovers](https://www.viam.com/resources/rover).

## Prerequisites

- An assembled Viam Rover.
  For assembly instructions, see [Unbox and set up your Viam Rover](/reference/device-setup/viam-rover/setup/)
- The board is connected to Viam.
  To add your Pi to Viam, refer to [the rover setup guide](/reference/device-setup/viam-rover/setup/#control-your-rover-on-viam).

## Add the fragment

Follow the appropriate instructions for the model of rover and board you have:




### Viam Rover 2 (RPi 5)

Navigate to your machine’s page.
In the left-hand menu of the **CONFIGURE** tab, click the **+** (Create) icon next to the machine [part](/reference/glossary/part/)
you want to add the fragment to.

Select **Insert fragment**.
Now, you can see the available fragments to add.
Select [`ViamRover2-2024-rpi5`](https://app.viam.com/fragment/11d1059b-eaed-4ad8-9fd8-d60ad7386aa2/json) and click **Insert fragment** again to add the fragment to your machine configuration:

<picture>
<source srcset="/appendix/try-viam/rover-resources/fragments/fragments_list_hu_62ba278867b654a.webp" type="image/webp">
<img src="/appendix/try-viam/rover-resources/fragments/fragments_list.png" alt="List of available fragments" class="shadow" id="" style="width: 500px" loading="lazy">
</picture>
Click **Save** in the upper right corner of the page to save your new configuration.

The fragment adds the following components to your machine’s JSON configuration:

<ul>
<li>A [board component](/reference/components/board/) named `local` representing the Raspberry Pi.</li>
<li>Two [motors](/reference/components/motor/gpio/) (`right` and `left`)
<ul>
<li>The configured pin numbers correspond to where the motor drivers are connected to the board.</li>
</ul>
</li>
<li>Two [encoders](/reference/components/encoder/single/), one for each motor</li>
<li>A wheeled [base](/reference/components/base/), an abstraction that coordinates the movement of the right and left motors
<ul>
<li>Width between the wheel centers: 356 mm</li>
<li>Wheel circumference: 381 mm</li>
<li>Spin slip factor: 1</li>
</ul>
</li>
<li>A webcam [camera](/reference/components/camera/webcam/)</li>
<li>An [accelerometer](https://github.com/viam-modules/tdk-invensense/)</li>
<li>A [power sensor](https://github.com/viam-modules/texas-instruments/)</li>
</ul>
For information about how to configure components yourself when you are not using the fragment, click the links on each component above.
To see the configured pin numbers and other values specific to this fragment, [view it in the app](https://app.viam.com/fragment?id=11d1059b-eaed-4ad8-9fd8-d60ad7386aa2).

### Viam Rover 2 (RPi 4)

Navigate to your machine’s page.
In the left-hand menu of the **CONFIGURE** tab, click the **+** (Create) icon next to the machine [part](/reference/glossary/part/)
you want to add the fragment to.

Select **Insert fragment**.
Now, you can see the available fragments to add.
Select [`ViamRover2-2024-rpi4-a`](https://app.viam.com/fragment/7c413f24-691d-4ae6-a759-df3654cfe4c8/json) and click **Insert fragment** again to add the fragment to your machine configuration:

<picture>
<source srcset="/appendix/try-viam/rover-resources/fragments/fragments_list_hu_62ba278867b654a.webp" type="image/webp">
<img src="/appendix/try-viam/rover-resources/fragments/fragments_list.png" alt="List of available fragments" class="shadow" id="" style="width: 500px" loading="lazy">
</picture>
Click **Save** in the upper right corner of the page to save your new configuration.

The fragment adds the following components to your machine’s JSON configuration:

<ul>
<li>A [board component](/reference/components/board/) named `local` representing the Raspberry Pi.</li>
<li>Two [motors](/reference/components/motor/gpio/) (`right` and `left`)
<ul>
<li>The configured pin numbers correspond to where the motor drivers are connected to the board.</li>
</ul>
</li>
<li>Two [encoders](/reference/components/encoder/single/), one for each motor</li>
<li>A wheeled [base](/reference/components/base/), an abstraction that coordinates the movement of the right and left motors
<ul>
<li>Width between the wheel centers: 356 mm</li>
<li>Wheel circumference: 381 mm</li>
<li>Spin slip factor: 1</li>
</ul>
</li>
<li>A webcam [camera](/reference/components/camera/webcam/)</li>
<li>An [accelerometer](https://github.com/viam-modules/tdk-invensense/)</li>
<li>A [power sensor](https://github.com/viam-modules/texas-instruments/)</li>
</ul>
For information about how to configure components yourself when you are not using the fragment, click the links on each component above.
To see the configured pin numbers and other values specific to this fragment, [view it in the app](https://app.viam.com/fragment?id=7c413f24-691d-4ae6-a759-df3654cfe4c8).

### Viam Rover 1 (RPi 4)

Navigate to your machine’s page.
In the left-hand menu of the **CONFIGURE** tab, click the **+** (Create) icon next to the machine [part](/reference/glossary/part/)
you want to add the fragment to.

Select **Insert fragment**.
Now, you can see the available fragments to add.
Select [`ViamRover202210b`](https://app.viam.com/fragment/3e8e0e1c-f515-4eac-8307-b6c9de7cfb84/json) and click **Insert fragment** again to add the fragment to your machine configuration:

<picture>
<source srcset="/appendix/try-viam/rover-resources/fragments/fragments_list_hu_62ba278867b654a.webp" type="image/webp">
<img src="/appendix/try-viam/rover-resources/fragments/fragments_list.png" alt="List of available fragments" class="shadow" id="" style="width: 500px" loading="lazy">
</picture>
Click **Save** in the upper right corner of the page to save your configuration.

The fragment adds the following components to your machine’s JSON configuration:

<ul>
<li>A [board component](/reference/components/board/) named `local` representing the Raspberry Pi
<ul>
<li>An I<sup>2</sup>C bus for connection to the accelerometer.</li>
</ul>
</li>
<li>Two [motors](/reference/components/motor/gpio/) (`right` and `left`)
<ul>
<li>The configured pin numbers correspond to where the motor drivers are connected to the board.</li>
</ul>
</li>
<li>Two [encoders](/reference/components/encoder/single/), one for each motor</li>
<li>A wheeled [base](/reference/components/base/), an abstraction that coordinates the movement of the right and left motors
<ul>
<li>Width between the wheel centers: 260 mm</li>
<li>Wheel circumference: 217 mm</li>
<li>Spin slip factor: 1</li>
</ul>
</li>
<li>A webcam [camera](/reference/components/camera/webcam/)</li>
<li>An [accelerometer](https://github.com/viam-modules/analog-devices/)</li>
</ul>
<blockquote>
**Info:**

This particular motor driver has pins labeled “ENA” and “ENB.”
Typically, this would suggest that they should be configured as enable pins, but on this specific driver these function as PWM pins, so we configure them as such.

</blockquote>
For information about how you would configure a component yourself if you weren’t using the fragment, click the links on each component above.
To see the configured pin numbers and other values specific to this fragment, [view it in the app](https://app.viam.com/fragment?id=3e8e0e1c-f515-4eac-8307-b6c9de7cfb84).

### Viam Rover 2 (Jetson Nano)

Navigate to your machine’s page.
In the left-hand menu of the **CONFIGURE** tab, click the **+** (Create) icon next to the machine [part](/reference/glossary/part/)
you want to add the fragment to.

Select **Insert fragment**.
Now, you can see the available fragments to add.
Select [`ViamRover2-2024-jetson-nano-a`](https://app.viam.com/fragment/747e1f43-309b-4311-b1d9-1dfca45bd097/json) and click **Insert fragment** again to add the fragment to your machine configuration.

<picture>
<source srcset="/appendix/try-viam/rover-resources/fragments/fragments_list_hu_62ba278867b654a.webp" type="image/webp">
<img src="/appendix/try-viam/rover-resources/fragments/fragments_list.png" alt="List of available fragments" class="shadow" id="" style="width: 500px" loading="lazy">
</picture>
Click **Save** in the upper right corner of the page to save your new configuration.

The fragment adds the following components to your machine’s JSON configuration:

<ul>
<li>A [board component](/reference/components/board/) named `local` representing the Jetson.</li>
<li>Two [motors](/reference/components/motor/gpio/) (`right` and `left`)
<ul>
<li>The configured pin numbers correspond to where the motor drivers are connected to the board.</li>
</ul>
</li>
<li>Two [encoders](/reference/components/encoder/single/), one for each motor</li>
<li>A wheeled [base](/reference/components/base/), an abstraction that coordinates the movement of the right and left motors
<ul>
<li>Width between the wheel centers: 356 mm</li>
<li>Wheel circumference: 381 mm</li>
<li>Spin slip factor: 1</li>
</ul>
</li>
<li>A webcam [camera](/reference/components/camera/webcam/)</li>
<li>An [accelerometer](https://github.com/viam-modules/tdk-invensense/)</li>
<li>A [power sensor](https://github.com/viam-modules/texas-instruments/)</li>
</ul>
For information about how to configure components yourself when you are not using the fragment, click the links on each component above.
To see the configured pin numbers and other values specific to this fragment, [view it in the app](https://app.viam.com/fragment?id=747e1f43-309b-4311-b1d9-1dfca45bd097).

### Viam Rover 2 (Jetson Orin Nano)

Navigate to your machine’s page.
In the left-hand menu of the **CONFIGURE** tab, click the **+** (Create) icon next to the machine [part](/reference/glossary/part/)
you want to add the fragment to.

Select **Insert fragment**.
Now, you can see the available fragments to add.
Select [`ViamRover2-2024-nano-orin-a`](https://app.viam.com/fragment/6208e890-8400-4197-bf0f-e8ddeca4e157/json) and click **Insert fragment** again to add the fragment to your machine configuration:

<picture>
<source srcset="/appendix/try-viam/rover-resources/fragments/fragments_list_hu_62ba278867b654a.webp" type="image/webp">
<img src="/appendix/try-viam/rover-resources/fragments/fragments_list.png" alt="List of available fragments" class="shadow" id="" style="width: 500px" loading="lazy">
</picture>
Click **Save** in the upper right corner of the page to save your new configuration.

The fragment adds the following components to your machine’s JSON configuration:

<ul>
<li>A [board component](/reference/components/board/) named `local` representing the Jetson.</li>
<li>Two [motors](/reference/components/motor/gpio/) (`right` and `left`)
<ul>
<li>The configured pin numbers correspond to where the motor drivers are connected to the board.</li>
</ul>
</li>
<li>Two [encoders](/reference/components/encoder/single/), one for each motor</li>
<li>A wheeled [base](/reference/components/base/), an abstraction that coordinates the movement of the right and left motors
<ul>
<li>Width between the wheel centers: 356 mm</li>
<li>Wheel circumference: 381 mm</li>
<li>Spin slip factor: 1</li>
</ul>
</li>
<li>A webcam [camera](/reference/components/camera/webcam/)</li>
<li>An [accelerometer](https://github.com/viam-modules/tdk-invensense/)</li>
<li>A [power sensor](https://github.com/viam-modules/texas-instruments/)</li>
</ul>
For information about how to configure components yourself when you are not using the fragment, click the links on each component above.
To see the configured pin numbers and other values specific to this fragment, [view it in the app](https://app.viam.com/fragment?id=6208e890-8400-4197-bf0f-e8ddeca4e157).



## See the components on the configuration page

Adding a fragment to your machine adds the configuration to your machine.
The components and services included in the fragment will now appear as cards on the **CONFIGURE** tab, along with a card for your fragment:






    
    
    
<picture>

  
  
<source srcset="/appendix/try-viam/rover-resources/fragments/fragments_cards_hu_71a7a1ca9f41db68.webp" type="image/webp">
<img src="/appendix/try-viam/rover-resources/fragments/fragments_cards.png" alt="List of available fragments" class="shadow" id="" style="width: 500px" loading="lazy">
  

</picture>




## Modify the config

The fragment you added is read-only, but if you need to modify your rover's config you can [overwrite sections of the fragment](/fleet/reuse-configuration/#override-specific-settings).

## Next steps

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

