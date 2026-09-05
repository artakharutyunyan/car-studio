"""Convert licensed source assets to the studio's selectable glTF contract.
Run with bpy 4.5 and a source path: python scripts/convert-classic-cars.py CAR SOURCE
CAR is ferrari-f40 or porsche-930. Outputs stay in public/models.
"""
import os,sys,json,math,ctypes,importlib.util
# Disable GPU probing in the macOS sandbox; conversion and Cycles use the CPU.
if os.environ.get('CODEX_SANDBOX')=='seatbelt':
 lib=ctypes.CDLL(importlib.util.find_spec('bpy').origin)
 backend=getattr(lib,'_Z39GPU_backend_type_selection_set_override15eGPUBackendType')
 backend.argtypes=[ctypes.c_int];backend.restype=None;backend(0)
import bpy
from mathutils import Vector,Matrix
car,source=sys.argv[1:3];ferrari=car=='ferrari-f40'
os.environ['BLENDER_USER_RESOURCES']='/private/tmp/car-studio-blender-resources'
if ferrari:bpy.ops.wm.open_mainfile(filepath=os.path.abspath(source),use_scripts=False)
else:
 bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=os.path.abspath(source))
bpy.context.view_layer.update()
# Preserve mirror references until all modifiers have been evaluated.
for o in list(bpy.context.scene.objects):
 if o.type!='MESH':continue
 if not ferrari and (o.name=='Object_49' or any(m and m.name in ['coat','material_0'] for m in o.data.materials)):
  bpy.data.objects.remove(o,do_unlink=True);continue
 for mod in list(o.modifiers):
  if mod.type=='NODES':o.modifiers.remove(mod)
  elif mod.type=='SUBSURF':
   level=0 if any(m and m.name=='Grills' for m in o.data.materials) else 1
   mod.levels=level;mod.render_levels=level
if ferrari:
 for o in bpy.context.scene.objects:
  if o.type=='MESH' and len(o.data.polygons)>18000:
   mod=o.modifiers.new('Browser mesh budget','DECIMATE');mod.ratio=.45
bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH' and len(o.data.polygons)]
snapshots=[(o,bpy.data.meshes.new_from_object(o.evaluated_get(deps),depsgraph=deps),o.matrix_world.copy()) for o in meshes]
for o,data,matrix in snapshots:
 o.modifiers.clear();o.parent=None;o.matrix_world=Matrix.Identity(4);o.data=data;data.transform(matrix);o['source_object']=o.name
for o in list(bpy.context.scene.objects):
 if o not in meshes:bpy.data.objects.remove(o,do_unlink=True)
bpy.context.view_layer.update()
# Normalize dimensions, floor and center; both source cars point toward -Y.
points=[v.co for o in meshes for v in o.data.vertices]
lo=Vector([min(v[a] for v in points) for a in range(3)]);hi=Vector([max(v[a] for v in points) for a in range(3)])
scale=(4.358 if ferrari else 4.29)/(hi.y-lo.y);center=(lo+hi)/2
transform=Matrix.Scale(scale,4)@Matrix.Translation(Vector((-center.x,-center.y,-lo.z)))
for o in meshes:o.data.transform(transform)
# Use physical paint and glass that render consistently in the browser.
def physical(m,color,metal=.0,rough=.4,alpha=1,coat=0):
 m.use_nodes=True;m.node_tree.nodes.clear();out=m.node_tree.nodes.new('ShaderNodeOutputMaterial');p=m.node_tree.nodes.new('ShaderNodeBsdfPrincipled');m.node_tree.links.new(p.outputs['BSDF'],out.inputs['Surface']);p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;p.inputs['Alpha'].default_value=alpha;p.inputs['Coat Weight'].default_value=coat
 if alpha<1:m.surface_render_method='BLENDED'
 return p
for m in bpy.data.materials:
 name=m.name.lower()
 if ferrari:
  color=(.014,.019,.024);metal=.05;rough=.5
  if name=='body':color=(.65,.009,.013);metal=.3;rough=.27
  elif 'rubber' in name:color=(.014,.016,.018);rough=.77
  elif any(s in name for s in ['cromium','metals','mirror','metal-black']):color=(.48,.53,.59);metal=.9;rough=.24
  elif 'messing' in name:color=(.5,.29,.08);metal=.7
  elif 'red' in name or name=='rot':color=(.45,.006,.009);rough=.25
  elif 'orange' in name:color=(.8,.14,.004);rough=.25
  elif 'headlight' in name or name=='weis':color=(.63,.7,.78);rough=.2;metal=.3
  elif 'logo' in name:color=(.9,.63,.02);metal=.15
  elif name=='glass and windows':color=(.013,.025,.04);metal=.3;rough=.13
  physical(m,color,metal,rough,coat=.65 if name=='body' else 0)
 else:
  if name=='paint':physical(m,(.95,.64,.012),.28,.28,coat=.7)
  elif name=='glass':physical(m,(.018,.032,.043),.3,.16)
  elif name=='930_lights_refraction':physical(m,(.48,.55,.62),.15,.18,alpha=.3)
  else:
   # Disable transmission for consistent, low-cost browser rendering.
   if m.node_tree:
    for p in m.node_tree.nodes:
     if p.type=='BSDF_PRINCIPLED':p.inputs['Transmission Weight'].default_value=0
# Split actual disconnected geometry, keeping detailed tires and grilles intact.
for o in list(meshes):
 mats=' '.join(m.name.lower() for m in o.data.materials if m)
 if any(w in (o.name.lower()+' '+mats) for w in ['tire','rim','bolt','grills']):continue
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
 bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT')
 if not ferrari:
  # glTF duplicates vertices at UV seams. Weld only coincident vertices first.
  bpy.ops.mesh.remove_doubles(threshold=.00001)
 bpy.ops.mesh.separate(type='LOOSE');bpy.ops.object.mode_set(mode='OBJECT')
# Classify visible geometry; no synthetic Tesla systems are added.
bpy.context.view_layer.update();entries=[]
for o in sorted(bpy.context.scene.objects,key=lambda o:o.name):
 if o.type!='MESH' or not len(o.data.polygons):continue
 pts=[o.matrix_world@Vector(v) for v in o.bound_box];lo=Vector([min(p[a] for p in pts) for a in range(3)]);hi=Vector([max(p[a] for p in pts) for a in range(3)]);c=(lo+hi)/2;size=hi-lo
 used={p.material_index for p in o.data.polygons};mats=' '.join(m.name.lower() for n,m in enumerate(o.data.materials) if m and n in used);name=o.get('source_object',o.name)
 group='body';label='Exterior detail'
 if any(s in name.lower()+' '+mats for s in ['tire','rim','bolt']):group='wheels';label='Tire and tread' if 'tire' in name.lower()+' '+mats else 'Alloy wheel detail'
 elif mats=='glass' or mats=='glass and windows':group='glass';label='Glazing'
 elif ferrari and name in ['Circle','Circle.001']:group='drive';label='Exhaust detail'
 elif not ferrari and c.y>1.1 and c.z<.45 and size.x<.5 and 'chrome' in mats:group='drive';label='Exhaust detail'
 elif abs(c.x)>.55 and -.9<c.y<.65 and size.y>.45 and size.z>.25 and size.x<.45 and (mats=='body' or mats=='paint'):group='doors';label='Door panel'
 elif abs(c.x)<.7 and -.75<c.y<.9 and .35<c.z<1.1 and ('plastic' in mats or mats=='black') and size.y<1.7:group='cabin';label='Cockpit trim'
 elif mats=='body' or mats=='paint':
  label='Hood panel' if c.y<-.8 and c.z>.5 else 'Rear body panel' if c.y>.9 else 'Body panel'
 elif 'light' in mats:label='Front lighting element' if c.y<0 else 'Rear lighting element'
 elif 'logo' in mats or 'sticker' in mats:label='Badge and lettering'
 elif 'chrome' in mats or 'cromium' in mats:label='Metallic trim'
 elif 'grill' in mats:label='Vent grille'
 if abs(c.x)>.3:label+=(' · left' if c.x>0 else ' · right')
 if group=='wheels':label+=(' · front' if c.y<0 else ' · rear')
 o.name=f'{group}_{len(entries):04d}';o['part']=group;o['label']=label;o['component']=o.name
 # Source metadata unrelated to the exported geometry is not needed.
 for k in list(o.keys()):
  if k not in ['part','label','component','source_object']:del o[k]
 entries.append({'id':o.name,'part':group,'label':label,'source':name,'center':list(c),'size':list(size),'faces':len(o.data.polygons)})
for img in bpy.data.images:
 if img.size[0]>1024 or img.size[1]>1024:
  factor=1024/max(img.size);img.scale(max(1,int(img.size[0]*factor)),max(1,int(img.size[1]*factor)))
# Export individual selectable objects; all materials/textures embedded.
os.makedirs('public/models',exist_ok=True)
bpy.ops.export_scene.gltf(filepath=os.path.abspath(f'public/models/{car}.glb'),export_format='GLB',export_extras=True,export_cameras=False,export_lights=False,export_yup=True)
metadata={'creator':'Seatla Morake' if ferrari else 'Karol Miklas','source':'https://www.blendkit.com/asset-gallery-detail/ac7deb9f-9e90-45ec-b7d2-d390e9bcf5f1/' if ferrari else 'https://sketchfab.com/3d-models/free-1975-porsche-911-930-turbo-8568d9d14a994b9cae59499f0dbed21e','license':'Blendkit Royalty Free' if ferrari else 'CC BY 4.0','modifications':'Normalized scale, adapted physical materials and paint, separated source mesh geometry.','objects':entries}
open(f'public/models/{car}-manifest.json','w').write(json.dumps(metadata,indent=2)+'\n')
print('EXPORTED',car,len(entries),'pieces',sum(e['faces'] for e in entries),'faces',flush=True)
