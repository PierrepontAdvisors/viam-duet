# A robot that draws back — the script

What to say, slide by slide. The checklist, the ten-minute version and the likely questions are in `talk.md`.

Read it slowly, about 115 words a minute: the words take about 12 minutes, and the clips, the flipbook and the reveals add
two or three more, which leaves room in a twenty-minute slot for the chat. Each slide carries its time. `[click]` means
press the right arrow. *Italics* say what is on the screen. The pictures carry the cards; the words on them are few, so
say the rest.

---

## 1 · Duet (1:00)

*The title beside the photo of the arm, the board and the laptop.*

Hi, everyone. I'm Nicholas Swerdlowe. I'm a friend of your teacher.

I'm a product manager. My job is to decide what a piece of software should do, and then work with engineers and designers until it does it. For twelve years I did that for fashion companies, the ones behind Louis Vuitton, Gucci and Uniqlo, building the systems that make the pictures you see when you shop online. First with 3D. Now with AI.

Last weekend I spent two days at a robot hackathon in New York and built a robot arm that draws with you. You make a mark. It looks, it thinks, and it draws back.

Today: what it is, how it works, and what broke. Questions in the chat any time. We're watching it.

## 2 · What a hackathon is (1:15)

*The sign on the door. The room on demo day. Three facts.*

First, the word. A hackathon isn't about breaking into anything. It's a room, a problem, a clock, and people who would rather build than talk about building.

This one was run by Viam, a robotics software company. They lent every team an industrial robot arm. That's the sign on the door. That's the room on demo day.

Friday at nine they hand out the arms. At nine at night they lock the doors and send you home. Saturday at three-thirty you show what you have. Awards at five.

The theme was fine motor skills: delicate things. Plug in a charger. Pour water into a cup. Stack Jenga. Move an egg without breaking it. Or bring your own problem.

I brought mine.

## 3 · What other teams built (1:15) — not in the ten-minute version

*Four short clips, playing. No words on the card.*

Some of what the other teams built. Same arm. Same two days.

_(your line about clip 1)_

_(your line about clip 2)_

_(your line about clip 3)_

_(your line about clip 4)_

Every one of these started with somebody saying: what if it could.

## 4 · Why I built this (1:30)

*Black card. Four cartoon panels appear one at a time, a line under each.*

Why a robot that draws with you?

[click] My father was an architect. He always had a pen.

[click] At the diner, while we waited for the food, we drew on the placemat.

[click] He'd draw. I'd draw on top. He'd draw again. Until the food came. That's how I learned to draw.

[click] I walked into the hackathon thinking it would be fun to sketch with a robot. Halfway through building it, I understood what I was actually building.

The other side of that table.

## 5 · What Duet is (1:15)

*The photo of the setup. Four numbered dots appear on it, one at a time, with a label for each.*

The whole system fits on a desk. That's the arm.

[click] A camera on the wrist.

[click] A gripper, holding a green marker.

[click] A whiteboard. Red is the person. Green is the robot.

[click] A laptop, running the code.

That's the entire machine.

## 6 · One turn (1:30)

*Three pictures appear left to right: LOOK, THINK, DRAW.*

One turn.

[click] Look. You draw, you press Go, and the camera photographs the board.

[click] Think. The photo goes to Claude. Claude is an AI that can look at a photo and tell you what's in it. I ask it two questions. What do you see? What would you add?

Here's a real answer from Saturday. *(Point at the yellow box.)* "A crowded world of creatures, flowers and dancing figures. A small green dancing figure in the open lower-right space to balance the crowd." About eight seconds.

[click] Draw. Claude also returns the shape it wants to add, as a list of points. The arm follows the points, and the green figure appears.

Your turn.

## 7 · It's just points (1:30)

*Two code panels: turtle on the left, the robot on the right.*

This is the part I want you to take home, because you're drawing in Python right now.

Left: turtle. Pen up. Go to the start. Pen down. Walk a list of points. Pen up.

Right: my robot, simplified. Pen up. Move to the start. Pen down. Walk a list of points. Pen up.

Same program. The robot has a motor.

The hard part, I didn't write. When I say move_to, six joints have to find a path to that point without hitting the table. Viam's software solves that. I hand it points.

Nobody in that room was doing exercises. They were using exactly what you're learning to make something that didn't exist on Thursday.

## 8 · Watch it (1:15)

*The board, turn by turn, in a loop.*

A full session. Ten turns. Red is the person. Green is the robot.

*(Let it loop once. About fifteen seconds. Say nothing.)*

Every green line answers a red one.

You can play with it after class, at viam-duet.vercel.app. It replays this session, with what Claude said each turn.

## 9 · The robot crushed the pen (1:15) — not in the ten-minute version

*A cartoon of the arm pushing the marker into the board.*

Now, what broke.

The first line the robot ever drew, it crushed the marker. I had taught it where the board was by touching the corners with the marker in my hand. The robot holds a marker twenty-seven millimeters differently. More than an inch. So it tried to draw an inch below the surface. The board didn't move. The felt did.

The fix: teach it the corners again, with the marker in the robot's grip. The mistake said exactly what was wrong.

Measure with the robot's hand, not yours.

## 10 · The smart trigger that wasn't (1:15)

*Two cartoons: the confused robot over an empty board, and a kid pressing a big green button.*

Friday night, at home, without the robot, I wrote something clever. The camera would notice when you stepped back, and the robot would take its turn on its own. No button.

Saturday morning it fired every few seconds on an empty board. The robot kept taking turns nobody had asked for. I gave it an hour.

Then I deleted it and added a button. Go, robot. You draw, you press Go. The button worked all day. It was in the demo. Nobody missed the magic.

The simple thing is allowed to win.

## 11 · The error you'll get too (1:00) — not in the ten-minute version

*A cartoon of a kid squinting at an error, and four lines of code beside it.*

One you'll meet yourselves. The day before, in the practice course: SyntaxError, 'return' outside function.

The return was right there under the function. Except it was four spaces in, not eight, so Python decided the function had ended. In Python, indentation is the structure, not decoration.

The message told me exactly that. The error message is the clue, not the insult. Read it.

## 12 · The log (0:45) — not in the ten-minute version

*A cartoon of a notebook with four boxes, and the four boxes under it.*

One habit worth stealing. I wrote down every problem. What I saw. What I tried. What fixed it. Why it worked. Eight entries by Friday night; that indentation error is one of them.

More than once, writing down exactly what I saw was most of the fix, because it made me look.

Debugging isn't being clever. It's being organized about being wrong.

## 13 · What it felt like (1:15)

*The medal photo.*

One person, two days. Most teams were two or three. I was one, with Claude as my teammate.

During the demo the connection to the robot kept dropping, and the arm freezes when it drops. I stood there waiting for it to come back. It came back. It drew.

I didn't win. I got an honorable mention, this medal, and it was the best two days I've had building anything.

## 14 · One piece of advice (0:45)

*Black card. Two cartoons appear one at a time, a line under each.*

One piece of advice.

[click] You already know enough to start. Turtle is a robot with the motor taken out.

[click] Start with the smallest thing that works, then make it bigger. Mine was a square in the air. Then a square on the board. Then a shape Claude chose. Then a drawing. By seven on Friday night it drew back for the first time.

Nobody starts with the whole drawing.

Questions.
