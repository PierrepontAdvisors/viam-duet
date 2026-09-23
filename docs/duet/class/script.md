# A robot that draws back — the script

Written to be read aloud, word for word. The checklist, the ten-minute version and the likely questions are in `talk.md`.

Timing. The full script is about 1,600 words: roughly fourteen minutes read steadily, sixteen if you take your time,
and the clips, the flipbook and the reveals add two or three more. If the slot is twenty minutes and you want room to
breathe, either drop the paragraphs marked *(skip if you're running long)* or open the deck with `?cut=10`, which leaves
ten slides and about twelve minutes.

`[click]` means press the right arrow. *Italics* say what is on the screen or what to do, and are not read out.

---

## 1 · Duet (1:00)

*The title beside the photo of the arm, the board and the laptop.*

Hi everyone. I'm Nicholas Swerdlowe, and I'm a friend of your teacher.

I work as a product manager, which means I figure out what a piece of software should do, and then work with engineers and designers until it does it. For twelve years I've done that for fashion companies, the ones behind brands like Louis Vuitton and Uniqlo. I build the systems that make the pictures you see when you shop online. For a long time that meant 3D, and lately it means AI.

One thing to say up front, because it matters for the end of this talk. I have never been a professional programmer. I've worked alongside them for twelve years, and I only started writing real code myself recently.

Last weekend I spent two days at a robot hackathon here in New York, and I built a robot arm that draws with you. You make a mark on a whiteboard, and the robot looks at it, thinks about it, and draws something back.

Today I'll show you what it is, how it works, and everything that went wrong on the way. If you have a question, put it in the chat, because we're watching it.

## 2 · What a hackathon is (1:15)

*The sign on the door. The room on demo day. Three facts.*

Let me start with that word, because it sounds more dramatic than it is. A hackathon has nothing to do with breaking into anything. It's a room with a problem in it, a clock on the wall, and people who would rather build something than talk about it.

This one was run by Viam, a company that makes software for robots, and they lent every team a real industrial arm. You show up Friday at nine, they hand out the arms, and at nine that night they lock the doors and send everybody home. Saturday at three-thirty you stand up and show what you made.

*(skip if you're running long)*

The theme was fine motor skills, which means making an arm do delicate things. You could take one of their challenges or bring your own problem, and I brought mine.

## 3 · What other teams built (1:15) — not in the ten-minute version

*Four short clips, playing. No words on the card.*

Some of what the other teams built, same two days, same arm.

One team taught theirs to play Jenga, pulling a block out without bringing the tower down.

One built an arm that throws a ball.

Another one caught a ball in a basket.

And one team bolted a sabre to the arm and taught it to fence.

*(skip if you're running long)*

Every one of them started with somebody saying "what if it could," and then finding out.

## 4 · Why I built this (1:30)

*Black card. Four cartoon panels appear one at a time, a line under each.*

So why a robot that draws with you?

[click] My father was an architect, and he always had a pen on him.

[click] When I was a kid he would take me to the diner, and while we waited for the food we'd draw together on the paper placemat.

[click] He'd draw something, I'd draw on top of it, he'd add to that, and we'd keep going until the food arrived. That's actually how I learned to draw.

[click] Here's the part I didn't expect. I walked in thinking it would be fun to sketch with a robot. Halfway through building it, I understood what I was really making: the other side of that table.

## 5 · What Duet is (1:15)

*The photo of the setup. Four numbered dots appear on it, one at a time, with a label for each.*

The whole thing fits on a desk, and there are only four pieces to it. That's the arm.

[click] On its wrist there's a camera, so it can see the board.

[click] Underneath that, a gripper, holding a green marker.

[click] On the table, a whiteboard, where everything red was drawn by a person and everything green by the robot.

[click] And off to the side, my laptop, running the code that ties it together. That's the entire machine.

## 6 · One turn (1:30)

*Three pictures appear left to right: LOOK, THINK, DRAW.*

Here's what one turn looks like.

[click] First it looks. You draw something, you press Go, and the camera takes a photo of the whiteboard.

[click] Then it thinks. The photo goes to Claude, which is an AI that can look at a photo and tell you what's in it. I ask it the same two questions every turn: what do you see, and what would you add?

*(Point at the yellow box.)*

Here's a real answer from Saturday:

"A crowded world of creatures, flowers and dancing figures."

And then:

"A small green dancing figure in the open lower-right space to balance the crowd."

That took about eight seconds.

[click] Then it draws. Claude also sends back the shape it wants to add, as a list of points. The arm follows them, the little green figure appears, and it's your turn again.

## 7 · It's just points (1:30)

*Two code panels: turtle on the left, the robot on the right.*

This next part is the one I really want you to take home, because you're working in Python right now.

On the left is Tracy, and you've written something like this already. Pen up, go to the starting point, pen down, walk through a list of points, pen up again.

On the right is my robot, simplified a little. Pen up, move to the starting point, pen down, walk through a list of points, pen up again. It's the same program. Tracy draws on a screen; mine has a motor and a marker. That's the only difference that matters.

And see that line with the hash in front of it? That's a comment. The computer skips it. It's there for a person, and notice it doesn't repeat what the code says; it says why the code is like that.

*(skip if you're running long)*

The genuinely hard part I didn't write. When I say move_to, something has to bend six joints so the pen lands on that spot without hitting the table. Viam's software does that, and I just hand it the points.

Nobody in that room was doing exercises out of a textbook. They were using what you're learning to build things that didn't exist on Thursday.

## 8 · Watch it (1:15)

*Left: the board, turn by turn, in a loop. Right: video of the arm drawing.*

On the left is a full session from the hackathon. Ten turns, red drawn by a person, green drawn by the robot. On the right is the arm itself, actually doing it.

*(Let both run once. About fifteen seconds. Say nothing.)*

Every green line on that board is the robot answering a red one.

There's a version online at viam-duet.vercel.app that replays this session with what Claude said each turn.

## 9 · The robot crushed the pen (1:15) — not in the ten-minute version

*A cartoon of the arm pushing the marker into the board.*

Now let me tell you what broke, because plenty did.

The very first line it ever drew, it crushed the marker. I had taught it where the board was by holding the marker in my own hand and touching the corners. But the robot holds a marker about twenty-seven millimeters differently, which is more than an inch. So it was aiming an inch below the surface. The board didn't move. The felt tip did.

The fix was to teach it the corners again, with the marker in the robot's grip. The mistake told me exactly what was wrong. Measure with the robot's hand, not with yours.

## 10 · The smart trigger that wasn't (1:15)

*Two cartoons: the confused robot over an empty board, and a kid pressing a big green button.*

On Friday night I went home and wrote something clever. The camera would notice when you stepped back from the board, and the robot would take its turn on its own, with nobody pressing anything.

Saturday morning it fired every few seconds at a completely empty board, taking turns nobody had asked for. I spent an hour trying to make it smarter.

Then I deleted the whole thing and put a button on the screen that says "Go, robot". That version worked all day, and nobody watching ever knew they were missing the magic. Sometimes the simple thing is allowed to win.

## 11 · The error you'll get too (1:00) — not in the ten-minute version

*A cartoon of a kid squinting at an error, and four lines of code beside it.*

Here's one you're going to run into yourselves. The day before the hackathon I was working through a practice course, and I got this: SyntaxError, 'return' outside function.

I stared at it, because the return was right there, underneath the function. Except it was indented four spaces instead of eight, and that's enough for Python to decide the function had already ended. In Python the indentation isn't decoration, it's the structure.

The message had been telling me that the whole time. Error messages are clues, not insults. Read them.

## 12 · The log (0:45) — not in the ten-minute version

*The loop across the top, the notebook on the left, the four fields listed on the right.*

You know this loop: plan, code, test, debug, revise. I went round it all weekend, and the step nobody really teaches you is debug.

So here's what I did every time something broke. I wrote down what I saw, what I tried, what fixed it, and why that worked. Eight entries by Friday night, and that indentation error is one of them.

More than once, writing down exactly what I was seeing turned out to be most of the fix, because it forced me to look at it properly. Debugging isn't about being clever. It's about being organized while you're wrong.

## 13 · What it felt like (1:15)

*The medal photo.*

So what was it like? Most teams were two or three people. I was one, with Claude as my teammate.

During the final demo the connection to the robot kept dropping, and when it drops, the arm freezes. So I'm standing in front of everybody waiting to see whether it comes back. It came back, and it drew.

I didn't win. I got an honorable mention, which is this medal, and it was still the best two days I have spent building anything.

## 14 · One piece of advice (0:45)

*Black card. Two cartoons appear one at a time, a line under each.*

If you take one thing away from today, let it be this.

[click] You already know enough to start. Remember, I'm not a professional programmer either. Tracy is a robot with the motor taken out.

[click] Start with the smallest version that works, and then make it bigger. Mine was a square drawn in the air with the pen up. Then a square on the board. Then a shape that Claude picked. Then a whole drawing. By seven o'clock on Friday night, it drew back for the first time.

Nobody starts with the whole drawing. Questions?
