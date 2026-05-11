# Building an organic project dashboard for interconnected creative work

The ideal system for managing FAITHH, Constella, and Tom Cat Sound isn't a traditional task manager—it's a **visual knowledge environment** where insights flow between projects and surface what's ready to work on next. Three approaches emerge as most promising: using Obsidian with Canvas and Dataview for a fully customizable local solution, leveraging Excalidraw's JSON-native format for programmatic whiteboard generation from your existing state files, or building a custom tldraw-based dashboard integrated directly into FAITHH.

## The "chip synthesis" philosophy has a name: Zettelkasten thinking

Your intuition about work on one project illuminating the next aligns precisely with Zettelkasten methodology. The core insight from Zettelkasten practitioners: **"Ignore project boundaries and always benefit from all your knowledge work for every project."** This means your FAITHH AI work generates insights that might unlock a Constella creative breakthrough, which in turn reveals a new service offering for Tom Cat Sound.

The practical implementation requires two layers: a **knowledge layer** where atomic insights accumulate regardless of source project, and a **project layer** with lightweight structure notes that pull from this shared pool. Tools like Obsidian excel here because bi-directional linking creates automatic discovery of unexpected connections. When you add a note about audio processing for Tom Cat Sound, backlinks might surface related FAITHH architecture decisions you'd forgotten.

This differs fundamentally from rigid task management. Traditional tools force you to assign each task to exactly one project, breaking the natural flow of creative work. A Zettelkasten-informed system lets the same insight serve multiple projects simultaneously.

## Visual PKM tools ranked for your use case

**Obsidian Canvas** emerges as the strongest option for several reasons. Its **JSON Canvas format** is an open specification, meaning your existing `project_states.json` could be programmatically converted into visual canvas elements. The Dataview plugin transforms your vault into a queryable database, enabling dashboards like "show all decisions from the last 30 days across all projects." Canvas files store as local JSON, preserving full data ownership and enabling custom scripts.

For a more polished whiteboard-first experience, **Heptabase** offers the closest thing to a "digital dry erase board" specifically designed for PKM. Cards live on infinite canvases with visual sections and mind-mapping tools. The tradeoff is **$12/month** pricing and less programmatic control—though an unofficial MCP server exists for backup data access.

**Logseq** provides a free, open-source alternative with whiteboards, though less refined than competitors. Its block-based architecture means every piece of information has a unique ID that can be referenced anywhere, creating highly granular cross-project connections.

| Tool | Canvas quality | JSON/MD integration | Cost | Best for |
|------|---------------|---------------------|------|----------|
| Obsidian | ★★★★★ | Native | Free | Maximum flexibility, local-first |
| Heptabase | ★★★★★ | Export only | $12/mo | Polished visual thinking |
| Logseq | ★★★★☆ | Native markdown | Free | Open-source, outliner-style |
| Tana | ★★★☆☆ | Limited | $10-16/mo | Supertag-based queries |

## Feeding your JSON files into visual whiteboards

**Excalidraw** is the standout for data-driven visualization. Its files are native JSON with a documented schema—rectangles, text, arrows, all defined as JSON objects with x/y coordinates. A Python or Node script could read your `project_states.json`, generate Excalidraw elements (boxes for each project state, connectors showing relationships), and output a `.excalidraw` file viewable in browser or embedded in Obsidian.

Sample element structure:
```json
{
  "type": "rectangle",
  "x": 100, "y": 200,
  "width": 200, "height": 100,
  "backgroundColor": "#e8f4ea"
}
```

**tldraw** offers even deeper customization for developers. Its React SDK allows defining custom shape types—you could create a "Project State" shape that renders live data from your JSON, with custom UI showing status, blockers, and related decisions. The workflow starter kit demonstrates data-fetching nodes that pull from external APIs, directly applicable to reading your state files.

For the Obsidian ecosystem, the **JSON Canvas specification** (jsoncanvas.org) provides interoperability. A script converting your project states to JSON Canvas format would produce files immediately openable in Obsidian Canvas, with nodes representing projects and edges showing dependencies.

## Decision-support patterns that reduce fatigue

The question "what should I work on next?" shouldn't require analysis every time—the system should surface answers automatically. Research on decision fatigue shows quality degrades after extended choice-making (Israeli judges granted parole significantly more often at day's start than before lunch). The solution: **progressive disclosure** and **smart defaults**.

The **Now/Next/Later** roadmap pattern, invented by product manager Janna Barstow, works exceptionally well for creative work. Only "Now" represents commitment; "Next" and "Later" indicate direction, not promises. This eliminates the anxiety of overloaded backlogs while maintaining strategic visibility.

**Energy-based task selection** matches task requirements to current capacity. Tag tasks by required energy level (deep creative, administrative, social), then filter your view based on current state. A morning dashboard might surface high-concentration FAITHH architecture work; afternoon shows Tom Cat Sound client communications.

**Momentum visualization** uses color gradients or heat maps to show which projects have recent activity. A project dormant for weeks might glow cooler, while one with commits yesterday shows warmer. This creates organic pressure toward neglected areas without rigid scheduling.

Practical implementation: create a dashboard with three sections—**Unblocked and matching current energy**, **Recently completed (momentum)**, and **Adjacent possible** (tasks enabled by recent completions).

## The interstitial journaling practice for capturing transitions

Tony Stubblebine's interstitial journaling directly addresses the "what next" question. Instead of maintaining todo lists, write brief notes at every task transition:

```
10:04 - Finished FAITHH context window optimization. Going to sketch Constella narrative flow.
11:32 - Constella session done, had insight about audio-reactive visuals → log for Tom Cat Sound.
11:35 - Energy dropping. Switching to email batch.
```

This practice serves multiple purposes: it clears mental residue from the previous task (reducing the **40% cognitive performance loss** from attention residue), creates a natural decision point, and generates a searchable log of work patterns. Reviewing a week of entries reveals which projects naturally cluster together, informing your "chip synthesis" intuitions.

The format integrates seamlessly with existing markdown workflows. Each entry becomes a searchable artifact; tagging with project names creates automatic aggregation.

## Theme-based productivity for unlimited time horizons

With unlimited time but need for direction, CGP Grey's **yearly theme system** provides strategic guidance without rigid goals. A theme like "Year of Integration" might guide decisions toward connecting your three projects—choosing FAITHH features that serve Constella, developing Tom Cat Sound offerings that showcase both.

The key insight: **"A good theme can't fail."** Unlike goals with binary success/failure, themes create directional pressure. The Theme System Journal uses half-filled circles for daily tracking—nothing/some/significant progress—acknowledging that partial advancement counts.

Cal Newport's **Slow Productivity** principles complement this for sustainable pacing:
- **Do fewer things**: Every active project carries "overhead tax" (emails, meetings, context switches). Limit active threads to increase completion rate and quality.
- **Work at natural pace**: Seasonal variation is normal. Plan lighter months deliberately.
- **One major project per day**: Not the only work, but the only deep project. This might mean Mondays for FAITHH architecture, Tuesdays for Constella writing, etc.

## Building a custom FAITHH-integrated dashboard

Given your existing FAITHH infrastructure, the most powerful option may be a **custom dashboard** reading directly from your state files. The architecture would combine:

1. **Data layer**: Your existing `project_states.json`, `decisions_log.json`, and `LIFE_MAP.md` as single source of truth
2. **Visualization layer**: tldraw or Excalidraw embedded component rendering state as visual elements
3. **Decision support layer**: Algorithms surfacing "ready to work on" items based on:
   - Dependencies resolved
   - Time since last touch
   - Energy requirements vs. current time of day
   - Theme alignment scoring

The tldraw SDK makes this approachable. A React component could:
- Parse your JSON on load
- Create custom shapes for each project with status indicators
- Draw connector arrows showing cross-project dependencies
- Highlight the "adjacent possible"—tasks newly unblocked by recent completions
- Update in real-time as state files change

This approach preserves your plain-text foundation while adding the organic visual layer you're seeking. FAITHH itself could analyze work patterns and surface insights: "You've been in Tom Cat Sound mode for 3 days—Constella has unblocked items that might benefit from fresh perspective."

## Recommended implementation path

**Phase 1 (immediate)**: Install Obsidian with Canvas and Dataview plugins. Create a dashboard canvas with embedded Dataview queries pulling from your markdown files. This gives you an immediate visual overview with zero custom code.

**Phase 2 (short-term)**: Write a script converting `project_states.json` to JSON Canvas or Excalidraw format. Generate a "big board" view that updates whenever state changes. Link this into your Obsidian vault.

**Phase 3 (integration)**: Build a custom tldraw dashboard into FAITHH, reading state files directly and implementing decision-support algorithms. Add interstitial journaling capture that FAITHH can analyze for pattern recognition.

**Daily practice**: Adopt interstitial journaling immediately—it requires no tools, just timestamps and brief notes. End each day with an anti-todo list (what you accomplished, not what remains). Review weekly to spot "chip synthesis" opportunities where insights crossed projects.

The underlying philosophy: your system should feel like a **thinking environment** rather than a task tracker. Projects exist as living spaces that naturally reveal connections, and "what to work on" emerges from the landscape rather than requiring constant deliberation. The combination of Zettelkasten knowledge management, visual canvases, and decision-support algorithms creates exactly the organic, interconnected view you're seeking—a digital space where working on FAITHH genuinely illuminates what Constella needs next.