# A robot that draws back — the talk

For Carolina Uribe's class, grades 9 to 12, over Zoom or Meet. About twenty minutes of talk, then a Q&A rotation at the teacher's computer. Read this from a phone or a second window; the shared tab shows only the deck.

## Pre-flight

- [ ] Open `docs/duet/class/index.html` from disk in Chrome. If Carolina says ten minutes, open it as `index.html?cut=10` instead.
- [ ] Press **F** for fullscreen. Right arrow, space or a click on the right two thirds advances; left arrow or a click on the left third goes back; **1**–**9** and **0** jump; **Home**/**End**.
- [ ] Notes are off. (`?notes=1` shows them: rehearsal only, never on a share.)
- [ ] Second tab, already loaded: https://viam-duet.vercel.app (the replay, for the Q&A).
- [ ] Zoom: Share Screen → the Chrome window → tick "Optimize for video clip". Meet: share the window.
- [ ] Before class, step through cards 3 and 8 and confirm the four clips and the flipbook are playing on the shared screen.
- [ ] This file open on the phone.

## The 10-minute version

Cards 1, 2, 4, 5, 6, 7, 8, 10, 13, 14, with these targets: 1 (0:30), 2 (1:15), 4 (1:00), 5 (1:15), 6 (1:15), 7 (1:15), 8 (1:00), 10 (1:00), 13 (0:45), 14 (0:45) = 10:00. Open the deck with `?cut=10` and the cards below marked "(cut in 10)" are simply not there.

## The talk

Words in **bold** are on the card. Everything else is spoken. Times are targets, total 17:15, leaving room for chat questions.

### 1 · Duet (0:30)

**A robot that draws back. Two days at a robot hackathon.**

Hi, I'm Nicholas. I'm a friend of Ms. Uribe. Last weekend I spent two days at a robot hackathon in New York and built this: a robot arm that draws with you. You draw something, it looks at it, and it draws back. I'm going to show you what it is, how it works, and everything that went wrong on the way. Ask anything in the chat whenever you want. I can see it.

### 2 · What a hackathon is (1:30)

**Friday 9 am to Saturday 6 pm. Doors lock at night. / Teams of 2 or 3. A real robot arm each. / Demo at 3:30. Awards at 5.**

First, what's a hackathon? It's not a competition to hack into things. It's a weekend where a bunch of people show up to a room with a problem and try to build something real before the time runs out.

This one was run by Viam, a company that makes software for robots. They lent every team a real robot arm. That's the sign on the door. That's the room on demo day.

You get there Friday at 9 in the morning. They hand out the arms. At 9 at night they lock the doors, so no all-nighters. Saturday morning you come back, and at 3:30 in the afternoon everyone demos what they built. Awards at 5.

The theme was "fine motor skills": making a robot arm do delicate things. The suggested challenges were things like plug in a phone charger, pour water into a cup, stack Jenga blocks, sort recycling, move an egg without breaking it. Or bring your own idea. I brought my own.

### 3 · What other teams built (1:30) (cut in 10)

Four clips, no words on the card.

Here's what some other teams built. Same arm, same two days.

_(your line about clip 1)_
_(your line about clip 2)_
_(your line about clip 3)_
_(your line about clip 4)_

Different ideas, same two days. Every one of these started with somebody saying "what if it could..."

### 4 · Why I built this (1:30)

**My dad was an architect. He always had a pen. / At the diner, while we waited for the food, we'd draw together. / He'd draw. I'd draw on top. He'd draw again. Until the food came. / I didn't figure out that's where this came from until halfway through building it.**
Four cartoon panels, one per line; each advance shows the next panel with its line under it.

Why did I build a robot that draws with you?

_(advance)_ My dad was an architect. He always had a pen.

_(advance)_ When I was a kid he'd take me to the diner, and while we waited for the food, we'd draw together on the placemat.

_(advance)_ He'd draw something. I'd draw on top of it. He'd draw again. Until the food came, and the drawing was done. That's how I got into art.

_(advance)_ Here's the strange part. I walked into the hackathon just thinking it would be fun to sketch with a robot. I didn't figure out where the idea came from until halfway through building it. I'd built the other side of that diner table.

### 5 · What Duet is (1:30)

**You draw. It looks. It thinks. It draws back.** Four callouts.

So this is the setup. That's the arm.

_(advance)_ On its wrist, that little box is a camera.

_(advance)_ Below it, the gripper, holding a green marker.

_(advance)_ On the table, the board. The red lines are a person's. The green lines are the robot's.

_(advance)_ And my laptop, running the code.

That's all of it. A camera, a hand, a marker, a board, a laptop.

### 6 · One turn (1:30)

**LOOK · THINK · DRAW.** Claude's sentence. **8 seconds to look and decide.**

One turn goes like this.

_(advance)_ LOOK. You draw something and press Go. The camera takes a photo of the board.

_(advance)_ THINK. The photo goes to Claude. Claude is an AI that can look at a photo and tell you what's in it. I ask it two questions: what do you see, and what would you add? This is a real answer from the hackathon: "A crowded world of creatures, flowers and dancing figures. A small green dancing figure in the open lower-right space to balance the crowd." That took about eight seconds.

_(advance)_ DRAW. Claude doesn't just say it. It also sends the shape it wants to draw as a list of points. The arm follows the points, and the green figure appears. Then it's your turn again.

### 7 · It's just points (1:30)

**Your turtle and my robot follow the same thing: a list of points.** Two code panels.

Now here's the part I really want you to see, because Ms. Uribe told me you're drawing in Python right now.

On the left is turtle. You've written this. Pen up. Go to the start. Pen down. Then go through a list of points. Pen up.

On the right is my robot. I simplified it a little, but that's the shape of it. Pen up. Move to the start. Pen down. Go through a list of points. Pen up.

It's the same program. Your turtle and my robot follow the same thing: a list of points. Mine has a motor. Everything you've learned about drawing with code is exactly what the robot does. The rest is plumbing.

### 8 · Watch it (1:30)

The flipbook. **Play with it after: viam-duet.vercel.app**

Here's a whole session. Ten turns. Red is the person. Green is the robot. Watch it grow.

_(let it loop once, about fifteen seconds; say nothing)_

Every green line is the robot answering a red one.

There's a version of this you can play with on the web after class, at viam-duet.vercel.app. It replays a real session, with what Claude said at every turn.

### 9 · The robot crushed the pen (1:15) (cut in 10)

A picture of the arm crushing the marker. **The robot crushed the pen.** … **Measure with the robot's hand, not yours.**

OK. What broke. Because plenty did.

The very first line the robot drew, it pushed the marker so hard it flattened the tip. Crushed it.

Why? To tell the robot where the board is, I'd touched the marker to the corners of the board. With the marker in my hand. But the robot holds the marker differently than I do. 27 millimeters differently. That's more than an inch. So it drove the pen an inch into the board.

The fix: teach it the corners again, with the marker in the robot's grip. The mistake told me exactly what was wrong. Measure with the robot's hand, not yours.

### 10 · The smart trigger that wasn't (1:15)

**The smart trigger that wasn't.** Three lines. **Go, robot!** … **The simple thing is allowed to win.**

Second one. I was proud of this one, before it broke.

I wrote clever code so the robot would notice, by itself, using the camera, when you'd finished drawing and stepped back. No button. Magic.

Saturday morning at the table, it fired every few seconds on a completely empty board. The robot kept trying to take its turn when nobody had drawn anything. I spent an hour on it.

Then I deleted the whole thing and added a button that says "Go, robot!" You draw, you press Go. The button worked all day. It was in the demo. Nobody missed the magic. The simple thing is allowed to win.

### 11 · The error you'll get too (1:00) (cut in 10)

**The error you'll get too.** The excerpt. **SyntaxError: 'return' outside function.** … **The error message is the clue, not the insult.**

And one you're going to get too. The day before the hackathon I was doing the practice course, and I got this: SyntaxError, 'return' outside function.

I stared at it. The return was right there under the function. Except it wasn't. It was four spaces in instead of eight. Python thought the function had already ended. In Python, indentation isn't decoration; it's the structure.

The error message was telling me exactly that. The error message is the clue, not the insult. Read it.

### 12 · The log (0:45) (cut in 10)

**I wrote down every problem.** A picture of the log, then **1 Symptom · 2 What I tried · 3 Fix · 4 Why it worked**. **Nine entries in two days.** … **This is what debugging actually is.**

One thing I did that I'd tell anyone to do. I wrote down every problem. What I saw. What I tried. What fixed it. Why it worked. Nine entries in two days.

Half of them I fixed by writing them down, because writing down what you saw makes you actually look at what you saw. That is what debugging actually is. Not being smart. Being organized about being wrong. You could start one tomorrow.

### 13 · What it felt like (1:15)

**One person. Two days. Honorable mention.** The medal.

What it felt like. One person, two days. Most teams were two or three people. I was one, with Claude as my teammate.

I was tired. During the demo the WiFi in the room kept dropping, and the arm freezes when it drops. I stood there with my hands shaking, waiting for it to come back. And it came back, and it drew.

I didn't win. I got an honorable mention. That's this medal. And it was still the best two days I've had building something. I'd do it again tomorrow.

### 14 · One piece of advice (0:45)

**You already know enough to start. / Start with the smallest thing that works, then make it bigger.**

So, the one thing I'd tell you.

_(advance)_ You already know enough to start. You know turtle. That's a robot with the motor taken out.

_(advance)_ Start with the smallest thing that works, then make it bigger. Mine was a square. Then a square the robot drew. Then a shape Claude chose. Then a whole drawing. Nobody starts with the whole drawing.

Questions.

## Likely questions

For the rotation at the teacher's computer. One-line answers; edit them before the talk.

- **Did you write all the code?** I designed it and decided everything. Claude wrote a lot of it with me. I still had to understand every piece to fix it when it broke, and it broke a lot.
- **How much did it cost?** The arm was lent for the weekend. Claude cost a few dollars for two days of turns.
- **Can it draw anything?** It draws what it decides to add to what you drew, in simple shapes. It's a partner, not a printer.
- **Did it ever hit anything?** No. The software knows where the table and the wall are and plans around them, and there's a big red emergency-stop button.
- **Could I build this?** The drawing part, yes, this month, in turtle. The robot part is the same code with a motor.
- **Why a robot and not just a screen?** Because it makes a real mark you keep.
- **What was the hardest part?** Getting the pen to touch the board at exactly the right height.
- **What would you do next?** Let you teach it your own drawing style from a stack of your sketches.
