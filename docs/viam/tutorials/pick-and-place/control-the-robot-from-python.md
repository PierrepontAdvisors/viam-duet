# Phase 4: Control the robot from Python

Connect from your personal computer and drive the saved static pick-and-place sequence from a Python script.
> Source: https://docs.viam.com/tutorials/pick-and-place/control-the-robot-from-python/


In this phase you write and run a Python script on your personal computer that connects to the robot and executes the static pick-and-place sequence from the previous phase. This proves your connection, environment, and named positions work end to end before you add vision feedback.

## Why a script before a module

Everything you did before happened by clicking test cards on the **Control** tab. That is a fine way to verify hardware, but it does not scale: you cannot loop, branch on a sensor reading, or retry a failed grasp from a button. A program script gives you those things, plus fast iteration, a local debugger, and the ability to sprinkle in `print` statements wherever you need visibility into what the robot is doing.

In the next phase, you package this same logic as a module. For now, a script you run from your own terminal, that you can stop, edit, and rerun in seconds, is the faster path to a working pick-and-place loop.

Every control you clicked in the UI maps directly onto an SDK method: the arm card's joint sliders become `Arm` methods, **Grab** and **Open** on the gripper card become `gripper.grab()` and `gripper.open()`, and setting a switch to position 2 becomes `switch.set_position(2)`. Once you can call those methods from code, you can compose them into logic no UI card lets you express by clicking.

## Get the companion project

The workshop's companion repository, [viam-devrel/pick-and-place](https://github.com/viam-devrel/pick-and-place), has a `scripts/` project with a starter script already set up for this phase. Clone or download the repository, then work from the `scripts/` directory:

```sh
git clone https://github.com/viam-devrel/pick-and-place.git
cd pick-and-place/scripts
```

`uv` reads the project's `pyproject.toml` and `.python-version` and resolves `viam-sdk` for you automatically. If you are not using `uv`, pip works as a fallback once you have installed the project's dependencies yourself.

## Connect to your robot

Open `starter-script.py` and find the `connect()` function. It mirrors the boilerplate the Viam app generates for you on the machine's **Connect** tab, under **Python SDK**:

```python
MACHINE_ADDRESS = "<paste from Connect tab>"
API_KEY = "<paste from Connect tab>"
API_KEY_ID = "<paste from Connect tab>"


async def connect() -> RobotClient:
    opts = RobotClient.Options.with_api_key(
        api_key=API_KEY,
        api_key_id=API_KEY_ID,
    )
    return await RobotClient.at_address(MACHINE_ADDRESS, opts)
```

Open the **Connect** tab on your machine's page in the Viam app, select **Python SDK**, toggle **Include API key**, and copy the three values it shows you: the machine address and an API key and key ID pair. Paste them into `MACHINE_ADDRESS`, `API_KEY`, and `API_KEY_ID` at the top of the script. This is the same connection code every Viam Python script starts with.

<!-- ASSET P0 auth-details (UI+): Connect -> Python SDK, connection block with api_key, api_key_id, and machine address boxed in red. See plans/2026-07-02-pick-and-place-shot-list.md -->






    
    
    
<picture>

  
  
<source srcset="/tutorials/pick-and-place/auth-details_hu_1d256ee53d1a81d5.webp" type="image/webp" width="1200" height="678">
<img src="/tutorials/pick-and-place/auth-details.png" width="1200" height="678" alt="The Connect tab showing the Python SDK connection code with the api_key, api_key_id, and machine address boxed in red." class="" id="" style="" loading="lazy">
  

</picture>




The machine address, also known as the "remote address" or fully-qualified domain name (FQDN), can also be found in the dropdown from the **Online** indicator. The API key and ID can also be found and created from the **API keys** section of the **Connect** tab.

> **Handle your API key like a secret:**
> 
> 
> Your API key grants control of the robot to anyone who has it. Do not commit it to version control. The companion repo's `.gitignore` already excludes the starter script's typical edit locations, but the safer pattern is to read the key from an environment variable instead of pasting it directly into the file, for example `API_KEY = os.environ["VIAM_API_KEY"]`.
> 

## Get typed resource handles

After the connection opens, the script builds typed handles for each resource you drive in this phase:

```python
gripper = Gripper.from_robot(machine, "gripper-1")

home = Switch.from_robot(machine, "home-pose")
approach = Switch.from_robot(machine, "approach-pose")
grasp = Switch.from_robot(machine, "grasp-pose")
travel = Switch.from_robot(machine, "travel-pose")
place_pose = Switch.from_robot(machine, "place-pose")
```

`from_robot` returns a typed client for each resource: a Python object whose methods mirror that resource's API. `gripper.grab()` and `gripper.open()` are the same actions as the gripper card's **Grab** and **Open** buttons, and every call travels over the connection to `viam-server`, which routes it to the right resource. You are not driving the hardware directly; you are calling the same API the Control tab calls, from code.

This code drives only the gripper and these pose switches. The script also keeps `motion` and `vision` handles commented out just below them, marked `# Used in Phase 5`; leave them commented until you add the vision service in the next phase.

## Run the script

<!-- ASSET P0 term-resource-names (TERM+): uv run output with resource_names printed; label arm-1/gripper-1/cam-1/pose switches/obstacle grippers -->

Start by confirming the connection without moving anything, then test drive the arm.

### First run: confirm the connection

Run the script with `uv run starter-script.py` (or `python3 starter-script.py` if you're not using `uv`). As shipped, the static sequence is commented out so nothing moves. This first run (TODO 2 in starter-script.py) only opens the connection. The `print(machine.resource_names)` line ships commented out; uncomment it to print every resource on the machine:

```python
print(machine.resource_names)
```

<div class="checkpoint">
  <p class="checkpoint-title"><i class="icon fas fa-check-circle"></i>Checkpoint</p>
  <div class="checkpoint-body"><code>machine.resource_names</code> prints a list that includes at least <code>arm-1</code>, <code>gripper-1</code>, and <code>cam-1</code>, the five poses (<code>home-pose</code>, <code>approach-pose</code>, <code>grasp-pose</code>, <code>travel-pose</code>, <code>place-pose</code>) as switches, and the three obstacles from Phase 3 as grippers. The list also contains the <code>builtin</code> motion service and other <code>erh:vmodutils</code> entries, so expect more names than just these. Nothing moves on this run.</div>
</div>


### Second run: drive the arm

With the connection and resource names confirmed, uncomment the static sequence block in the starter script (the lines under `TODO 4`). This is the same sequence you tested by hand from the **Control** tab at the end of Phase 3, now expressed as code instead of button clicks. On a switch, `set_position(2)` executes the pose it has saved:

```python
await home.set_position(2)
await approach.set_position(2)
await gripper.open()
await grasp.set_position(2)
await gripper.grab()
await asyncio.sleep(0.3)  # finger gripper settle
await travel.set_position(2)
await place_pose.set_position(2)
await gripper.open()
await home.set_position(2)
```

The short sleep after `gripper.grab()` gives the two-finger gripper time to settle its grip on the block before the arm starts moving again; without it, the arm can begin the travel move before the fingers have finished closing.

> **The arm moves on this run:**
> 
> 
> With the sequence uncommented, running the script drives the arm through the full static sequence right after it prints the resource list. Clear the workspace and keep the e-stop within reach before you run it again.
> 

Run the script again. This time it prints the resource list, then drives the arm through the full sequence.

<div class="checkpoint">
  <p class="checkpoint-title"><i class="icon fas fa-check-circle"></i>Checkpoint</p>
  <div class="checkpoint-body">On the second run the arm moves through the full sequence end to end: home, approach, open, grasp, grab, travel, place, open, home. The arm should complete every step without stopping, in the same order you validated manually previously.</div>
</div>


## Debugging guide

Most problems fall into one of a few categories:

- **`ResourceNotFoundError: vision-segment`** (or a similar not-found error for the vision service) means you uncommented the vision handle before configuring the vision service. That service is not added until Phase 5, so leave the `vision = VisionClient.from_robot(...)` line commented (it is marked `# Used in Phase 5` in the starter script) until then, and rerun.
- **Connection failures.** If `connect()` raises an error or hangs, double-check the `MACHINE_ADDRESS`, `API_KEY`, and `API_KEY_ID` values against the **Connect** tab. A stale or mistyped API key produces an authentication error immediately; a wrong address usually times out instead. Also confirm the machine shows the green **Live** indicator in the Viam app. A machine that is not live cannot accept a connection no matter how correct your credentials are.
- **Resource-name mismatches.** If `Gripper.from_robot(machine, "gripper-1")` or a similar call raises a not-found error, the name in your script does not match the name on the **Configure** tab. Names are exact strings, not approximations, so `gripper-1` and `gripper_1` are different resources as far as the SDK is concerned. Open `resource_names` from the connection checkpoint above and compare it character for character against the names your script uses.
- **A switch does nothing on `set_position(2)`.** This means the pose was never saved. Go back to the **Control** tab, jog the arm to the correct pose, and set that switch to **update config** (position 1) to save it, as you did in Phase 3, then rerun the script.

With `resource_names` printing everything you expect and the static sequence running end to end from your own code, you have working proof that your connection, your named resources, and your saved poses all hold up under real code. You are ready to integrate perception in [Phase 5](/tutorials/pick-and-place/perception-guided-picking/).

<nav class="workshop-nav" aria-label="Workshop phase navigation"><p class="workshop-progress">Phase 4 of 6</p><div class="workshop-nav-links"><a class="workshop-nav-prev" href="/tutorials/pick-and-place/static-positions/">&larr; Previous</a><a class="workshop-nav-next" href="/tutorials/pick-and-place/perception-guided-picking/">Next &rarr;</a></div>
</nav>


