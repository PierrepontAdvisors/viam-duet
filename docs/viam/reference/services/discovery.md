# Discovery service

Use a discovery service to discover available resources on a machine.
> Source: https://docs.viam.com/reference/services/discovery/


A discovery service allows you to return a list of physical hardware available on a machine, and suggest configurations for those components to integrate the hardware into the machine.
If you are [creating a modular resource](/build-modules/write-a-driver-module/) that depends on other [resources](/reference/glossary/#term-resource)
 that are discoverable in a systematic way, you can create a discovery service as part of your module to discover those resources.

## Example usage

Imagine you are creating a vision service module that depends on a camera.
To make it easier for users to configure the camera, you include a discovery service in your module.
You implement the discovery service to report all the camera paths your computer or SBC finds.
Users of your module can then:

1. Configure both the vision service and the discovery service in their machine's configuration.
1. Click the **Test** panel in the discovery service configuration to see all cameras recognized by the machine, presented as a list of configuration snippets.
1. Create a camera with the copy-pasteable configuration snippet for the camera they want to use, with the camera path already filled in.
1. Use the configured camera in their vision service configuration.

To see this in action, see [webcam discovery](/reference/components/camera/webcam/#find-a-video-path-using-a-discovery-service) as an example.

To interact with a discovery service programmatically, use the [discovery service API](/reference/apis/services/discovery/).

## Configuration

To use a discovery service, you need to add it to your machine's configuration.

Go to your machine's **CONFIGURE** page, and add your discovery service.

The following list shows the available discovery service models.
For additional configuration information, click on the model name:




### viam-server

<div class="search-container" data-unique-id="rdkservicediscovery-discovery">
  <div id="searchbox-rdkservicediscovery-discovery" class="searchbox"></div><br>
  <div id="searchstats-rdkservicediscovery-discovery" class="searchstats"></div>

  <div class="searchhitsbox mr-component" id="rdk:service:discovery">
    <span>
      <div class="modellistheader">
        <div class="name">Model</div>
        <div>Description</div>
      </div>
      <div id="hits-rdkservicediscovery-discovery" class="hits modellist"></div>
    </span>
    <div id="pagination-rdkservicediscovery-discovery" class="pagination"></div>
  </div>
</div>
<noscript>
  <div class="alert alert-caution" role="alert">
      <h4 class="alert-heading">Javascript</h4>
      Please enable javascript to see and search models.

  </div>
</noscript>
{{< alert title=“Add support for other models” color=“tip” >}}
If none of the existing models fit your use case, you can [create a {{< glossary_tooltip term_id=“modular-resource” text=“modular resource” >}}](/build-modules/write-a-driver-module/) to add support for it.
{{< /alert >}}

### Micro-RDK

<blockquote>
**Support Notice:**

There is currently no support for this component compatible with the Micro-RDK.

</blockquote>



## API

The [discovery service API](/reference/apis/services/discovery/) supports the following methods:

<!-- prettier-ignore -->
| Method Name | Description |
| ----------- | ----------- |
| [`DiscoverResources`](/reference/apis/services/discovery/#discoverresources) | Get a list of component configs of all resources available to configure on a machine based on the hardware that is connected to or part of the machine. |
| [`GetResourceName`](/reference/apis/services/discovery/#getresourcename) | Get the `ResourceName` for this instance of the service. |
| [`DoCommand`](/reference/apis/services/discovery/#docommand) | Execute model-specific commands. |
| [`GetStatus`](/reference/apis/services/discovery/#getstatus) | Get the current status of the discovery service as a map of key-value pairs describing its state. |
| [`Close`](/reference/apis/services/discovery/#close) | Safely shut down the resource and prevent further use. |


