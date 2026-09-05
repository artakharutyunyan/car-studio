# Collection validation

Validated on 2026-09-05.

- TypeScript passes (`npx tsc --noEmit`).
- Application lint passes (`npx oxlint app vercel-app`). Repository-wide lint still reports existing issues in the bundled `components/ui` and `hooks/use-mobile.ts`; these unrelated files were not changed.
- Both production builds pass: Vinext / Cloudflare and the standalone Vercel browser app. The build reports a large JavaScript chunk warning.
- Three.js GLTFLoader checks pass for all sixteen models: unique selectable IDs, catalog correspondence, finite geometry bounds, embedded texture payloads, non-overlapping exploded layouts, and camera coverage at three viewport proportions.
- Selectable counts: Model X 334, F40 185, Porsche 930 318, Phantom 423, DB5 108, Roma 181, Diablo 72, Range Rover 707, Mercedes 300 SL 115, AMG ONE 184, BMW M1 186, BMW M3 E30 93, SF-23 168, AMR23 160, W14 138, MP4/5 132.
- The Porsche manifest excludes its original antenna object. The regenerated model and card preview were inspected.
- Existing explosion and pointer tests pass, including drag-return, pinch, cancellation, and tap recovery.
- Local HTTP checks return 200 for both collections and all sixteen car routes. An unknown car returns 404.
- Exported models were rendered in Blender for visual asset inspection. Incorrect source axes, source rig transforms, and damaged optimized F1 copies were corrected; the F1 assets now use their original detailed source geometry.
- All project files, including hidden files, dependencies, binaries, and build output, were searched for the user-specified unwanted attribution string; no matches were found. The former nested project directory is absent.

Browser interaction and device frame-rate QA were not run. Geometry checks do not decode texture pixels; Blender renders provide the separate visual asset check. WebMCP registration remains feature-detected, with execution in a supported browser context unverified.

See [MODEL_SOURCES.md](MODEL_SOURCES.md) for sources, licenses, adaptations, and model scope.
