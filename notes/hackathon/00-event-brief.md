# Robot Hackathon: Fine Motor Skills — event brief

Sources: Luma event page (luma.com/wuo6ynis) and Viam's crash-course slide deck, read 2026-09-18.

## When and where
- Fri 2026-09-18, 9:00 AM – 9:00 PM hard close (no overnight hacking)
- Sat 2026-09-19, 9:00 AM – 6:00 PM
- Viam, 1900 Broadway, New York, NY 10023
- Bring a laptop. Viam 101 was the recommended prep, and it's done.

## Schedule
| Day 1 (Fri) | | Day 2 (Sat) | |
|---|---|---|---|
| 9:00 | Check-in, breakfast | 9:00 | Doors, breakfast |
| 9:30 | Kickoff + Viam crash course | 9:30 | Hacking resumes |
| 10:30 | Teams and hardware handed out | 12:30 | Lunch |
| 11:00 | Hacking begins | 3:30 | Demos and drinks |
| 1:00 | Lunch | 5:00 | Awards |
| 6:00 | Dinner | 6:00 | End |
| 9:00 | Hacking ends | | |

## Format
- Teams of 2–3. Build an end-to-end application on a real arm.
- Pick a suggested challenge or bring your own.
- Suggested (deck + Luma): recycling sort (perception in clutter), bin picking / packing, charger plugging (sub-cm precision, plug hidden at contact), pouring liquid into a cup (continuous control), block stacking / Jenga (precision with force feedback), egg transfer (force control).
- Past open projects: chess, cocktail mixing, quality inspection, drawing, puzzle insertion, table setting, folding clothes.
- Prizes: gold = UFactory Lite6 + $5k Viam credits; silver = Seeed reBot Arm B601-RS + $2.5k; bronze = SO-101 + $1k.

## Hardware per team
- UFactory xArm6 or xArm 850 with its control box (Luma also mentions Universal Robots arms)
- UFactory two-finger gripper
- Intel RealSense D435 or Orbbec Astra 2 depth camera, mounted on the arm
- A Linux computer running viam-server, wired to the control box
- Extras on request: Stream Decks, webcams, Raspberry Pis, manipulation objects (blocks, cups, pens, paper)
- Every machine comes pre-configured with `arm`, `gripper`, `cam`, plus `table` and `wall` obstacles

## Where the machine lives
app.viam.com → organization **Hackathons** → location **Fine Motor Skills** → your team's machine.

## People and help
- Viam staff on the floor: Michael Lee, Jiwon Shin, Nick Hehr, Brandon Shrewsbury, Nicolas Palpacuer, Grant Mulitz, Joseph Boradach
- Hackathon Discord: invite on the Luma event page
- Docs: https://docs.viam.com (local mirror in `docs/viam/`)
- The deck says the pick-and-place tutorial uses the same hardware setup as the hackathon machines
- Viam's MCP server for AI agents: https://app.viam.com/mcp

## Safety, said three times in the deck
Know where the E-stop is before the arm moves. Obstacles only constrain the motion service. Direct arm calls (`move_to_position`, `move_to_joint_positions`) go straight through the table and wall.
