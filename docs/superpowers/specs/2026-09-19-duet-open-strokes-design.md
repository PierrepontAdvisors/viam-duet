# Duet open strokes: larger shapes, no overlap, dots instead of fills

Date: 2026-09-19, at the table on day 2. Status: spec written from the brainstorm, awaiting Nicholas's review. Branch `feat/duet-design` in the main checkout. Parent spec: `docs/superpowers/specs/2026-09-18-duet-design.md` (sections 7 and 15). Assumption recorded: both kinds of overlap seen at the table are covered, a stroke crossing its own line and separate strokes landing on one another.

## 1. Summary and decisions

The robot's drawings come out tight: shapes are small, dense clusters of short strokes sit a few millimetres apart, spirals and zigzags cross their own lines, and anything Claude means as a filled area arrives as a stack of near-parallel lines that the bold marker merges into a blob. This spec adds one artist-independent pass in the planner that makes every plan larger, open, and single-lined, and adds one new stroke kind, dots, as the only way to fill an area.

Decisions:

- **The rules live in the planner, not in the artists.** They run on the final plan in `planner.finalize`, after any artist styling, so Abstract, Haring, Mondrian, and Van Gogh all obey them. Haring's extra passes beside each stroke are the kind of overlap being removed, so Haring loses them by design.
- **Bigger, fewer shapes.** Shapes smaller than 30 mm across are scaled up to 40 mm before clipping; a turn keeps at most 2 strokes on Short, 3 on Medium, 5 on Long, in Claude's order (the first strokes are placed nearest the person's mark).
- **Open lines.** A stroke is cut where it returns within 5 mm of an earlier part of itself; a stroke that runs alongside an earlier one closer than 6 mm for most of its length is dropped.
- **Dots are the fill.** A `dots` stroke is a polygon that the planner stipples on a 9 mm grid with a little jitter, each dot a 1.5 mm tick the controller draws as any other stroke. Line fills and hatching are refused by the prompt and thinned by the planner.
- **Pen offset trial.** −1.2 mm is tried at the next free moment (config only); the current −1.5 mm stays until then.

Out of scope: hatching as an artist grammar, controller changes, page changes (dots are ordinary polylines to the page; the stroke count and ghost pen already handle them).

## 2. Where the rules run

Today's pipeline per turn, in `session._state_plan`: `planner.validate(strokes, ink, budget)` turns Claude's strokes into clipped polylines clear of ink, the artist's `style` adds its grammar, and `planner.finalize(styled, ink, budget)` clips, clears, drops crumbs, and cuts to the millimetre budget.

New order:

1. `validate`: convert each stroke to polylines (`dots` yields many), **enlarge** small shapes, clip to the drawable area, clear from existing ink, cut to budget.
2. artist `style` (unchanged).
3. `finalize`: clip, **uncross** each polyline, **thin** parallels, clear from existing ink, **cap** the stroke count, drop crumbs, cut to budget.

Enlarging happens before clearance so a grown shape cannot land on ink; uncross and thin happen after styling so they also govern what the artist added.

## 3. The rules

All in a new pure module `duet/open.py` with the constants in `config.py`. Polylines are lists of (x, y) in robot-board millimetres. Dots are exempt from enlarge, uncross, and thin: a polyline shorter than `DOT_EXEMPT_MM` (3 mm) passes through those three untouched.

- **`enlarge(polylines) -> polylines`.** For each polyline whose bounding-box span (the larger of width and height) is under `MIN_SHAPE_MM` (30), scale about its centroid so the span becomes `TARGET_SHAPE_MM` (40). Nothing else moves. Clipping afterwards handles shapes that grow past the board.
- **`uncross(polyline) -> polyline`.** Resample at 2 mm. Walk the points; keep a point if its distance to every earlier point more than `SELF_GAP_MM` (5) of path behind it is at least `SELF_GAP_MM`. The first offending point ends the stroke; the rest is discarded. Exception: if the offending point is within `SELF_GAP_MM` of the stroke's first point and the stroke is at least 20 mm long, the stroke is a closing loop and is kept up to and including that point. Spirals become open arcs; zigzags with teeth closer than 5 mm lose the second tooth; circles survive.
- **`thin(polylines) -> polylines`.** In order, keep a polyline unless, against some earlier kept polyline, more than half of its 2 mm samples lie within `PARALLEL_GAP_MM` (6) of it. Crossings survive (few near samples); parallels, doubled passes, and hatching do not.
- **`cap(polylines, length_setting) -> polylines`.** Keep the first `STROKE_CAP[length]` polylines longer than `DOT_EXEMPT_MM`, where `STROKE_CAP = {"short": 2, "medium": 3, "long": 5}`; dots are not counted (they are bounded by `DOTS_MAX`) and pass through in place. Implementation: `finalize` gains a `length` argument; the session passes `self.settings.length`.
- **`stipple(polygon) -> polylines`.** Points on a square grid of `DOT_SPACING_MM` (9) inside the polygon (shapely `contains`), each offset by a uniform random jitter of up to `DOT_JITTER_MM` (1.5) from a fixed seed per turn so replays are stable, each emitted as a two-point polyline of length `DOT_MM` (1.5) heading right. At most `DOTS_MAX` (60) dots per turn; beyond that the grid spacing is widened until it fits. Existing ink clearance is applied by the ordinary clear step, so dots never land within 8 mm of a mark.

## 4. The `dots` stroke

`claude_turn.Stroke.kind` gains `"dots"`; `points` holds the polygon's vertices (three or more). `planner.stroke_to_polyline` becomes `stroke_to_polylines` and returns `[polyline]` for the existing kinds and `stipple(polygon)` for dots. The prompt's stroke description gains: "To fill an area, give a `dots` stroke with the area's outline as its points; the robot stipples it with sparse dots. Never fill or hatch with lines."

## 5. Prompt changes (all artists)

Appended to the common instructions in `claude_turn.py`, after the coordinate rules:

> Shapes are large: each at least 40 mm across, most of them 60 mm or more. Draw outlines, never fills or hatching with lines; to fill an area use a dots stroke. Lines never cross their own path and never run alongside another line closer than 8 mm. Give at most N shapes.

where N is the stroke cap for the length setting. The prompt asks for 8 mm between lines while the planner enforces 6 mm, on purpose: Claude aims wide and the planner only catches what slips. The Abstract note's "two to four shapes" and "10 mm apart" lines are replaced by these numbers so the two do not disagree.

## 6. Configuration

New in `config.py`: `MIN_SHAPE_MM = 30.0`, `TARGET_SHAPE_MM = 40.0`, `SELF_GAP_MM = 5.0`, `PARALLEL_GAP_MM = 6.0`, `STROKE_CAP = {"short": 2, "medium": 3, "long": 5}`, `DOT_SPACING_MM = 9.0`, `DOT_JITTER_MM = 1.5`, `DOT_MM = 1.5`, `DOTS_MAX = 60`, `DOT_EXEMPT_MM = 3.0`. `PEN_DOWN_OFFSET_MM` stays −1.5 until the −1.2 trial.

## 7. Effects on the existing artists

- **Abstract**: its own 8 mm spacing rule becomes redundant with `thin` and is removed; its prompt note defers to the common numbers.
- **Haring**: the two extra passes are removed by `thin`; ticks (12 mm apart, 10 to 20 mm long) survive `thin` and are exempt from `enlarge` because enlarge runs before styling. Haring becomes a single-line outline with ticks.
- **Mondrian**: grid rectangles are outlines and survive; subdivisions closer than 6 mm are thinned.
- **Van Gogh**: rows of short dashes closer than 6 mm collapse to one row; the prompt already asks for long sweeping lines.
- **Fallbacks** pass through the same `finalize`, so they obey the rules too.

## 8. Testing

`tests/test_open.py`, pure and fast:

- enlarge: a 24 mm circle becomes 40 mm about the same center; a 50 mm shape is untouched; a 1.5 mm dot is untouched.
- uncross: a two-turn spiral ends after its first turn; a 30 mm circle closes; a zigzag with 3 mm teeth keeps one tooth; a straight line is unchanged.
- thin: two parallel 40 mm lines 3 mm apart keep only the first; two crossing lines both survive; Haring's three-pass stroke keeps one pass.
- cap: six strokes on Short keep two; dots from one `dots` stroke count as one.
- stipple: a 40 × 40 mm square yields between 12 and 25 dots, all inside, none closer than 6 mm to another; a 176 × 240 mm polygon is capped at 60 dots by widening the grid; the same seed gives the same dots.
- planner: `validate` on a `dots` stroke returns dots clear of ink; `finalize` receives `length` and caps.
- Existing suites keep passing; `test_planner_haring.py` is updated for the single pass.

Hardware check, at the table: one Medium turn on a blank board, then a photo. Expected: shapes at least 40 mm across, no two lines closer than about 6 mm, no line over its own path, and, if Claude used dots, evenly spaced points.

## 9. Rollout

Behind nothing: the planner change ships and the next `python -m duet.run` uses it. If a turn looks wrong the numbers in `config.py` are the knobs; setting `STROKE_CAP` high and the gaps to 0 reproduces today's behaviour.
