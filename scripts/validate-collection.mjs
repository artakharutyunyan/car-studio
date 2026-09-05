import fs from 'node:fs';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import {GLTFLoader} from 'three/examples/jsm/loaders/GLTFLoader.js';
import {createExplosionLayout,layoutCenter,overviewDirection} from '../app/explosion-layout.ts';

// Geometry tests do not decode image pixels; texture payloads are checked below.
globalThis.self=globalThis;
const manager=new THREE.LoadingManager();
manager.addHandler(/.*/, {load(_url,onLoad){const texture=new THREE.Texture();queueMicrotask(()=>onLoad(texture));return texture;}});
const names=fs.readdirSync('public/models').filter(f=>f.endsWith('-manifest.json')).map(f=>f.replace('-manifest.json',''));
for(const name of names){
 const bytes=fs.readFileSync(`public/models/${name}.glb`);
 const jsonLength=bytes.readUInt32LE(12);const gltf=JSON.parse(bytes.subarray(20,20+jsonLength).toString());
 for(const image of gltf.images||[]){assert(Number.isInteger(image.bufferView),`${name}: texture is not embedded`);assert(gltf.bufferViews[image.bufferView].byteLength>0);}
 const asset=await new GLTFLoader(manager).register(()=>({name:'EXT_texture_webp',loadTexture:()=>Promise.resolve(new THREE.Texture())})).parseAsync(bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),'');
 asset.scene.rotation.y=-Math.PI/2;asset.scene.updateMatrixWorld(true);
 const catalog=JSON.parse(fs.readFileSync(`public/models/${name}-manifest.json`)).objects;
 const pieces=[];const ids=new Set();
 asset.scene.traverse(o=>{if(o.userData.component){assert(!ids.has(o.userData.component),'Duplicate selectable id');ids.add(o.userData.component);const bounds=new THREE.Box3().setFromObject(o);assert(!bounds.isEmpty());assert(bounds.min.toArray().concat(bounds.max.toArray()).every(Number.isFinite));pieces.push({id:o.userData.component,part:o.userData.part,bounds});}});
 assert.equal(ids.size,catalog.length);assert(catalog.every(p=>ids.has(p.id)));
 assert(catalog.every(p=>['body','glass','doors','cabin','wheels','drive','suspension'].includes(p.part)));
 if(name==='porsche-930')assert(!catalog.some(p=>p.source==='Object_49'),'Porsche antenna should be removed');
 const result=createExplosionLayout(pieces),slots=[...result.pieces.values()];
 assert.equal(slots.length,catalog.length);
 for(let i=0;i<slots.length;i++)for(let j=i+1;j<slots.length;j++){
  const a=slots[i],b=slots[j];assert(Math.abs(a.u-b.u)>=(a.width+b.width)/2-1e-7||Math.abs(a.v-b.v)>=(a.height+b.height)/2-1e-7,`${name}: overlapping slots`);
 }
 for(const aspect of [.5,1.3,2]){
  const camera=new THREE.PerspectiveCamera(37,aspect,.05,500),tan=Math.tan(THREE.MathUtils.degToRad(37/2));
  const distance=Math.max(result.height/(2*tan),result.width/(2*tan*aspect))*1.18+3;
  camera.position.copy(layoutCenter).addScaledVector(overviewDirection,distance);camera.lookAt(layoutCenter);camera.updateMatrixWorld(true);
  for(const piece of pieces){const t=result.pieces.get(piece.id).translation;for(const x of [piece.bounds.min.x,piece.bounds.max.x])for(const y of [piece.bounds.min.y,piece.bounds.max.y])for(const z of [piece.bounds.min.z,piece.bounds.max.z]){const point=new THREE.Vector3(x,y,z).add(t).project(camera);assert(Math.abs(point.x)<1&&Math.abs(point.y)<1&&point.z<1,`${name}: ${piece.id} outside view`);}}
 }
 console.log(`${name}: ${catalog.length} pieces; catalog, embedded textures and exploded framing verified.`);
}
