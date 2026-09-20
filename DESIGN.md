---
name: AI Bouncer
description: A local-first decision instrument that descends through evidence before reaching a safe verdict.
colors:
  ocean-black: "#02070c"
  abyss: "#050e18"
  midnight: "#081b26"
  thermocline: "#3de0f3"
  marine-snow: "#f4f6f4"
  muted-sonar: "#91afbd"
  kev-signal: "#43e8ef"
  semif-signal: "#b2a0ff"
  pass: "#52e3aa"
  warn: "#ffd13b"
  danger: "#ff6064"
  danger-depth: "#461319"
typography:
  display:
    fontFamily: "Oxanium, sans-serif"
    fontSize: "clamp(29px, 6vw, 54px)"
    fontWeight: 700
    lineHeight: 0.95
    letterSpacing: "-0.045em"
  verdict:
    fontFamily: "Source Code Pro, ui-monospace, monospace"
    fontSize: "9.5cqw"
    fontWeight: 700
    lineHeight: 0.85
    letterSpacing: "0.02em"
  readout:
    fontFamily: "Source Code Pro, ui-monospace, monospace"
    fontSize: "3.5cqw"
    fontWeight: 700
    lineHeight: 1
  body:
    fontFamily: "system-ui, sans-serif"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.7
  label:
    fontFamily: "Source Code Pro, ui-monospace, monospace"
    fontSize: "9px"
    fontWeight: 600
    lineHeight: 1.2
    letterSpacing: "0.14em"
rounded:
  sharp: "0"
  readout: "1.1cqw"
  evidence: "1.2cqw"
  thermocline: "1.5cqw"
  pill: "999px"
  circle: "50%"
spacing:
  xs: "6px"
  sm: "8px"
  md: "12px"
  lg: "18px"
  xl: "24px"
  section: "30px"
components:
  button-primary:
    backgroundColor: "{colors.thermocline}"
    textColor: "{colors.abyss}"
    typography: "{typography.label}"
    rounded: "{rounded.sharp}"
    padding: "0 20px"
    height: "60px"
  button-evidence:
    backgroundColor: "{colors.danger-depth}"
    textColor: "{colors.marine-snow}"
    typography: "{typography.label}"
    rounded: "{rounded.evidence}"
    padding: "0 6.5cqw 0 8.3cqw"
    height: "5.5cqw"
  field:
    backgroundColor: "{colors.abyss}"
    textColor: "{colors.marine-snow}"
    typography: "{typography.body}"
    rounded: "{rounded.sharp}"
    padding: "12px"
  replay-badge:
    backgroundColor: "{colors.midnight}"
    textColor: "{colors.thermocline}"
    typography: "{typography.label}"
    rounded: "{rounded.pill}"
    height: "5.6cqw"
  gate:
    backgroundColor: "{colors.abyss}"
    textColor: "{colors.marine-snow}"
    rounded: "{rounded.readout}"
    padding: "1.5cqw"
---

# Design System: AI Bouncer

## Overview

**Creative North Star: "The Decompression Instrument"**

AI Bouncer turns a software decision into a controlled technical descent. The interface feels like a dive computer built for evidence: abyssal layers deepen from cyan signal to coral danger, one illuminated tether connects every checkpoint, and compact readouts make the system feel observable rather than theatrical.

The visual system is dense but disciplined. Operational controls stay rectilinear and quiet while the 9:16 decision stage carries the atmosphere, using marine texture, hairline gates, glass-like readouts, and a decisive turnaround zone. Color, symbols, labels, and plain-language reasons work together so no verdict depends on hue alone.

**Key Characteristics:**

- One continuous vertical depth axis organizes the decision story.
- Cyan evidence and coral danger create a directional descent, not decorative neon.
- Oxanium display type pairs with Source Code Pro readouts and restrained system text.
- Kev and SemIf remain separately identifiable at every gate.
- Replay, live inference, probability, confidence, and benchmark accuracy are visibly distinct.

## Colors

The palette starts in near-black ocean ink, reserves cyan for inspection and structure, gives each model its own signal color, and introduces warm colors only as safety meaning intensifies.

### Primary

- **Thermocline Cyan** (`thermocline`): Illuminates the central tether, evidence boundary, selected controls, focus treatment, and active inspection state.

### Secondary

- **Kev Aqua** (`kev-signal`): Identifies Kev labels and probability values without implying the decision outcome.
- **SemIf Violet** (`semif-signal`): Identifies SemIf labels and probability values with equal visual weight.

### Tertiary

- **Safe Ascent Green** (`pass`): Marks cleared gates, live availability, and ALLOW states.
- **Decompression Amber** (`warn`): Marks ambiguous gates and ASK HUMAN states.
- **Turnaround Coral** (`danger`): Marks failed gates, blocked actions, and the final safety boundary.

### Neutral

- **Ocean Black** (`ocean-black`): Frames the app and supplies the deepest page background.
- **Abyss Ink** (`abyss`): Grounds the decision stage and primary dark fields.
- **Midnight Blue** (`midnight`): Supports readouts and quiet control surfaces.
- **Marine Snow** (`marine-snow`): Carries primary text and high-contrast instrument marks.
- **Muted Sonar** (`muted-sonar`): Carries explanations, inactive labels, and secondary metadata.
- **Danger Depth** (`danger-depth`): Underlays blocked states without competing with coral text and borders.

### Named Rules

**The Descent Spectrum Rule.** Cyan reveals evidence; amber interrupts certainty; coral marks the point where policy turns the action around.

**The Two Signals Rule.** Kev aqua and SemIf violet identify model provenance only; pass, warn, and fail colors communicate state.

## Typography

**Display Font:** Oxanium (with sans-serif fallback)  
**Body Font:** system UI sans-serif  
**Label/Mono Font:** Source Code Pro (with ui-monospace fallback)

**Character:** Oxanium gives the control deck a compressed technical headline voice, while Source Code Pro makes probabilities, gates, labels, and verdicts feel measured. System text is reserved for longer explanations where effortless reading matters more than instrument character.

### Hierarchy

- **Display** (700, responsive clamp, 0.95 line-height): Control-deck headlines and major framing statements.
- **Verdict** (700, container-responsive, 0.85 line-height): The largest typographic event in the stage; BLOCK, ASK HUMAN, or ALLOW.
- **Readout** (700, container-responsive, 1 line-height): Model probabilities and other numeric instrument values.
- **Body** (400, 14px, 1.7 line-height): Explanations, source notes, evidence, and benchmark context.
- **Label** (600, 9px, 0.14em tracking): Uppercase section headings, field labels, safety notes, and compact metadata.

### Named Rules

**The Readout Integrity Rule.** Probabilities, model confidence, and benchmark accuracy always use explicit labels; typography must never make them look interchangeable.

## Layout

The signature surface is a fixed-ratio 9:16 decision stage (`941 / 1672`) built as one continuous vertical plot. Five sequential gates descend around a central tether: gate labels occupy the left, Kev reads near the inner-left column, and SemIf reads near the inner-right column. The hidden-evidence thermocline interrupts the fourth gate; the fifth gate then leads into a full-width turnaround verdict.

On viewports below the wide breakpoint, the stage and control deck stack at up to the stage width. At `1100px` and above, the app becomes a two-column workstation: a sticky stage between `540px` and `740px`, and a control deck between `440px` and `540px`, separated by a responsive gutter. At `520px` and below, scenario choices collapse to one column and the four-way source selector becomes a two-by-two grid.

Control-deck spacing follows a compact rhythm: 8px gaps for repeated choices, 12px for labels and internal field padding, 18px before major actions, 24px minimum shell padding, and 30px between control sections. The stage itself uses container-relative units so its hierarchy scales as one composed instrument.

**The One Axis Rule.** New decision dimensions extend the descent; they do not become disconnected cards or dashboard tiles.

## Elevation & Depth

Depth comes primarily from tonal layering, atmospheric raster texture, luminous hairlines, and the cyan-to-coral gradient on the central tether. Shadows are glow cues rather than generic floating-card elevation: they call attention to an active node, the evidence thermocline, the dangerous turnaround, or the desktop stage as a whole.

### Shadow Vocabulary

- **Signal Pulse** (`0 0 1.2cqw rgba(61, 224, 243, 0.6)`): Keeps the tether and active nodes legible against the ocean texture.
- **Thermocline Chamber** (`0 0 3.2cqw rgba(61, 224, 243, 0.48), inset 0 0 4cqw rgba(61, 224, 243, 0.11)`): Separates revealed evidence from ordinary gates.
- **Turnaround Bloom** (`0 -1cqw 3cqw rgba(255, 58, 65, 0.2)`): Signals the final safety boundary without lifting it like a card.
- **Desktop Stage** (`0 35px 90px rgba(0, 0, 0, 0.55)`): Gives the recordable stage physical separation only in the wide workstation layout.

### Named Rules

**The Instrument Glow Rule.** Glow follows signal and state; ordinary containers remain flat and are separated by hairline borders.

## Shapes

The control deck is deliberately angular: scenario choices, source segments, fields, and the primary inspection action use square corners. The stage uses three exceptions with functional meaning: full pills enclose actions and source mode, small rounded rectangles frame gates and evidence, and circles mark nodes and status symbols. The thermocline and turnaround introduce sculpted notches and arcs to show an actual change in depth.

**The Meaningful Curve Rule.** Rounded or curved forms indicate a signal, action capsule, node, or depth transition; general-purpose panels stay rectilinear.

## Components

### Buttons

- **Shape:** The primary control-deck action is full width and square-cornered; stage evidence actions use gently rounded instrument frames.
- **Primary:** Thermocline cyan fill, abyss text, strong uppercase mono label, 60px minimum height, and a quiet cyan glow.
- **Hover / Focus:** Borders brighten on hover; keyboard focus uses a high-contrast white outline offset from the control. Disabled inspection states retain their label and drop to 65% opacity.
- **Secondary / Ghost:** Scenario and source controls are dark, hairline-bordered segments. Active state is shown through fill or inset cyan, not color alone.

### Chips

- **Style:** Replay and live mode use outlined pills with a replay ring or glowing live dot, an explicit text label, and wide letter spacing.
- **State:** Replay is thermocline cyan; live is safe green. The label and icon remain present so mode is never color-only.

### Cards / Containers

- **Corner Style:** Control-deck containers are square; stage gates use compact readout rounding.
- **Background:** Controls use abyss and midnight layers. The stage keeps translucent gate interiors so the depth texture remains continuous.
- **Shadow Strategy:** Gates stay flat at rest; only active inspection, thermocline evidence, and turnaround verdicts glow.
- **Border:** One-pixel or container-relative hairlines define choices and gates.
- **Internal Padding:** Compact 12–14px control padding; stage padding scales with its container.

### Inputs / Fields

- **Style:** Full-width abyss fields with a cool blue hairline, square corners, 12px internal padding, and Source Code Pro input text.
- **Focus:** The border and a one-pixel outer outline both switch to cyan.
- **Error / Disabled:** Live failures appear as labeled amber evidence callouts; missing model evidence resolves to NO VERDICT rather than a safe state.

### Navigation

There is no global navigation. The numbered control deck—choose trap, select bouncer, inspect request, evidence and benchmark—acts as the local task sequence, with persistent section markers and a disclosure control for technical depth.

### Decompression Gate

Each gate combines a numbered safety question with side-by-side Kev and SemIf probability readouts plus a labeled PASS, WARN, FAIL, or OFF status symbol. During inspection, gates resolve sequentially: unresolved gates recede, the active gate glows, and completed gates return at reduced intensity. The final resolver is visually separate from model readings and always states that the represented action was not executed.

## Do's and Don'ts

### Do:

- **Do** preserve the single vertical descent from proposed action through five gates to the resolver verdict.
- **Do** pair every pass, warning, failure, replay, live, and verdict color with a symbol or explicit label.
- **Do** keep Kev probability, SemIf probability, model confidence, and fixed-benchmark accuracy separately labeled.
- **Do** use glow only to trace active evidence, inspection progress, or a policy boundary.
- **Do** respect reduced-motion preferences by collapsing the sequential scan into an immediate resolved state.

### Don't:

- **Don't** rearrange the safety decision into a generic grid of glowing AI cards.
- **Don't** use Kev aqua or SemIf violet as verdict colors; they identify model provenance.
- **Don't** present replay fixtures as fresh inference or imply that a represented action was executed.
- **Don't** soften unavailable or malformed model evidence into ALLOW; the interface must fail visibly and conservatively.
- **Don't** add rounded containers indiscriminately; curves must retain their depth, signal, or action meaning.
