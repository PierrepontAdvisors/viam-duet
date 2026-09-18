# Deploy and maintain ML models

Deploy a pre-trained or custom ML model to a machine, retrain when accuracy drops, roll out new versions to a fleet, and run batch inference against stored images.
> Source: https://docs.viam.com/vision/deploy-and-maintain/


The model is the artifact at the center of every vision pipeline. Deploy one from the registry or bring your own, roll out new versions as you retrain, and validate models against stored data before they go live.

<div class="card-container">
  <div class="row-no-margin">
<div class="col hover-card "><a href="/vision/deploy-and-maintain/available-models/"><div ><div>What&#39;s in the registry</div><p>Three kinds of registry entries feed a vision pipeline: ML model service implementations, vision service models, and public ML models. How to pick among them.</p></div>
    </a></div>

<div class="col hover-card "><a href="/vision/deploy-and-maintain/deploy-from-registry/"><div ><div>Deploy a model from the registry</div><p>Pick a pre-trained ML model from the Viam registry, deploy it to your machine, and wire it through an ML model service so a vision service can use it.</p></div>
    </a></div>

<div class="col hover-card "><a href="/vision/deploy-and-maintain/deploy-custom-model/"><div ><div>Deploy a custom model</div><p>Deploy a model you trained outside Viam (or trained yourself on Viam data) through an ML model service and use it with the vision service.</p></div>
    </a></div>

<div class="col hover-card "><a href="/vision/deploy-and-maintain/retrain/"><div ><div>Retrain a model</div><p>Close the loop when a vision model&#39;s accuracy drops in production: capture the failing images, label them, retrain, and redeploy a new model version to one or many machines.</p></div>
    </a></div>

<div class="col hover-card "><a href="/vision/deploy-and-maintain/roll-out-to-fleet/"><div ><div>Roll out to a fleet</div><p>Update a vision model across many machines at once using fragments and model version pinning. Short guide with links to the full fleet and deployment docs.</p></div>
    </a></div>

<div class="col hover-card "><a href="/vision/deploy-and-maintain/batch-inference/"><div ><div>Run batch inference</div><p>Use the viam infer CLI command to run a deployed ML model against images already captured to the Viam Cloud. Useful for labeling assistance, dataset validation, and running large or GPU-only models.</p></div>
    </a></div>

</div>
</div>

