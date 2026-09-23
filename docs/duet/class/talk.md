# A robot that draws back — the run-of-show

For Carolina's class, grades 9 to 12, over Zoom or Meet. About twenty minutes of talk, then a Q&A rotation at the teacher's computer. The words are in `script.md`; this file is everything around them. The shared tab shows only the deck.

## Pre-flight

- [ ] Open `docs/duet/class/index.html` from disk in Chrome. If Carolina says ten minutes, open it as `index.html?cut=10` instead.
- [ ] Press **F** for fullscreen. Right arrow, space or a click on the right two thirds advances; left arrow or a click on the left third goes back; **1**–**9** and **0** jump; **Home**/**End**.
- [ ] Second tab, already loaded: https://viam-duet.vercel.app (the replay, for the Q&A).
- [ ] Zoom: Share Screen → the whole screen, not the Chrome window (a fullscreen window can hand Zoom a black frame). Leave "Optimize for video clip" unticked: it softens the code cards, and the only video is fifteen seconds of muted clips. Meet: share the screen.
- [ ] Chat: fullscreen Chrome hides it. Either a second screen with the Zoom window, or Carolina reads chat questions aloud. Say which at the start.
- [ ] Card 3: the four clip lines are written in `script.md`, and the four captions in `index.html`.
- [ ] Card 13: `hackathon-videos/photo-medal.jpg` dropped in, `build_assets.py` rerun, the medal shows on the card.
- [ ] Likely questions edited (bottom of this file). The AI cost figure read off the Anthropic console.
- [ ] Do Not Disturb on; Slack, Mail and Messages closed.
- [ ] Before class, step through cards 3 and 8 and confirm the four clips and the flipbook are playing on the shared screen.
- [ ] `script.md` open on the phone.

## The 10-minute version

Cards 1, 2, 4, 5, 6, 7, 8, 10, 13, 14, with these targets: 1 (1:00), 2 (1:00), 4 (1:15), 5 (1:00), 6 (1:15), 7 (1:15), 8 (1:00), 10 (1:00), 13 (0:45), 14 (0:30) = 10:00. Open the deck with `?cut=10` and the cards below marked "(cut in 10)" are simply not there. The cut renumbers: the kickers read 01 to 10 and the number keys jump by that numbering (in the cut, `8` is the trigger card and `0` is the advice).

## The words

What to say on each slide is `script.md`, one section per slide with a time at a slow pace and `[click]` cues. Read that from the phone; this file is the run-of-show.

## Carolina's question: why communication matters when people build together

She asked for this one, so it's written out to be read aloud like the script. About two and a half minutes.

Most of the work in software isn't typing. It's making sure the next person understands what you did, and that person is usually you, three weeks later, with no memory of why you wrote any of it.

So you write for them. A name is the shortest explanation you can give. On this project I called one piece of the page "strip," and that word was already being used for something else in the same file. Two things, one name, and the layout broke in a way that took me a while to see. Renaming it fixed it. That wasn't a coding problem. It was a naming problem.

Then there are comments, which you're writing right now. Here's the rule I'd give you: the code already says what it does, so a comment should say why it's like that. "Add 5 to the height" is a useless comment. "Add 5 so the pen clears the marker tray" is the one that saves somebody an hour.

You also say what something should do before you build it. I wrote a plan for these slides before I made a single one, so when I disagreed with myself later, the plan was there to argue with. And my tests are really just sentences: this card shows four pictures, this button says Go. If somebody breaks one of those sentences, the computer says so immediately.

Debugging together is mostly describing. Half the bugs I fixed that weekend, I fixed by writing down exactly what I saw before I tried anything. When you ask someone for help, the help you get is only as good as your description.

One last thing. I build with AI every day now, and an AI is a collaborator you have to be precise with. If I can't say clearly what I want, I don't get it. So explaining your code to the person sitting beside you is the same skill. Being understood is the job.

## Likely questions

The first six are the ones students actually asked on 2026-09-22, in the order the teacher recorded them. Answer in your own words; these are the facts to hit.

- **How do you manage your time and stay organized?** I split the two days into two-hour sprints, and I deliberately spent the first one not building. I wrote down what the arm could do, what I actually wanted to make, and what would be finished by Saturday. The thinking time is the part people skip.
- **What is different about working alone versus with a team?** Alone you're never blocked waiting for anybody, and you can change your mind in a second. But nobody catches your bad idea, and nobody knows what you meant at two in the morning. That's why I wrote everything down: I was my own teammate.
- **How long have you been coding?** I've worked in software for twelve years, but as a product manager, not a programmer. I've only been writing real code myself recently, and I still look things up constantly.
- **How did Claude and the robot communicate?** They never talked to each other. My Python program is the go-between. It sends the photo to Claude over the internet and gets back two sentences and a list of points, then it sends those points to the arm, also over the internet, using Viam's library.
- **Did you use an AI agent, APIs, or something else?** Both, in different places. During the demo, each turn is one plain API call: the photo goes out, the answer comes back, nothing autonomous. While I was building it, I used Claude as an agent that could read my files and write code with me, which is how one person got it done in two days.
- **How do comments and communication help when several people work on the same project?** See the written answer above. The short version: the code says what, a comment says why, and everything else — names, plans, tests — exists so the next person doesn't have to guess.
- **Did you write all the code?** I designed it and decided everything. Claude wrote a lot of it with me. I still had to understand every piece to fix it when it broke, and it broke a lot. That's the job now: knowing what to build, and knowing when it's wrong.
- **How much did it cost?** The arm was lent for the weekend. The AI part cost less than lunch. The Claude I write code with is a monthly subscription.
- **Could I build this?** The drawing part, yes, this month, with Tracy. The robot part is the same code with a motor.
- **Did it ever hit anything?** Never a person or the table. It did crush the pen on the board once; that's the story on card 9. The software knows where the table and wall are and plans around them, and there's a big red emergency-stop button.
- **Can it draw me?** No. It doesn't copy what it sees; it adds one thing to what you drew, with one green marker, in simple shapes.
- **Is it going to take artists' jobs?** It can't start a drawing. It can only answer one. Every piece needs a person's first mark.
- **What would you do next?** Let you teach it your own drawing style from a stack of your sketches.
