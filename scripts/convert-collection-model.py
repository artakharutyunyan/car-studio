"""Normalize licensed glTF assets and expose their disconnected source geometry.
Usage: python scripts/convert-collection-model.py ID SOURCE LENGTH ORIENTATION
Orientation: native, x-up, x-length, or roma (source axes differ).
"""
import os,sys,json,math,ctypes,importlib.util,struct
if os.environ.get('CODEX_SANDBOX')=='seatbelt':
 lib=ctypes.CDLL(importlib.util.find_spec('bpy').origin);fn=getattr(lib,'_Z39GPU_backend_type_selection_set_override15eGPUBackendType');fn.argtypes=[ctypes.c_int];fn.restype=None;fn(0)
import bpy
from mathutils import Matrix,Vector
car,source,length,orientation=sys.argv[1:5];length=float(length)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=os.path.abspath(source));bpy.context.view_layer.update()
rotation={'native':Matrix.Identity(4),'flip':Matrix.Rotation(math.pi,4,'Z'),'x-up':Matrix.Rotation(math.pi/2,4,'X'),'x-length':Matrix.Rotation(-math.pi/2,4,'Z'),'roma':Matrix.Rotation(-math.pi/2,4,'Z'),'x-reverse':Matrix.Rotation(math.pi/2,4,'Z')}[orientation]
meshes=[]
deps=bpy.context.evaluated_depsgraph_get()
snapshots=[(o,bpy.data.meshes.new_from_object(o.evaluated_get(deps),depsgraph=deps),o.matrix_world.copy()) for o in bpy.context.scene.objects if o.type=='MESH' and len(o.data.polygons)]
for o,data,world in snapshots:
 if o.type!='MESH' or not len(o.data.polygons):continue
 mats=[m.name for m in o.data.materials if m]
 # Source presentation floors are not vehicle geometry.
 if car=='aston-martin-db5' and mats==['Material']:continue
 if car=='ferrari-roma' and mats==['Color_M08']:continue
 matrix=rotation@world;o.data=data;o.modifiers.clear();o.parent=None;o.matrix_world=Matrix.Identity(4);o.data.transform(matrix);o['source_object']=o.name;meshes.append(o)
for o in list(bpy.context.scene.objects):
 if o not in meshes:bpy.data.objects.remove(o,do_unlink=True)
points=[v.co for o in meshes for v in o.data.vertices];lo=Vector([min(v[a] for v in points) for a in range(3)]);hi=Vector([max(v[a] for v in points) for a in range(3)]);center=(lo+hi)/2
transform=Matrix.Scale(length/(hi.y-lo.y),4)@Matrix.Translation(Vector((-center.x,-center.y,-lo.z)))
for o in meshes:o.data.transform(transform)
for m in bpy.data.materials:
 if not m.node_tree:continue
 for p in m.node_tree.nodes:
  if p.type!='BSDF_PRINCIPLED':continue
  p.inputs['Transmission Weight'].default_value=0
  if car.startswith('f1-'):
   for link in list(p.inputs['Normal'].links):m.node_tree.links.remove(link)
   p.inputs['Roughness'].default_value=max(.35,p.inputs['Roughness'].default_value)
  if car=='rolls-royce-phantom':
   p.inputs['Roughness'].default_value=max(.2,p.inputs['Roughness'].default_value)
   if m.name=='Material.001':
    p.inputs['Base Color'].default_value=(.02,.035,.05,1);p.inputs['Alpha'].default_value=1
   if m.name=='Material.002':p.inputs['Base Color'].default_value=(.028,.036,.055,1);p.inputs['Metallic'].default_value=.4
  if 'windowglass' in m.name.lower() or (car=='aston-martin-db5' and 'transparent_glass' in m.name.lower()):
   for k in ['Base Color','Alpha']:
    for link in list(p.inputs[k].links):m.node_tree.links.remove(link)
   p.inputs['Base Color'].default_value=(.025,.045,.065,1);p.inputs['Alpha'].default_value=1;p.inputs['Metallic'].default_value=.3;p.inputs['Roughness'].default_value=.17
  if m.name=='ferrari_roma_carpaint':p.inputs['Base Color'].default_value=(.55,.018,.025,1);p.inputs['Metallic'].default_value=.35;p.inputs['Roughness'].default_value=.27
  if car=='bmw-m1' and m.name=='BMWM1_paint-material':
   p.inputs['Base Color'].default_value=(.8,.11,.015,1);p.inputs['Metallic'].default_value=.25;p.inputs['Roughness'].default_value=.28
  if car=='bmw-m3-e30' and m.name=='BMW_E30_M3_PAINT':
   p.inputs['Base Color'].default_value=(.62,.018,.025,1);p.inputs['Metallic'].default_value=.22;p.inputs['Roughness'].default_value=.3
  if car=='lamborghini-countach' and m.name=='CARO':
   p.inputs['Base Color'].default_value=(.82,.84,.84,1);p.inputs['Metallic'].default_value=.3;p.inputs['Roughness'].default_value=.24
  if car=='toyota-supra-mk4' and m.name=='Primary1.001':
   p.inputs['Base Color'].default_value=(.88,.18,.025,1);p.inputs['Metallic'].default_value=.22;p.inputs['Roughness'].default_value=.27
  if car=='lamborghini-diablo' and m.name=='Default':
   # Alpha blending this atlas across separated pieces creates depth-sorting
   # holes in WebGL, even though Blender's offline render looks assembled.
   for link in list(p.inputs['Alpha'].links):m.node_tree.links.remove(link)
   p.inputs['Alpha'].default_value=1
   m.surface_render_method='DITHERED'
# Weld UV-seam duplicate vertices, then separate actual disconnected islands.
for o in list(meshes):
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
 bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.remove_doubles(threshold=.00001);bpy.ops.mesh.normals_make_consistent(inside=False);bpy.ops.mesh.separate(type='LOOSE');bpy.ops.object.mode_set(mode='OBJECT')
bpy.context.view_layer.update()
def bounds(o):
 points=[v.co for v in o.data.vertices];lo=Vector([min(v[a] for v in points) for a in range(3)]);hi=Vector([max(v[a] for v in points) for a in range(3)]);return (lo+hi)/2,hi-lo
def solid_material(name,color,metallic=0,roughness=.38):
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metallic;p.inputs['Roughness'].default_value=roughness
 return m
williams_materials={
 'blue':solid_material('Williams blue',(.015,.08,.42),.16,.3),
 'yellow':solid_material('Williams yellow',(.95,.58,.015),.08,.32),
 'white':solid_material('Williams white',(.82,.84,.86),.12,.3),
 'wheel':solid_material('Williams wheels',(.012,.014,.018),.05,.58),
} if car=='f1-williams-fw14b' else None
small={}
for o in list(bpy.context.scene.objects):
 if o.type!='MESH' or not len(o.data.polygons):continue
 c,size=bounds(o);name=(o.get('source_object',o.name)+' '+' '.join(m.name for m in o.data.materials if m)).lower();group='body';label='Bodywork detail'
 if any(k in name for k in ['tire','tyre','wheel','rim','brake','hlfw','hrfw','hlrw','hrrw']):group='wheels';label='Wheel assembly detail'
 elif abs(c.x)>.52 and c.z<.65 and size.y<1.05 and size.z<1.05 and (abs(c.y)>length*.18):group='wheels';label='Wheel assembly detail'
 elif (car=='rolls-royce-phantom' and 'material.001' in name):group='glass';label='Glazing'
 elif any(k in name for k in ['window','windshield','transparent_glass','glass_tint']) or name.endswith(' glass'):group='glass';label='Glazing'
 elif any(k in name for k in ['interior','_int_','leather','seat','wood','steer','cockpit']):group='cabin';label='Cockpit detail'
 elif 'exhaust' in name:group='drive';label='Exhaust detail'
 elif 'suspension' in name:group='suspension';label='Suspension detail'
 if car.startswith('f1-') and group=='body':label='Chassis & aerodynamic detail'
 o['part']=group;o['label']=label
 if williams_materials:
  if group=='wheels':key='wheel'
  elif c.z>.58:key='blue'
  elif c.y<(-length*.28):key='yellow'
  elif abs(c.x)>.48:key='white'
  else:key='blue'
  o.data.materials.clear();o.data.materials.append(williams_materials[key])
 # Retain small trim in spatial clusters to bound browser draw calls.
 if max(size)<.18 or len(o.data.polygons)<8:
  key=(group,int(c.x*2),int(c.y*2),int(c.z*2));small.setdefault(key,[]).append(o)
for objects in small.values():
 if len(objects)<2:continue
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join()
# Welding invalidates imported custom corner normals. Rebuild smooth normals
# while preserving intentional creases at sharp panel edges.
for o in bpy.context.scene.objects:
 if o.type!='MESH':continue
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
 if o.data.has_custom_normals:bpy.ops.mesh.customdata_custom_splitnormals_clear()
 for edge in o.data.edges:edge.use_edge_sharp=False
 for polygon in o.data.polygons:polygon.use_smooth=True
 o.data.set_sharp_from_angle(angle=math.radians(35))
entries=[]
for o in sorted(bpy.context.scene.objects,key=lambda o:o.name):
 if o.type!='MESH' or not len(o.data.polygons):continue
 c,size=bounds(o);group=o['part'];label=o['label'];source_name=o.get('source_object',o.name)
 o.name=f'{group}_{len(entries):04d}';o['component']=o.name
 for k in list(o.keys()):
  if k not in ['part','label','component']:del o[k]
 entries.append({'id':o.name,'part':group,'label':label,'source':source_name,'center':list(c),'size':list(size),'faces':len(o.data.polygons)})
for img in bpy.data.images:
 if max(img.size)>1024:
  factor=1024/max(img.size);img.scale(max(1,int(img.size[0]*factor)),max(1,int(img.size[1]*factor)))
bpy.ops.export_scene.gltf(filepath=os.path.abspath(f'public/models/{car}.glb'),export_format='GLB',export_extras=True,export_cameras=False,export_lights=False,export_yup=True)
# The glTF exporter omits zero-area geometry. Catalog only exported pieces.
blob=open(f'public/models/{car}.glb','rb').read();exported=json.loads(blob[20:20+struct.unpack_from('<I',blob,12)[0]])
exported_ids={n.get('extras',{}).get('component') for n in exported.get('nodes',[])}
entries=[e for e in entries if e['id'] in exported_ids]
open(f'public/models/{car}-manifest.json','w').write(json.dumps({'modifications':'Normalized orientation and scale; removed presentation floor; separated and clustered source geometry; adapted browser materials.','objects':entries},indent=2)+'\n')
print('EXPORTED',car,len(entries),'pieces',sum(e['faces'] for e in entries),'faces',flush=True)
