# Glossary

Viam terms in my own words. Rewrite these as understanding improves.

- **Machine** — A physical device (robot, sensor rig, computer) managed through Viam. Has a config in the Viam app and runs `viam-server`.
- **viam-server** — The process that runs on the machine, reads its config, and exposes components and services over an API.
- **Component** — A driver for a piece of hardware: board, motor, camera, sensor, arm, etc.
- **Service** — Higher-level software capability: data management, vision, motion planning, SLAM, ML model, etc.
- **Resource** — The umbrella term for any component or service.
- **Module** — A packaged, versioned add-on (from the registry or custom) that provides components or services not built into viam-server.
- **Registry** — Viam's catalog of modules and ML models.
- **Fragment** — A reusable chunk of machine config that can be shared across many machines.
- **Organization / Location** — How machines are grouped in the Viam app for access control and fleet management.
- **SDK** — Client library (Python, Go, TypeScript, and others) for talking to a machine's resources from your own code.
- **Arm** — A component representing a robotic arm; exposes joint positions and end-effector pose.
- **Gripper** — A component with open/grab operations, attached to the arm as the end effector.
- **Frame system** — Viam's model of where every component sits relative to the others and to the `world` frame. Lets you express a position once and have it make sense for the camera, the arm, and the gripper.
- **Pose / PoseInFrame** — A position plus orientation. `PoseInFrame` ties it to a named reference frame (for example `cam-1` or `world`).
- **Point cloud** — A set of 3D points, here produced by the vision service from a camera, used to find objects to pick.
- **Vision service** — Detects objects, classifies images, or returns point clouds from a camera, often backed by an ML model.
- **Motion service** — Plans and executes movement of a component (the gripper on the arm) to a destination pose while avoiding obstacles.
- **Model** — one implementation of a component or service type, e.g. `arm/simulated`. All models of a type share the API; the model decides what's behind it.
- **DoCommand** — the escape hatch on every resource for commands the standard API doesn't cover. The pick-station uses it to report grasp and hover poses.
- **Orientation vector** — Viam's orientation format: the direction the tool's z-axis points plus a rotation (theta) about it. `ov_degrees` in the app; `o_x/o_y/o_z/theta` in the SDK.
- **Tool center point** — the flange-to-tool-tip distance (196 mm here) that puts the gripper frame at the point that touches the work.
- **WorldState** — the set of obstacles passed to a single motion service call. Each obstacle is a geometry in a named frame; `world` makes it fixed, the gripper frame makes it move with the arm.
- **Scene store vs planner** — the 3D scene draws whatever you tell it (via the pack-sequencer); the planner only avoids what you pass in a WorldState. The two are not linked.
- **API key** — Credential used by SDK code and the CLI to authenticate to a machine or organization. Keep out of git.
