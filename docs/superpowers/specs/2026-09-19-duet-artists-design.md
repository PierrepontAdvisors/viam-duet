# Duet artists: a per-turn picker on the main screen and four new artists

Date: 2026-09-19, day 2 at the table. Status: approved and implemented on 2026-09-19 (commits 38b35a1, 8d27ea1, 6bf7617; the picker markup rode in 7b8f585). Branch `feat/duet-design` in the main checkout. Parent specs: `docs/superpowers/specs/2026-09-18-duet-design.md` (artists, section 7) and `docs/superpowers/specs/2026-09-19-duet-open-strokes-design.md` (the planner rules every artist obeys).

## 1. Summary and decisions

The artist is chosen today in the Controls panel, in a four-button segment under Session, and two of the four are greyed out. This spec puts the choice on the main screen, beside the Go button, so a visitor can pick a different artist for every turn; makes a mid-turn change safe; and adds four artists, two of which work from the visitor's own ink instead of asking Claude.

Decisions from the brainstorm:

- **Eight artists, in this order:** Abstract, Mimic, Haring, Mondrian, Van Gogh, Architect, Designer, Shader. Mondrian and Van Gogh stay (Nicholas's call); nothing is removed.
- **Per-turn choice is a main-screen dropdown** next to "Go, robot!", reading "as Abstract ▾". The panel keeps a segment too, on its own Artist row, in sync.
- **The artist is snapshotted when the visitor's mark is captured** and that snapshot drives the prompt, the styler, the recording, and the messages for that turn. Changing the setting during the robot's move applies to the next turn.
- **Mimic and Shader are ink artists:** they compute their strokes from the visitor's new strokes and never call Claude, so their turns start within a second. They speak from a small bank of storybook lines.
- **Architect and Designer are prompt artists** like Haring: Claude proposes, a styler shapes the lines (right angles; rounded corners).
- **Shader keeps 4 mm from the visitor's ink instead of 8**, otherwise every shape under 40 mm across would come out hollow. `finalize` already takes a clearance argument; the session passes the styler's own value when it has one.

Out of scope: a designer ground-shadow line (dropped for now), changing the planner's open-strokes rules, page playback of an artist's name inside the bubble text, Mondrian and Van Gogh changes.

## 2. The main-screen picker

### Markup and layout

`#go` and a new picker share one absolutely positioned flex row at Go's current spot (`left 1.6cqw, top 7.2cqw`, z-index 3, gap 1cqw). `.go` loses its own `position/left/top`; `.go.home` (Return to home) keeps them, since it shows alone at "The end".

```html
<div class="cta" id="cta" data-el="call to action row">
  <button class="go hidden" id="go" data-el="go robot button">Go, robot!</button>
  <div class="pick hidden" id="artist-pick" data-el="artist picker">
    <button class="chip black" id="artist-btn" data-el="artist picker — button">as Abstract ▾</button>
    <div class="menu hidden" id="artist-menu" data-el="artist picker — menu"></div>
  </div>
</div>
```

The menu is a column of chips under the button (z-index 4, above the bubble at 2 and the chips at 3), one per id in `state.artists`, in that order. Each row is `<button class="chip white" data-v="mimic"><b>Mimic</b> Copies what you just drew</button>`; the current artist's row has `.on` (yellow). The menu is built once per state message from `state.artists`, so a backend with a different roster still lists correctly.

### Behaviour, by session state

| state | picker | text |
|---|---|---|
| `human_turn` | shown, opens on click | "as {Name} ▾" (the setting, `state.artist`) |
| `capture`, `interpret` | shown, does not open | "{Name} is looking…" (the turn's artist) |
| `plan`, `robot_draw` | shown, does not open | "{Name} is drawing" (the turn's artist) |
| everything else | hidden | |

The turn's artist reaches the page in the `shot`, `interpretation`, and `plan` messages (section 3); until the first of them arrives for the exchange in progress, the picker shows the setting.

While a turn photo is being browsed (source is a shot, not live), the picker shows "{Name} drew this" for a robot shot whose turn has a recorded artist, and hides otherwise.

Clicking a row sends `set {artist}` and closes the menu; the button text updates when the next state message confirms. Escape, a click outside, or a state change out of `human_turn` closes it. Keyboard: none beyond Escape.

Names and one-line descriptions live in `story.js`:

```js
export const ARTIST_INFO = {
  abstract:  ['Abstract',  'Clean shapes that answer yours'],
  mimic:     ['Mimic',     'Copies what you just drew'],
  haring:    ['Haring',    'Bold outlines and motion ticks'],
  mondrian:  ['Mondrian',  'Straight lines, grids, boxes'],
  vangogh:   ['Van Gogh',  'Swirls of curved dashes'],
  architect: ['Architect', 'Walls, doors, stairs, rooflines'],
  designer:  ['Designer',  'Rounded housings and parts'],
  shader:    ['Shader',    'Fills your shapes with dots'],
};
export function artistName(id)            // ARTIST_INFO name, else the id with its first letter capitalised
export function pickerText(state, setting, turnArtist, browsing)   // the table above, or null when hidden
```

### The panel

The artist segment leaves the Session row and gets its own row: `<span class="lbl">Artist</span>` and a `.g.s12.seg#artist-seg` with the eight buttons (a new `.s12 { grid-column: span 12 }`). The Session row's freed three columns go to the Pause / Pass pair (`s2` becomes `s5`). Rendering stays as today: `markSeg` marks the setting, disabled when not in `state.artists`.

## 3. The per-turn artist in the session

`Session` gains `self.turn_artist: str`, initialised from the settings in `__init__` and `reset()`. In `_state_capture`, once new ink is found and before the human shot is emitted:

```python
self.turn_artist = self.settings.artist
```

`_state_interpret` and `_state_plan` use `self.turn_artist` wherever they read `self.settings.artist` today. `_state_look` uses it when recording the robot shot. It is written to the turn record (`rec.record_turn(turn, artist=...)`) alongside sees/adds, and added to three messages: `interpretation`, `plan`, and `shot` (both the human and the robot shot of that exchange). The `state` message is unchanged: `artist` there remains the setting.

The page's `TurnBook` notes `artist` from any of the three, and `protocol.js` parses it as an optional string on each. `interpretation.source` gains the value `ink`.

Existing behaviour that stays: `update_settings` accepts an artist change in any state; the panel and picker show the setting; the recording's top-level `artist` is the setting at the time of writing, as today.

## 4. Ink artists: the shared mechanism

A styler module may declare `FROM_INK = True` and provide `respond`. The two existing entry points (`style`, `fallback`) stay for prompt artists; ink artists provide `fallback` too, re-exported from `abstract`.

```python
# duet/styles/ink.py: shared by Mimic and Shader
@dataclass(frozen=True)
class InkTurn:
    strokes: list[Polyline]
    color: str
    sees: str
    adds: str
    thought: str
    quip: str

def join_fragments(polylines, gap_mm=INK_JOIN_MM) -> list[Polyline]
    # merges polylines whose ends lie within gap_mm of each other (shapely linemerge after snapping ends)
def closed_shapes(polylines, min_area_mm2) -> list[Polyline]
    # after joining: a polyline whose ends lie within gap_mm and whose closed polygon is valid with area >= min
def light_vector(direction_deg) -> tuple[float, float]
    # unit vector the light comes from, in board mm, y down; same angle convention as haring.ticks
```

A `respond` signature, identical for both ink artists:

```python
def respond(new: list[Polyline], energy: float, direction_deg: float, exchange: int,
            length_setting: str) -> InkTurn
```

`exchange` doubles as the random seed, so a replay draws the same dots.

In the session:

```python
async def _state_interpret(self) -> str:
    styler = STYLERS[self.turn_artist]
    if getattr(styler, "FROM_INK", False):
        self.result = None
        self.ink_turn = styler.respond(self.human_new, self.settings.energy, self.settings.direction,
                                       self.turn + 1, self.settings.length)
        self.bus.emit("interpretation", sees=..., adds=..., thought=..., quip=..., source="ink",
                      latency_s=0.0, error=None, turn=self.turn + 1, artist=self.turn_artist)
        return "plan"
    ...as today, with artist=self.turn_artist in the propose call and the message
```

`_state_plan`, when `self.ink_turn` is set for this turn: `styled, self.color = ink_turn.strokes, ink_turn.color`; sees/adds from it; `source = "ink"`; then the ordinary `planner.finalize(styled, ink, budget, clearance_mm=getattr(styler, "CLEARANCE_MM", cfg.CLEARANCE_MM), length_setting=...)`. The existing "nothing survived, use the fallback" branch applies unchanged. `ink_turn` is cleared when the plan is emitted.

The page's status line shows `claude ink · {artist} works from your ink` for `source == "ink"`.

## 5. Mimic

Copies the strokes the visitor just drew and places the copy beside them.

- **Scale** about the strokes' bounding-box centre by `s = 0.8 + 0.8 * energy` (0.8 at 0, 1.2 at 0.5, 1.6 at 1).
- **Variation by exchange** (`(exchange - 1) % 3`): 0 shift only; 1 mirror left-right about the centre, then shift; 2 rotate a quarter turn about the centre, then shift.
- **Placement.** With `u` the unit vector for `direction_deg` and `S` the original's span (the larger of width and height), the copy's centre is `c + d·u`, `d = S/2 + s·S/2 + CLEARANCE_MM + MIMIC_GAP_MM`. If the copy's bounding box is not inside the drawable inset, try `u` turned 180°, then +90°, then −90°; if none fits, repeat the four with `s = 0.8`; if still none, take the candidate with the most area inside and let clipping trim it.
- **Order.** Strokes are emitted longest first, so when the stroke cap bites (3 on Short) the biggest parts of the copy survive.
- **Words**, cycled by exchange. Thoughts: "Let me try that…", "Watch this…", "One more, my way…". Quips: "Copycat!", "Like this?", "Two of a kind!", "Your move, again.". `sees` "Your new mark, ready to echo."; `adds` "a copy beside it, shifted" / "…mirrored" / "…turned".
- **Fallback:** Abstract's arc.

Constants: `MIMIC_GAP_MM = 4.0`, `MIMIC_SCALE = (0.8, 1.6)`.

## 6. Shader

Fills the visitor's new shapes with dots, denser away from the light.

- **What counts as a shape.** `join_fragments` at 10 mm, then `closed_shapes` with `SHADER_MIN_AREA_MM2 = 300`. Each shape is stippled with `op.stipple(shape, spacing, max_dots=cap, seed=exchange)`.
- **No shape?** The new strokes are lines. The band `LineString(line).buffer(SHADER_BAND_MM, single_sided=True)` is taken on whichever side lies away from the light (the side whose centroid has the smaller dot product with `light_vector`), and that band is stippled instead.
- **Spacing from energy:** `SHADER_SPACING_MM = (12.0, 5.0)`, linear in energy, so the default 0.5 gives 8.5 mm.
- **Gradient from the light dial.** For each dot, `t` is its position along the light vector across the shape's bounding box, −1 on the shadow edge to +1 on the lit edge. It is kept with probability `1 − (1 − SHADER_LIT_KEEP) · (t + 1) / 2`, `SHADER_LIT_KEEP = 0.25`, drawn from `random.Random(exchange)`.
- **Cap by length:** `SHADER_DOTS_MAX = {"short": 30, "medium": 60, "long": 120}` for the turn, split across the shapes in proportion to their areas (each shape's share is its `max_dots`), before the gradient thins it. Each dot is one pen touch of roughly 1.5 to 2 s, so 120 dots fit inside the Long time budget with room to spare.
- **Clearance:** `CLEARANCE_MM = 4.0` on the module; the session passes it to `finalize`. Dots within 4 mm of any ink, the visitor's or earlier robot strokes, are removed as usual.
- **Words**, cycled. Thoughts: "Where does the light fall?", "A little shadow…". Quips: "Let me shade that in.", "Darker here, lighter there.", "Dots, dots, dots!". `sees` "A shape with an inside." or "A line with a shadow side."; `adds` "dots inside it, thicker away from the light" or "a band of dots along its shadow side".
- **Fallback:** Abstract's arc.

## 7. Architect (prompt artist)

Prompt note, in `ARTIST_NOTES["architect"]`:

> The artist mode is Architect: you draft in plan and elevation. Read the person's mark as a site or a building element and build around it: walls, a doorway with its quarter-circle swing, a stair run, a colonnade of posts, a roofline, a ground line. Straight lines and right angles; arcs only as door swings and arches. Your straight lines will be squared up for you, so give simple runs of horizontal and vertical segments.

Per-length asks for Architect (`ASKS["architect"]`): Short "one element: a wall, a doorway, or a post"; Medium "one room or one elevation that extends the drawing"; Long "a full plan or elevation: walls, doors, a stair, a colonnade, a roofline, spread across the free space".

Styler `duet/styles/architect.py`: `style` simplifies each polyline (`LineString.simplify(2.0)`) and, if every segment lies within `ARCH_SNAP_DEG = 15` of horizontal or vertical, squares it: walking the vertices, each segment keeps its start and moves its end onto the axis it is nearest to. A polyline with any segment further from the axes than that (arcs, diagonals) passes untouched. `energy` and `direction_deg` are accepted and ignored, as in Abstract. `fallback` is Abstract's.

## 8. Designer (prompt artist)

Prompt note, in `ARTIST_NOTES["designer"]`:

> The artist mode is Product Designer: you sketch objects. Read the person's mark as a component, a button, a handle, a lens, a screen, and sketch the product it belongs to around it: a housing with rounded corners, a second view or an exploded part set beside it, small circles for controls. Sharp corners will be rounded for you, so give clean boxes and simple outlines.

Per-length asks (`ASKS["designer"]`): Short "one component: a button, a port, or a handle"; Medium "the housing around the part, one clean outline"; Long "the whole product: housing, controls, a second view or an exploded part beside it".

Styler `duet/styles/designer.py`: `style` fillets every vertex whose turn angle exceeds `FILLET_MIN_DEG = 25` with a circular arc of radius `min(DESIGNER_FILLET_MM = 8, 0.45 × each adjacent segment)`, sampled at six points; straight runs and gentle curves pass untouched. `energy` and `direction_deg` are accepted and ignored. `fallback` is Abstract's.

`claude_turn.propose` picks `ASKS.get(artist, ASKS["haring"])[length_setting]` in place of today's inline abstract-or-haring choice; the Abstract asks move into the same table.

## 9. Configuration

Added to `config.py`, after the open-strokes block:

```python
INK_JOIN_MM = 10.0                                  # fragments whose ends lie this close are one stroke
MIMIC_GAP_MM = 4.0                                  # beyond the clearance, between original and copy
MIMIC_SCALE = (0.8, 1.6)                            # copy scale at energy 0 and 1
SHADER_MIN_AREA_MM2 = 300.0                         # smaller closed shapes are not shaded
SHADER_BAND_MM = 12.0                               # the shadow band beside a line with no interior
SHADER_SPACING_MM = (12.0, 5.0)                     # dot spacing at energy 0 and 1
SHADER_LIT_KEEP = 0.25                              # keep probability on the lit edge (1.0 on the shadow edge)
SHADER_DOTS_MAX = {"short": 30, "medium": 60, "long": 120}
SHADER_CLEARANCE_MM = 4.0
ARCH_SNAP_DEG = 15.0
DESIGNER_FILLET_MM = 8.0
FILLET_MIN_DEG = 25.0
```

`session.ARTISTS` becomes the eight ids in display order; `STYLERS` maps all eight; `run.py --artist` offers all eight.

## 10. Testing

Backend, pure and fast:

- `tests/test_mimic.py`: the copy sits at least 8 mm from the original and inside the inset; energy 1 gives a 1.6× span; exchange 2 mirrors (x order reverses), exchange 3 rotates (width and height swap); a mark by the right edge puts the copy to its left; strokes come longest first; words cycle with exchange.
- `tests/test_shader.py`: a closed 60 mm circle yields dots all inside, none within 4 mm of the outline, more on the shadow half than the lit half; a bare line yields dots only on its shadow side within the band; two fragments of one square are joined and shaded; Short caps at 30 dots before thinning; the same exchange gives the same dots.
- `tests/test_architect.py`: a polyline with segments within 15° of the axes comes out exactly orthogonal; a 45° line and a 60 mm arc are unchanged.
- `tests/test_designer.py`: a square's four corners become arcs (no turn angle over 25° remains); a straight line is unchanged; a 10 mm segment limits its fillet to 4.5 mm.
- `tests/test_session.py`: changing the artist while the session is in `interpret` leaves `plan` using the snapshot and the next `state` showing the new setting; a Mimic exchange never calls the brain, emits `interpretation` with `source == "ink"` and `artist == "mimic"`, and its `plan` and robot `shot` carry `artist`; the turn record has `artist`.
- `tests/test_claude_turn.py`: every id in `ARTISTS` has a note and an asks entry.
- `tests/test_web.py`: `set artist` accepts each of the eight.
- `tests/test_run.py`: `--artist` accepts each of the eight.

Page, `node --test 'pagetests/*.test.mjs'`:

- `protocol.test.mjs`: `interpretation`, `plan`, and `shot` parse an optional `artist`; `source: "ink"` is accepted.
- `story.test.mjs`: `artistName` for all eight and for an unknown id; `pickerText` per the table in section 2, including the browsing case.
- `smoke.test.mjs` / replay harness: the picker is visible in `human_turn`, opens to eight rows with the current one marked, is disabled with the "is drawing" text during `robot_draw`, and hidden at `finished`.

Hardware check, at the table: one Medium exchange each on Mimic (a copy beside the mark), Shader (dots inside a drawn circle, denser on the far side from the sun icon), Architect (a squared-up element), Designer (rounded corners). Pick each from the main screen during the human turn.

## 11. Rollout

Behind nothing. Bump the page's asset version (`?v=ds6`) so open pages fetch the new modules. The default artist stays Abstract. Every new artist passes through the same `finalize`, so the open-strokes guarantees hold for them.
