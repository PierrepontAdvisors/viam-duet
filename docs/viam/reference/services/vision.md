# Vision service configuration

Configuration reference for built-in vision service models: mlmodel, color_detector, and detections-to-segments.
> Source: https://docs.viam.com/reference/services/vision/


The vision service has three built-in models with distinct configuration shapes:

<div class="card-container">
  <div class="row-no-margin">
<div class="col hover-card "><a href="/reference/services/vision/mlmodel/"><div class="hover-card-img">




    
    
    
<picture>

  
  
<source srcset="/services/vision/dog-detector_hu_dcb4fabeb8a1f027.webp" type="image/webp">
<img src="/services/vision/dog-detector.png" alt="mlmodel" class="" id="" style="" loading="lazy">
  

</picture>

</div><div class="small-hover-card-div"><div>mlmodel</div><p>Configure the mlmodel vision service to turn a deployed ML model into a detector, classifier, or 3D segmenter.</p></div>
    </a></div>

<div class="col hover-card "><a href="/reference/services/vision/color_detector/"><div class="hover-card-img">




    
    
    
<picture>

  
  
<source srcset="/services/vision/dog-detector_hu_dcb4fabeb8a1f027.webp" type="image/webp">
<img src="/services/vision/dog-detector.png" alt="color_detector" class="" id="" style="" loading="lazy">
  

</picture>

</div><div class="small-hover-card-div"><div>color_detector</div><p>Configure the color_detector vision service to find regions of a specific hue in camera images. No ML model required.</p></div>
    </a></div>

<div class="col hover-card "><a href="/reference/services/vision/detections-to-segments/"><div ><div>detections-to-segments</div><p>Project 2D detections into 3D point cloud segments using a depth camera&#39;s intrinsic parameters.</p></div>
    </a></div>

</div>
</div>

For API method reference (`GetDetections`, `GetClassifications`, `GetObjectPointClouds`, `CaptureAllFromCamera`, `GetProperties`), see [Vision service API](/reference/apis/services/vision/).

