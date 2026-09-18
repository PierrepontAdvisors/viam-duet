# Tutorials catalog

> Worked examples and walkthroughs. Several are hosted outside this site (codelabs.viam.com, viam.com/post/*) -- that's not a mistake, follow the link. Not part of the site structure in sitetree.json: many tutorials apply across several hardware/software combinations at once and don't fit a single-parent hierarchy.

- [Control a motor in 2 minutes](https://docs.viam.com/tutorials/control/control-motor/): Use Viam to control a motor's speed and direction in just a few steps.
  `level: Beginner · languages: python, go, typescript, flutter, c++ · components/services: motor`
- [Build an Outdoor Rover: Simple, Useful and Affordable](https://www.viam.com/post/build-an-outdoor-rover): Build and control an affordable, functional outdoor rover (choose 3).
  `level: Intermediate · components/services: board, motor, base, camera`
- [Plan motion with an arm and gripper](https://docs.viam.com/tutorials/services/plan-motion-with-arm-gripper/): Use the motion service to move a robot arm and gripper.
  `level: Intermediate · languages: python, go · components/services: arm, gripper, motion, frame_system`
- [Vision-guided pick-and-place with the xArm6](https://docs.viam.com/tutorials/pick-and-place/): Build a vision-guided robot that detects blocks by shape and places them into a bin with motion planning, from manual control to programming an autonomous workflow in Python.
  `level: Intermediate · languages: python · components/services: arm, gripper, camera, vision, motion, frame_system, switch`
- [Add constraints and transforms to a motion plan](https://docs.viam.com/tutorials/services/constrain-motion/): Use constraints and transforms with the motion service.
  `level: Intermediate · languages: python · components/services: arm, gripper, motion, frame_system`
- [Dip apples in honey with Shana ToBot](https://codelabs.viam.com/guide/shana-tobot/index.html): This tutorial will walk you through making your own vending machine from scratch, along with a web application that allows you to operate your machine from any device.
  `level: Intermediate · components/services: arm`
- [Make your own sticker vending machine](https://codelabs.viam.com/guide/sticker-wizard/index.html): This tutorial will walk you through making your own vending machine from scratch, along with a web application that allows you to operate your machine from any device.
  `level: Intermediate · components/services: servo, motor, board`
- [Set up people detection notifications in Home Assistant](https://codelabs.viam.com/guide/home-assistant/index.html): Learn how to install the integration through the Home Assistant Community Store (HACS) and use a vision service to detect people from a camera connected to Home Assistant.
  `level: Intermediate · components/services: mlmodel, vision, camera`
- [Use a QR code scanner](https://codelabs.viam.com/guide/qrcode/index.html): Learn how to use a QR code scanner to detect and decode QR codes using a Viam module. We'll leverage the pyzbar and OpenCV Python libraries to process images from a camera and extract information encoded in QR codes.
  `level: Intermediate · components/services: camera, vision`
- [Use an AprilTag scanner](https://codelabs.viam.com/guide/apriltag/index.html): Learn how to detect and decode AprilTags using a Viam module. We'll leverage the apriltag and OpenCV Python libraries to process images from a camera and extract information encoded in AprilTags.
  `level: Intermediate · components/services: camera, vision`
- [Use Sensor Data with Webhooks and Elastic Cloud](https://codelabs.viam.com/guide/monitoring-automation-elastic/index.html): Learn how to continually index sensor data from Viam into Elasticsearch and display an alert in the real world.
  `level: Intermediate · components/services: sensor, board, movement_sensor, data_manager`
- [Automate air filtration with air quality sensors](https://codelabs.viam.com/guide/air-quality/index.html): Use Viam to automate an air filtration system using air quality sensors and an air filter attached to a box fan.
  `level: Intermediate · components/services: board, sensor, generic`
- [Drive a rover using TypeScript](https://codelabs.viam.com/guide/drive-rover-ts/): Drive a rover in a square using the Viam TypeScript SDK.
  `level: Beginner · components/services: base`
- [Plant Watering Device Workshop](https://codelabs.viam.com/guide/plant-watering-device-workshop/index.html): Learn how to physically assemble a functional plant watering device by connecting and wire the components and code the machine.
  `level: Intermediate · languages: python · components/services: sensor, board`
- [Working with Python environment variables](https://codelabs.viam.com/guide/environment-variables/index.html): Learn how to use Python variables with Viam projects so your code runs smoothly from development to deployment.
  `level: Intermediate`
- [Postman tutorial for Viam's gRPC APIs](https://codelabs.viam.com/guide/postman-grpc-apis/index.html): You can use the Viam web app or SDKS to control your machines, but you can also use Viam's gRPC APIs directly.
  `level: Intermediate · components/services: base`
- [Monitor Air Quality with a Fleet of Sensors](https://docs.viam.com/tutorials/control/air-quality-fleet/): Configure a fleet of machines to capture air quality sensor data across different locations.
  `level: Intermediate · languages: typescript · components/services: sensor, data_manager`
- [Monitor Job Site Helmet Usage with Computer Vision](https://docs.viam.com/tutorials/projects/helmet/): Use computer vision to detect problems such as people not wearing safety gear and get email alerts.
  `level: Intermediate · components/services: camera, data_manager, mlmodel, vision`
- [Build a Flutter App that Integrates with Viam](https://docs.viam.com/tutorials/control/flutter-app/): Use Viam's Flutter SDK to build a custom mobile app to show your machines and their components.
  `level: Intermediate · languages: flutter`
- [A security system based on face identification](https://docs.viam.com/tutorials/projects/verification-system/): Create an alarm system that can detect people and recognize faces, allowing it to intelligently trigger alarms.
  `level: Intermediate · components/services: mlmodel, vision, camera`
- [Build a Bedtime Songs Bot with a Custom ML Model](https://www.viam.com/post/bedtime-songs-bot): Create a robot babysitter with a webcam and machine learning.
  `level: Intermediate · languages: python · components/services: camera, sensor, mlmodel, vision`
- [Build a Robotic Claw Game with a Raspberry Pi](https://docs.viam.com/tutorials/projects/claw-game/): Create your own version of the famous arcade claw machine using a robotic arm and a claw grabber.
  `level: Advanced · languages: python, typescript · components/services: board, arm, gripper, motion, frame_system`
- [Build a Confetti Bot with a Raspberry Pi](https://www.viam.com/post/confetti-bot): Use a red button to activate a GPIO pin on the board and make a confetti popper go off.
  `level: Beginner · languages: python · components/services: board, motor`
- [Tipsy: Create an Autonomous Drink Carrying Robot](https://www.viam.com/post/autonomous-drink-carrying-robot): Create an autonomous drink carrying robot with motion sensing and machine learning.
  `level: Intermediate · languages: python · components/services: board, motor, base, camera, sensor, mlmodel, vision`
- [Create a Lazy Susan Using a DC Motor](https://www.viam.com/post/lazy-susan): Wire a DC motor to a board, attach a plate on top, and control the motor to rotate the plate.
  `level: Beginner · languages: python · components/services: board, motor`
- [Control a Robot Dog with a Custom Viam Base Component](https://docs.viam.com/tutorials/custom/custom-base-dog/): Integrate a custom base component with the Viam Python SDK.
  `level: Intermediate · languages: python · components/services: base, camera, custom`
- [A Guardian that Tracks Pets using a Pi, Camera, and Servo](https://docs.viam.com/tutorials/projects/guardian/): Make a functional guardian with a servo motor, some LEDs, a camera, and the ML Model and vision service to detect people and pets.
  `level: Intermediate · languages: python · components/services: camera, vision, servo, mlmodel`
- [Modernize a 1980s Robot](https://www.viam.com/post/modernize-a-1980s-robot): Modernize the Omnibot 2000 from the 1980s with Viam and AI.
  `level: Intermediate · components/services: board, motor, base, camera`
- [A Person Detection Security Robot That Sends You Photos](https://docs.viam.com/tutorials/projects/send-security-photo/): Use the vision service and the Python SDK to send yourself a text message when your webcam detects a person.
  `level: Intermediate · languages: python · components/services: camera, mlmodel, vision`
- [Build a Smart Pet Feeder with Machine Learning](https://www.viam.com/post/smart-pet-feeder): Use a Raspberry Pi, a motor, and machine learning to build a smart pet feeder.
  `level: Intermediate · languages: python · components/services: board, camera, motor, mlmodel, vision`
- [Use Object Detection to Turn Your Lights On](https://www.viam.com/post/object-detection-turn-your-lights-on): How to turn a light on when your webcam sees a person.
  `level: Intermediate · languages: python · components/services: camera, mlmodel, vision`
- [Plant Watering Machine with a Raspberry Pi](https://docs.viam.com/tutorials/projects/make-a-plant-watering-robot/): Create a plant watering machine with a Raspberry Pi.
  `level: Intermediate · languages: python · components/services: board, motor, sensor, module`
- [Integrate Viam with ChatGPT to Create a Companion Robot](https://docs.viam.com/tutorials/projects/integrating-viam-with-openai/): Harness AI and use ChatGPT to add life to your Viam rover and turn it into a companion robot.
  `level: Intermediate · languages: python · components/services: custom, servo, board, mlmodel, vision, speech`
- [Drive a rover in a square in 2 minutes](https://docs.viam.com/tutorials/control/drive-rover/): Use a Viam SDK to program a rover to move in a square.
  `level: Beginner · languages: python, go, typescript, cpp, flutter · components/services: base`
- [Foam Dart Launcher Robot Tutorial](https://www.viam.com/post/foam-dart-launcher): Build a foam dart launcher with a wheeled rover and a Raspberry Pi.
  `level: Intermediate · languages: python · components/services: base, camera, motor, board`
- [Build a Line Follower with a Rover and a Webcam](https://codelabs.viam.com/guide/linefollower/index.html): Build a line-following robot that relies on a webcam and color detection.
  `level: Intermediate · languages: python · components/services: vision, camera, base`
- [Drive a Rover (like SCUTTLE or Yahboom) Using a Gamepad](https://docs.viam.com/tutorials/control/gamepad/): Drive a wheeled rover with a Bluetooth gamepad that has a dongle.
  `level: Intermediate · components/services: base, input_controller, base_remote_control`
- [Configure a Rover like Yahboom or SCUTTLE](https://docs.viam.com/tutorials/configure/configure-rover/): Configure a rover like the a Yahboom 4WD Rover or a SCUTTLE robot on the Viam platform.
  `level: Beginner · languages: python, go · components/services: board, motor, camera, base, encoder`
