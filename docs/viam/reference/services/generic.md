# Generic service

A service that does not fit any of the other APIs.
> Source: https://docs.viam.com/reference/services/generic/


The _generic_ service API enables you to add support for unique types of services that do not already have an [appropriate API](/reference/apis/#service-apis) defined for them.

For example, when writing code to manage simultaneous localization and mapping (SLAM) for your machine, it makes sense to use the existing SLAM API, which provides specific functionality required for generating accurate maps of an environment.
However, if you want to create a new service to monitor your machine's CPU and RAM usage for example, you need very different functionality that isn't currently exposed in any API.
Instead, you can use the generic service API to add support for your unique type of service, like local system monitoring, to your machine.

Use generic for a [modular resource](/reference/glossary/#term-modular-resource)
 model that represents a unique type of service.
If you are adding support for unique or proprietary hardware, rather than adding new high-level software functionality, use the [generic component](/reference/components/generic/) instead.

There are no built-in generic service models (other than `fake`).

> **Important:**
> 
> The generic service API only supports the `DoCommand` method.
> If you use the generic API, your module needs to define any and all service functionality and pass it through `DoCommand`.
> 
> Whenever possible, it is best to use an [existing service API](/reference/apis/services/) instead of generic so that you do not have to replicate code.
> If you want to use most of an existing API but need just a few other functions, try using the `DoCommand` endpoint and extra parameters to add custom functionality to an existing API, instead of using the generic service.

## Configuration

<p>For configuration information, click on the model name:
</p>

<div class="search-container" data-unique-id="rdkservicegeneric-generic">
  <div id="searchbox-rdkservicegeneric-generic" class="searchbox"></div><br>
  <div id="searchstats-rdkservicegeneric-generic" class="searchstats"></div></p>
  <div class="searchhitsbox mr-component" id="rdk:service:generic">
    <span>
      <div class="modellistheader">
        <div class="name">Model</div>
        <div>Description</div>
      </div>
      <div id="hits-rdkservicegeneric-generic" class="hits modellist"></div>
    </span>
    <div id="pagination-rdkservicegeneric-generic" class="pagination"></div>
  </div>
</div>
<noscript>
  <div class="alert alert-caution" role="alert">
      <h4 class="alert-heading">Javascript</h4>
      <p>Please enable javascript to see and search models.</p>
  </div>
</noscript>

{{< alert title="Add support for other models" color="tip" >}}
If none of the existing models fit your use case, you can [create a {{< glossary_tooltip term_id="modular-resource" text="modular resource" >}}](/build-modules/write-a-driver-module/) to add support for it.
{{< /alert >}}


## API

The [generic service API](/reference/apis/services/generic/) supports the following method:

<!-- prettier-ignore -->
| Method Name | Description |
| ----------- | ----------- |
| [`DoCommand`](/reference/apis/services/generic/#docommand) | Execute model-specific commands. |
| [`GetStatus`](/reference/apis/services/generic/#getstatus) | Get the current status of the generic service as a map of key-value pairs describing its state. |
| [`GetResourceName`](/reference/apis/services/generic/#getresourcename) | Get the `ResourceName` for this instance of the generic service. |
| [`Close`](/reference/apis/services/generic/#close) | Safely shut down the resource and prevent further use. |


## Troubleshooting

You can find additional assistance in the [Troubleshooting section](/monitor/troubleshoot/).

You can also ask questions in the [Community Discord](https://discord.gg/viam) and we will be happy to help.


