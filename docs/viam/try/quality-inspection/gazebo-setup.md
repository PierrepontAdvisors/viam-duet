# Gazebo Simulation Setup

Set up the Gazebo simulation environment for the inspection tutorial.
> Source: https://docs.viam.com/try/quality-inspection/gazebo-setup/


This guide walks you through setting up the Gazebo simulation used in the [Your First Project](/try/quality-inspection/) tutorial.

## Prerequisites

- **Docker Desktop** installed and running
- A free [Viam account](https://app.viam.com)
- ~5GB disk space for the Docker image

## Step 1: Build the Docker Image

The simulation runs in a Docker container with Gazebo Harmonic and viam-server pre-installed.

**Clone the simulation repository:**

```bash
git clone https://github.com/viamrobotics/can-inspection-simulation.git
cd can-inspection-simulation
```

**Build the Docker image:**

```bash
docker build -t gz-harmonic-viam .
```

This takes 5-10 minutes depending on your internet connection.

## Step 2: Create a Machine in Viam

1. Go to [app.viam.com](https://app.viam.com) and log in
2. Click the **Locations** tab
3. Click **+ Add machine**
4. Name it `inspection-station-1`
5. Click **Add machine**

## Step 3: Create a credentials file

1. Click the 1. Click the <span style="display:inline-flex; align-items:center; gap:5px; background-color:#eff6ff; color:#3b82f6; border:1.5px solid #93c5fd; padding:2px 8px; border-radius:6px; font-size:0.85em; font-weight:500;">Awaiting setup</span> button
2. Click **Machine cloud credentials** to copy your machine's credentials
3. In the `can-inspection-simulation` directory, create a file called `station1-viam.json`
4. Paste your machine's credentials into this file and save

## Step 4: Start the Container

> **Note:**
> 
> 
> If you have a local installation of `viam-agent` running on your machine, it uses port 8080 by default. Running the container with `-p 8080:8080` will conflict with it. To avoid this, either stop the local `viam-agent` before starting the container, or change the host port mapping (for example, `-p 8090:8080`) and access the container on the new port instead.
> 




### Mac/Linux

```bash
docker run --name gz-station1 -d \
  -p 8080:8080 -p 8081:8081 -p 8443:8443 \
  -v "$(pwd)/station1-viam.json:/etc/viam.json" \
  gz-harmonic-viam
```

### Windows (PowerShell)

```powershell
docker run --name gz-station1 -d `
  -p 8080:8080 -p 8081:8081 -p 8443:8443 `
  -v "${PWD}\station1-viam.json:/etc/viam.json" `
  gz-harmonic-viam
```



## Step 5: Verify the Setup

**Check container logs:**

```bash
docker logs gz-station1
```

Look for:

- "Can Inspection Station 1 Running!"
- viam-server startup messages

**View the simulation:**

Open your browser to `http://localhost:8081`

You should see a web-based 3D view of the inspection station with:

- A conveyor belt
- Cans moving along the belt
- An overhead camera view






    
    
    
<picture>

  
  
<source srcset="/tutorials/first-project/gazebo-simulation_hu_1bd096c901176987.webp" type="image/webp" width="1623" height="1100">
<img src="/tutorials/first-project/gazebo-simulation.png" width="1623" height="1100" alt="Gazebo web viewer showing the Can Inspection Station with Overview Camera and Inspection Camera views." class="imgzoom shadow" id="" style="" loading="lazy">
  

</picture>




**Verify machine connection:**

1. Go to [app.viam.com](https://app.viam.com)
2. Click on `inspection-station-1`
3. The status indicator should show **Live** (in green)

## Troubleshooting

**Container won't start**


**Check if ports are in use:**




### Mac/Linux

```bash
lsof -i :8080
lsof -i :8081
```

### Windows (PowerShell)

```powershell
netstat -ano | findstr :8080
netstat -ano | findstr :8081
```



If something is using these ports, stop it or use different port mappings.



**Machine shows Offline in Viam**



1. Check container is running: `docker ps`
2. Check logs for errors: `docker logs gz-station1`
3. Verify credentials in your config file match the Viam app
4. Try restarting: `docker restart gz-station1`
   


**Simulation viewer is blank or slow**



- The web viewer requires WebGL support
- Try a different browser (Chrome usually works best)
- Check your system has adequate resources (4GB+ RAM recommended)
  


## Container Management

**Stop the container:**

```bash
docker stop gz-station1
```

**Start a stopped container:**

```bash
docker start gz-station1
```

**Remove the container (to recreate):**

```bash
docker rm gz-station1
```

**View logs:**

```bash
docker logs -f gz-station1
```

## Ready to Continue

Once your machine shows **Live** in the Viam app, you're ready to continue with the tutorial.

**[Continue to Part 1: Vision Pipeline →](/try/quality-inspection/part-1/)**

