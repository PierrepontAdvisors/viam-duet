# Motion planning reference

Configuration, API, and technical reference for the motion service.
> Source: https://docs.viam.com/motion-planning/reference/


The motion service turns a high-level "move to this pose" request into a
collision-free joint trajectory. This reference documents what you
configure, what the API exposes, and the formats and algorithms behind
those requests. For conceptual background, see
[How motion planning works](/motion-planning/how-planning-works/); for
task-based guidance, start from the [section landing](/motion-planning/).

**Configuration and API**: where most readers start.

<div class="card-container">
  <div class="row-no-margin">
<div class="col hover-card "><a href="/motion-planning/reference/motion-service/"><div ><div>Motion service</div><p>Configure the motion service for planning and executing component movements.</p></div>
    </a></div>

<div class="col hover-card "><a href="/motion-planning/reference/api/"><div ><div>API</div><p>The motion service API for planning and executing component movements.</p></div>
    </a></div>

<div class="col hover-card "><a href="/motion-planning/reference/cli-commands/"><div ><div>CLI commands</div><p>Reference for the Viam CLI commands that inspect the frame system and test motion from the command line.</p></div>
    </a></div>

</div>
</div>

**Formats and machinery**: the underlying schemas the service operates on.

<div class="card-container">
  <div class="row-no-margin">
<div class="col hover-card "><a href="/motion-planning/reference/frame-system-api/"><div ><div>Frame system API</div><p>Query and transform frame system poses with the robot service RPCs: FrameSystemConfig, GetPose, TransformPose, and TransformPCD.</p></div>
    </a></div>

<div class="col hover-card "><a href="/motion-planning/reference/kinematics/"><div ><div>Kinematics</div><p>Set up the kinematic model that describes how your arm&#39;s joints and links create motion.</p></div>
    </a></div>

<div class="col hover-card "><a href="/motion-planning/reference/orientation-vectors/"><div ><div>Orientation vectors</div><p>Reference for specifying component orientation using orientation vectors and other rotation formats.</p></div>
    </a></div>

<div class="col hover-card "><a href="/motion-planning/reference/algorithms/"><div ><div>Motion planning algorithms</div><p>The two-stage planning strategy the built-in motion service uses and the tuning surfaces exposed to callers.</p></div>
    </a></div>

<div class="col hover-card "><a href="/visualization/reference/world-state/"><div ><div>WorldState</div><p>What a WorldState is: the per-request set of obstacles and frame transforms you pass to a single Move call for the planner to plan around.</p></div>
    </a></div>

</div>
</div>

