# Train ML models

Create datasets from captured images and train ML models for classification or object detection.
> Source: https://docs.viam.com/train/overview/


Your machines capture images in the field. ML model training turns those images
into models that can classify what a camera sees or detect specific objects in
real time. Viam handles the training infrastructure so you can focus on your
data and your use case.

## The training workflow

Training an ML model follows a repeating cycle:

1. **Create a dataset.** Collect images from your machines into a named,
   organization-level collection. You can pull images from multiple machines
   across different locations into a single dataset.

2. **Label your images.** Tag images for classification (the whole image gets a
   label) or draw bounding boxes for object detection (each object in the image
   gets a labeled rectangle). You can label manually or use an existing model to
   auto-annotate and review predictions.

3. **Train a model.** Submit a training job and Viam runs it on cloud
   infrastructure. No GPU provisioning, no framework installation. When
   training completes, the model is stored in your organization's registry.

4. **Deploy to your machine.** Configure the appropriate ML model service on
   your machine (for example, `tflite_cpu` for TFLite models). Add a vision
   service to apply the model to live camera frames. The machine pulls the
   model from the registry automatically.

5. **Iterate.** Deploy the model, collect data on its predictions,
   auto-annotate new images with the current model, review the predictions,
   retrain, and redeploy. Each cycle tightens the feedback loop and improves
   accuracy. In ML this is called active learning.

## Scale labeling with auto-predictions

Once you have a working model, you do not have to label every new image by
hand. Use [auto-predictions](/train/automate-annotation/) to have an existing
model draft tags or bounding boxes for a dataset, then review the suggestions.

A typical active-learning loop:

1. Hand-label a starter dataset (20-50 images per class).
2. Train an initial model.
3. Capture more images from your machines.
4. Run auto-predictions against the new images using your initial model.
5. Accept or reject each prediction to produce verified labels.
6. Retrain with the expanded dataset.

This turns a small labeling effort into a growing, self-improving dataset.

## Supported frameworks and hardware

Viam's managed training handles TFLite and TensorFlow directly. For PyTorch,
ONNX, or other frameworks, write a [custom training script](/train/custom-training-scripts/).

| Framework                                          | How to train                      | ML model service                                                                                                                                | Hardware                                             |
| -------------------------------------------------- | --------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------- |
| [TensorFlow Lite](https://www.tensorflow.org/lite) | Managed training                  | [`tflite_cpu`](https://app.viam.com/module/viam/tflite_cpu)                                                                                     | linux/amd64, linux/arm64, darwin/arm64, darwin/amd64 |
| [TensorFlow](https://www.tensorflow.org/)          | Managed training or custom script | [`tensorflow-cpu`](https://app.viam.com/module/viam/tensorflow-cpu), [`triton`](https://app.viam.com/module/viam/mlmodelservice-triton-jetpack) | Nvidia GPU, linux/amd64, linux/arm64, darwin/arm64   |
| [PyTorch](https://pytorch.org/)                    | Custom script                     | [`torch-cpu`](https://app.viam.com/module/viam/torch-cpu), [`triton`](https://app.viam.com/module/viam/mlmodelservice-triton-jetpack)           | Nvidia GPU, linux/arm64, darwin/arm64                |
| [ONNX](https://onnx.ai/)                           | Custom script                     | [`onnx-cpu`](https://app.viam.com/module/viam/onnx-cpu), [`triton`](https://app.viam.com/module/viam/mlmodelservice-triton-jetpack)             | Nvidia GPU, linux/amd64, linux/arm64, darwin/arm64   |

**TFLite** produces compact models optimized for edge devices without a GPU,
and is the right choice for most Viam use cases. **TensorFlow** produces
larger models that require more compute. Use **PyTorch** or **ONNX** when you
are importing an existing model or need framework-specific features not
available in TensorFlow.

Custom training scripts currently run in TensorFlow-based containers. You can
install additional Python dependencies through `setup.py`. See
[custom training scripts](/train/custom-training-scripts/) for details.

## Task types

The task type determines what the model learns to do. It must match how you
labeled your dataset.






    
    
    
<picture>

  
  
<source srcset="/train/task-types_hu_9f8a26f30f76fb1f.webp" type="image/webp" width="1232" height="400">
<img src="/train/task-types.png" width="1232" height="400" alt="Three task type cards from the Viam training wizard: single label classification, multi label classification, and object detection." class="shadow imgzoom" id="" style="" loading="lazy">
  

</picture>




- **Single label classification** assigns exactly one label to each image. Your
  dataset should have tags with exactly one tag per image.
- **Multi label classification** assigns one or more labels to each image. Your
  dataset should have tags, and images may have multiple tags.
- **Object detection** finds objects in an image and draws bounding boxes around
  them with labels. Your dataset should have bounding box annotations.

## Automatic deployment

When training completes, the model is stored in your organization's registry.
If a machine is already configured to use that model, Viam automatically
deploys the new version. The machine pulls the latest version the next time it
checks for updates. No manual download or restart is needed.

## Dataset versioning

Each time you train a model from a dataset, Viam snapshots the dataset's
contents at that point. You can continue adding images and labels to a dataset
after training without affecting previously trained models.

<div class="card-container">
  <div class="row-no-margin">
<div class="col hover-card "><a href="/train/create-a-dataset/"><div ><div>Create a dataset</div><p>Create a dataset of images for training an ML model.</p></div>
    </a></div>

<div class="col hover-card "><a href="/train/annotate-images/"><div ><div>Annotate images</div><p>Label images with tags or bounding boxes for training an ML model.</p></div>
    </a></div>

<div class="col hover-card "><a href="/train/automate-annotation/"><div ><div>Automate annotation</div><p>Use ML models to auto-label images and programmatically build annotated datasets.</p></div>
    </a></div>

<div class="col hover-card "><a href="/train/train-a-model/"><div ><div>Train a model</div><p>Train a classification or object detection model from a labeled dataset.</p></div>
    </a></div>

<div class="col hover-card "><a href="/train/deploy-a-model/"><div ><div>Deploy a model</div><p>Add an ML model service and vision service to run a trained model on your machine.</p></div>
    </a></div>

<div class="col hover-card "><a href="/train/custom-training-scripts/"><div ><div>Custom training scripts</div><p>Use or write custom training scripts to train ML models on the Viam platform with any framework or logic.</p></div>
    </a></div>

</div>
</div>

