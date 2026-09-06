"""Render consistent collection cards from the actual exported vehicle meshes."""
import os,sys,ctypes,importlib.util,math
if os.environ.get('CODEX_SANDBOX')=='seatbelt':
 lib=ctypes.CDLL(importlib.util.find_spec('bpy').origin);backend=getattr(lib,'_Z39GPU_backend_type_selection_set_override15eGPUBackendType');backend.argtypes=[ctypes.c_int];backend.restype=None;backend(0)
import bpy
from mathutils import Vector
for car in sys.argv[1:] or ['model-x','ferrari-f40','porsche-930']:
 bpy.ops.wm.read_factory_settings(use_empty=True)
 bpy.ops.import_scene.gltf(filepath=os.path.abspath(f'public/models/{car}.glb'))
 # Normalize only the card composition; exported studio scale stays physical.
 # Normalize every car to the same apparent length in frame. Real-world length
 # varies from ~3m (2CV) to ~5.3m (S-Class/Cullinan); without this, only cars
 # near the old one-sided 4.9m cap filled the frame like the reference Tesla
 # card, while shorter cars looked small and any car with a corrupted bounding
 # box (wrong axis, stray geometry) rendered at the wrong apparent scale too.
 meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];points=[o.matrix_world@Vector(v) for o in meshes for v in o.bound_box];span=max(v.y for v in points)-min(v.y for v in points)
 if span>0:
  for o in meshes:o.scale*=4.9/span;o.location*=4.9/span
 scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=96;scene.cycles.use_denoising=False
 scene.render.resolution_x=960;scene.render.resolution_y=720;scene.render.resolution_percentage=100
 scene.render.threads_mode='FIXED';scene.render.threads=6
 scene.world=bpy.data.worlds.new('Studio');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.12,.15,.2,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.3
 def mat(name,color,metal=0,rough=.4):
  m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;return m
 bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.14));bpy.context.object.data.materials.append(mat('Studio floor',(.019,.029,.042),.2,.55))
 bpy.ops.mesh.primitive_cylinder_add(vertices=128,radius=3.05,depth=.12,location=(0,0,-.075));bpy.context.object.data.materials.append(mat('Display plinth',(.055,.075,.1),.4,.38))
 for radius in [2.88,3.0]:
  bpy.ops.mesh.primitive_torus_add(major_segments=128,minor_segments=6,location=(0,0,-.01),major_radius=radius,minor_radius=.007);bpy.context.object.data.materials.append(mat('Plinth rim',(.3,.4,.5),.8,.28))
 for pos,power,size in [((2,-4,6),2100,5),((-4,-1,3),1600,4),((0,5,5),2600,4)]:
  bpy.ops.object.light_add(type='AREA',location=pos);o=bpy.context.object;o.data.energy=power*.4;o.data.shape='DISK';o.data.size=size;o.rotation_euler=(Vector((0,0,.6))-o.location).to_track_quat('-Z','Y').to_euler()
 bpy.ops.object.camera_add(location=(6.5,-8.5,4.2));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,.6))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=7.1;scene.camera=cam
 scene.view_settings.view_transform='AgX';scene.view_settings.exposure=-.45
 os.makedirs('public/cars',exist_ok=True);scene.render.image_settings.file_format='WEBP';scene.render.image_settings.quality=90;scene.render.filepath=os.path.abspath(f'public/cars/{car}.webp')
 bpy.ops.render.render(write_still=True)
 print('RENDERED',car,flush=True)
