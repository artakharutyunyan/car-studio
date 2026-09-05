# Car Studio

An interactive collection of twelve road cars and four Formula 1 cars. Choose a card, orbit the model, isolate a component or mesh piece, and use the explosion slider to separate its geometry.

Road cars: Ferrari F40, Porsche 911 Turbo (930), Rolls-Royce Phantom Extended Series II, Aston Martin DB5, Ferrari Roma, Lamborghini Diablo SV, Range Rover, Mercedes-Benz 300 SL Gullwing, Mercedes-AMG ONE, BMW M1 Procar, BMW M3 E30, and Tesla Model X. Tesla appears last in the collection.

The separate Formula 1 collection includes the 2023 Ferrari SF-23, Aston Martin AMR23, Mercedes-AMG W14, and 1989 McLaren-Honda MP4/5.

## Run locally

Requires Node.js 22.13+ and npm. Everything lives directly in this directory.

```sh
npm ci
npm run dev -- --port 3015
```

Open http://localhost:3015/. Formula 1 is at `/formula-1`; individual studios use `/cars/<vehicle-id>`.

## Builds and validation

```sh
npx tsc --noEmit
npx oxlint app vercel-app
node --experimental-strip-types scripts/validate-collection.mjs
node --experimental-strip-types scripts/validate-explosion.mjs
node --experimental-strip-types scripts/validate-touch.mjs
npm run build
npm run build:vercel
```

`npm run build` produces the Vinext / Cloudflare app. `npm run build:vercel` builds the standalone browser app in `dist/vercel`. The checked-in Vercel configuration includes direct car and Formula 1 routes. No database or environment variables are required.

## Assets and scope

See [MODEL_SOURCES.md](MODEL_SOURCES.md) for creator credits, source links, licenses, and conversion notes. The Range Rover asset is **noncommercial, share-alike**; its license is distinct from the other models.

The models have different source detail levels; the Diablo is intentionally labeled a low-poly study. Selectable pieces are artist-authored geometry, not verified manufacturer service parts. Only the Tesla has illustrative battery, drive, and suspension geometry. The Porsche’s fender antenna has been removed.

Model conversion uses Blender’s `bpy` module. `scripts/convert-classic-cars.py` handles the F40 and 930; `scripts/convert-collection-model.py` handles the expanded collection. `scripts/render-car-cards.py` renders card images from the exported models. Original source downloads are not required to run the app.
