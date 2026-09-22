# A robot that draws back — the script

What to say, slide by slide. Nothing else: the checklist, the ten-minute version and the likely questions are in `talk.md`.

Read it slowly. At a slow pace (about 115 words a minute) the words take about 13 minutes; the clips, the flipbook and the
reveals add two or three more. That leaves room in a twenty-minute slot for questions from the chat. Each slide has its
time at a slow pace. `[click]` means press the right arrow. *Italics* say what is on the screen.

---

## 1 · Duet (0:30)

*The title over the photo of the arm, the board and the laptop.*

Hi, I'm Nicholas. I'm a friend of your teacher.

Last weekend I spent two days at a robot hackathon in New York, and I built this. A robot arm that draws with you. You draw something. It looks at it. And it draws back.

I'm going to show you what it is, how it works, and everything that went wrong on the way. If you have a question, put it in the chat any time. We're watching it.

## 2 · What a hackathon is (1:30)

*The sign on the door. The room on demo day. Three facts.*

First, what's a hackathon? It's not about breaking into computers. It's a weekend where a bunch of people show up to a room with a problem, and try to build something real before the time runs out.

This one was run by Viam, a company that makes software for robots. They lent every team a real robot arm. That's the sign on the door. That's the room on demo day.

You get there Friday at nine in the morning. They hand out the arms. At nine at night they lock the doors and send you home. I kept coding at home. Saturday morning you come back. At three-thirty everyone shows what they built. Awards at five.

The theme was "fine motor skills." Making a robot arm do delicate things. The suggested challenges were things like: plug in a phone charger. Pour water into a cup. Stack Jenga blocks. Move an egg without breaking it. Or bring your own idea.

I brought my own.

## 3 · What other teams built (1:30) — not in the ten-minute version

*Four short clips, playing. No words on the card.*

Here's what some other teams built. Same arm. Same two days.

_(your line about clip 1)_

_(your line about clip 2)_

_(your line about clip 3)_

_(your line about clip 4)_

Different ideas, same two days. Every one of these started with somebody saying: what if it could...

## 4 · Why I built this (1:30)

*Black card. Four cartoon panels appear one at a time, each with its line under it.*

So why did I build a robot that draws with you?

[click] My dad was an architect. He always had a pen.

[click] When I was a kid he'd take me to the diner. While we waited for the food, we'd draw together on the placemat.

[click] He'd draw something. I'd draw on top of it. He'd draw again. Until the food came, and the drawing was done. That's how I got into art.

[click] Here's the strange part. I walked into the hackathon just thinking it would be fun to sketch with a robot. I didn't figure out where the idea came from until I was halfway through building it.

I'd built the other side of that diner table.

## 5 · What Duet is (1:30)

*The photo of the setup. Four numbered dots appear on it, one at a time, with a line for each.*

This is the setup. That's the arm.

[click] On its wrist, that little box is a camera.

[click] Below it, the gripper. It's holding a green marker.

[click] On the table, the board. The red lines are a person's. The green lines are the robot's.

[click] And my laptop, running the code.

That's all of it. A camera, a hand, a marker, a board, a laptop.

## 6 · One turn (1:30)

*Three pictures appear left to right: LOOK, THINK, DRAW.*

One turn goes like this.

[click] Look. You draw something and press Go. The camera takes a photo of the board.

[click] Think. The photo goes to Claude. Claude is an AI that can look at a photo and tell you what's in it. I ask it two questions. What do you see? And what would you add?

This is a real answer from the hackathon. *(Point at the yellow box.)* "A crowded world of creatures, flowers and dancing figures. A small green dancing figure in the open lower-right space to balance the crowd." That took about eight seconds.

[click] Draw. Claude doesn't just say it. It also sends the shape it wants to draw, as a list of points. The arm follows the points, and the green figure appears.

Then it's your turn again.

## 7 · It's just points (1:30)

*Two code panels: turtle on the left, the robot on the right.*

Now here's the part I really want you to see, because your teacher told me you're drawing in Python right now.

On the left is turtle. You've written something like this. Pen up. Go to the start. Pen down. Go through a list of points. Pen up.

On the right is my robot. I simplified it a little, but that's the shape of it. Pen up. Move to the start. Pen down. Go through a list of points. Pen up.

It's the same program. Your turtle and my robot follow the same thing: a list of points. Mine has a motor.

The hard part, I didn't write. When I say move_to, the robot has to work out how to bend six joints to put the pen there without hitting the table. Viam's software does that. I just give it the points.

Nobody in that room was doing exercises. They were using the same stuff you're learning right now to make something that didn't exist on Thursday.

## 8 · Watch it (1:30)

*The board, turn by turn, in a loop.*

Here's a whole session. Ten turns. Red is the person. Green is the robot. Watch it grow.

*(Let it loop once. About fifteen seconds. Say nothing.)*

Every green line is the robot answering a red one.

There's a version of this you can play with after class, at viam-duet.vercel.app. It replays the session you just watched, with what Claude said at every turn.

## 9 · The robot crushed the pen (1:15) — not in the ten-minute version

*A cartoon of the arm pushing the marker into the board.*

Okay. What broke. Because plenty did.

The very first line the robot drew, it pushed the marker so hard it flattened the tip. Crushed it.

Why? To tell the robot where the board is, I'd touched the marker to the corners of the board. With the marker in my hand. But the robot holds the marker differently than I do. Twenty-seven millimeters differently. That's more than an inch. So it tried to push the pen an inch below the board. The board didn't move. The pen tip did.

The fix: teach it the corners again, with the marker in the robot's grip. The mistake told me exactly what was wrong.

Measure with the robot's hand, not yours.

## 10 · The smart trigger that wasn't (1:15)

*Two cartoons: the confused robot over an empty board, and a kid pressing a big green button.*

Second one. I was proud of this one, before it broke.

Friday night, at home, without the robot, I wrote clever code so it would notice by itself, using the camera, when you'd finished drawing and stepped back. No button. Magic.

Saturday morning at the table, it fired every few seconds on a completely empty board. The robot kept trying to take its turn when nobody had drawn anything. I spent an hour on it.

Then I deleted the whole thing and added a button that says "Go, robot!" You draw, you press Go. The button worked all day. It was in the demo. Nobody missed the magic.

The simple thing is allowed to win.

## 11 · The error you'll get too (1:00) — not in the ten-minute version

*A cartoon of a kid squinting at an error, and the four lines of code beside it.*

And here's one you're going to get too. The day before the hackathon, I was doing the practice course, and I got this: SyntaxError. 'return' outside function.

I stared at it. The return was right there under the function. Except it wasn't. Look at the code. It was four spaces in instead of eight. Python thought the function had already ended. In Python, indentation isn't decoration. It's the structure.

The error message was telling me exactly that.

The error message is the clue, not the insult. Read it.

## 12 · The log (0:45) — not in the ten-minute version

*A cartoon of a notebook with four boxes, and the four boxes under it.*

One thing I did that I'd tell anyone to do. I wrote down every problem. What I saw. What I tried. What fixed it. Why it worked. Eight entries by Friday night, and that error from the practice day is one of them.

More than once, writing down exactly what I saw was most of the fix. Because it makes you actually look.

That is what debugging actually is. Not being smart. Being organized about being wrong. You could start one tomorrow.

## 13 · What it felt like (1:15)

*The medal photo.*

What it felt like. One person, two days. Most teams were two or three people. I was one, with Claude as my teammate.

I was tired. During the demo, the connection to the robot kept dropping, and the arm freezes when it drops. I stood there with my hands shaking, waiting for it to come back. And it came back. And it drew.

I didn't win. I got an honorable mention. That's this medal. And it was still the best two days I've had building something. I'd do it again tomorrow.

## 14 · One piece of advice (0:45)

*Black card. Two cartoons appear one at a time, each with its line under it.*

So, the one thing I'd tell you.

[click] You already know enough to start. You know turtle. That's a robot with the motor taken out.

[click] Start with the smallest thing that works, then make it bigger. Mine was a square in the air, pen up. Then the same square on the board. Then a shape Claude chose. Then a whole drawing. By seven o'clock Friday night it drew back for the first time.

Nobody starts with the whole drawing.

Questions.
