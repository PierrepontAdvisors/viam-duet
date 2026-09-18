# fake

Reference for the fake camera model on Micro-RDK. Returns a static circle-in-diamond image for testing.
> Source: https://docs.viam.com/reference/components/camera/micro-rdk/fake/


A `fake` camera is a camera model for testing.
The camera always returns the same image, which is an image of a circle inside a diamond.

> **Software requirements:**
> 
> 
> To use this model, you must follow the [Set up an ESP32 guide](/reference/device-setup/setup-micro/#build-and-flash-custom-firmware), which enables you to install and activate the ESP-IDF.
> When you create a new project with `cargo generate`, select the option to include camera module traits when prompted.
> Finish building and flashing custom firmware, then return to this guide.
> 

## Configuration

```json {class="line-numbers linkable-line-numbers"}
{
  "name": "<your-camera-name>",
  "model": "fake",
  "api": "rdk:component:camera",
  "attributes": {}
}
```

