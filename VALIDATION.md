# Collection validation

Validated on 2026-09-05. Re-validated on 2026-09-06 after: an added illustrative "TOYOTA" badge on the Supra's front fascia (the source model had none); the Williams FW14B, first rebalanced from a solid-blue synthetic livery to a white/blue/yellow synthetic split, then replaced outright with a different, properly textured source model carrying real Canon/Camel/Elf/Labatt's-era sponsor decals; the Aston Martin DB5 recolored from the source model's teal-green to Silver Birch; and eight new road cars — Rolls-Royce Cullinan, Kia Forte, Audi R8, Ferrari LaFerrari, Ferrari 250 GTO, Lamborghini Urus, Porsche 959, and Porsche 918 Spyder. Each new source was checked for provenance red flags before use; one higher-detail Cullinan candidate and several Ferrari candidates were rejected after their mesh names or listing text disclosed non-CC origins (a paid-asset watermark, or mobile-game/file-share sourcing contradicting the license tag). All were verified with `validate-collection.mjs`, `validate-explosion.mjs`, and `validate-touch.mjs`, and card renders were generated or regenerated with `render-car-cards.py`.

- TypeScript passes (`npx tsc --noEmit`).
- Application lint passes (`npx oxlint app vercel-app`). Repository-wide lint still reports existing issues in the bundled `components/ui` and `hooks/use-mobile.ts`; these unrelated files were not changed.
- Both production builds pass: Vinext / Cloudflare and the standalone Vercel browser app. The build reports a large JavaScript chunk warning.
- Three.js GLTFLoader checks pass for all thirty-two models: unique selectable IDs, catalog correspondence, finite geometry bounds, embedded texture payloads, non-overlapping exploded layouts, and camera coverage at three viewport proportions.
- Selectable counts: Model X 334, F40 185, Porsche 930 318, Phantom 423, DB5 108, Roma 181, Diablo 72, Countach 216, Range Rover 707, Mercedes 300 SL 115, AMG ONE 184, BMW M1 186, BMW M3 E30 93, Supra Mk4 87 (includes the added badge piece), Nissan Skyline R34 83, Audi Quattro S1 63, Bugatti Veyron 113, Jaguar E-Type 86, McLaren F1 GTR Longtail 257, Cullinan 113, Kia Forte 173, Audi R8 167, Ferrari LaFerrari 347, Ferrari 250 GTO 144, Lamborghini Urus 331, Porsche 959 292, Porsche 918 Spyder 399, SF-23 168, AMR23 160, W14 138, MP4/5 132, and Williams FW14B 140.
- The Porsche 930 manifest excludes its original antenna object. The regenerated model and card preview were inspected.
- Existing explosion and pointer tests pass, including drag-return, pinch, cancellation, and tap recovery.
- Local HTTP checks return 200 for both collections and all thirty-two car routes. An unknown car returns 404.
- Exported models were rendered in Blender for visual asset inspection. Incorrect source axes, source rig transforms, and damaged optimized F1 copies were corrected; the F1 assets now use their original detailed source geometry.
- All project files, including hidden files, dependencies, binaries, and build output, were searched for the user-specified unwanted attribution string; no matches were found. The former nested project directory is absent.

Browser interaction and device frame-rate QA were not run. Geometry checks do not decode texture pixels; Blender renders provide the separate visual asset check. WebMCP registration remains feature-detected, with execution in a supported browser context unverified.

See [MODEL_SOURCES.md](MODEL_SOURCES.md) for sources, licenses, adaptations, and model scope.
