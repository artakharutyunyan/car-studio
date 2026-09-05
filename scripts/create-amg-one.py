"""Create the original stylized Mercedes-AMG One study used by Car Studio."""
import os, ctypes, importlib.util, math

if os.environ.get('CODEX_SANDBOX') == 'seatbelt':
    lib = ctypes.CDLL(importlib.util.find_spec('bpy').origin)
    backend = getattr(lib, '_Z39GPU_backend_type_selection_set_override15eGPUBackendType')
    backend.argtypes = [ctypes.c_int]
    backend.restype = None
    backend(0)

import bpy

bpy.ops.wm.read_factory_settings(use_empty=True)

def material(name, color, metallic=0.0, roughness=0.4):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*color, 1)
    shader.inputs['Metallic'].default_value = metallic
    shader.inputs['Roughness'].default_value = roughness
    return mat

silver = material('AMG silver paint', (.42, .48, .52), .78, .22)
carbon = material('Exposed carbon', (.012, .017, .019), .72, .28)
rubber = material('Tire rubber', (.008, .009, .01), 0, .6)
rim = material('Forged wheel', (.08, .1, .11), .86, .2)
glass = material('Dark glazing', (.015, .055, .075), .45, .12)
red = material('Performance accent', (.62, .015, .012), .45, .22)
light = material('LED lenses', (.7, .92, 1), .25, .12)

def cube(name, loc, scale, mat, bevel=.08, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(location=loc, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        mod = obj.modifiers.new('Sculpted edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
    obj.data.materials.append(mat)
    return obj

def ellipsoid(name, loc, scale, mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=24, location=loc)
    obj = bpy.context.object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(mat)
    return obj

# Low, layered body with a narrow nose and pronounced rear haunches.
cube('Carbon monocoque', (0, .02, .48), (.78, 1.95, .22), carbon, .16)
ellipsoid('Central body shell', (0, .05, .65), (.82, 1.9, .38), silver)
ellipsoid('Front left fender', (-.68, -1.34, .58), (.33, .78, .31), silver)
ellipsoid('Front right fender', (.68, -1.34, .58), (.33, .78, .31), silver)
ellipsoid('Rear left haunch', (-.68, 1.22, .65), (.38, .82, .38), silver)
ellipsoid('Rear right haunch', (.68, 1.22, .65), (.38, .82, .38), silver)
cube('Tapered front deck', (0, -1.37, .73), (.48, .78, .12), silver, .13)
cube('Rear deck', (0, 1.34, .82), (.63, .58, .13), silver, .13)

# Teardrop cockpit and roof intake.
ellipsoid('Cockpit canopy', (0, .15, 1.02), (.57, .88, .42), glass)
cube('Roof spine', (0, .58, 1.35), (.12, .5, .08), carbon, .06)
cube('Roof intake', (0, .72, 1.48), (.13, .28, .09), carbon, .05, rotation=(math.radians(-8), 0, 0))

# Aero surfaces and cooling openings.
cube('Front splitter', (0, -2.22, .28), (.91, .18, .045), carbon, .025)
cube('Front center blade', (0, -2.05, .34), (.08, .32, .12), carbon, .025)
cube('Left side skirt', (-.82, .12, .29), (.11, 1.42, .07), carbon, .03)
cube('Right side skirt', (.82, .12, .29), (.11, 1.42, .07), carbon, .03)
cube('Left side intake', (-.72, .47, .7), (.09, .42, .19), carbon, .04)
cube('Right side intake', (.72, .47, .7), (.09, .42, .19), carbon, .04)
cube('Rear diffuser', (0, 2.05, .31), (.78, .33, .09), carbon, .035)
cube('Rear wing', (0, 1.92, 1.18), (.82, .22, .055), carbon, .025)
for x in (-.62, .62):
    cube('Rear wing support', (x, 1.83, .94), (.035, .06, .24), carbon, .015)

# Wheels, brake discs, and red calipers.
for x in (-.91, .91):
    for y in (-1.42, 1.35):
        bpy.ops.mesh.primitive_torus_add(major_radius=.31, minor_radius=.105, major_segments=40, minor_segments=12,
                                        location=(x, y, .46), rotation=(0, math.pi / 2, 0))
        tire = bpy.context.object
        tire.name = f'Tire {x:+.0f} {y:+.0f}'
        tire.data.materials.append(rubber)
        bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=.245, depth=.11, location=(x, y, .46), rotation=(0, math.pi / 2, 0))
        wheel = bpy.context.object
        wheel.name = f'Wheel {x:+.0f} {y:+.0f}'
        wheel.data.materials.append(rim)
        cube(f'Brake caliper {x:+.0f} {y:+.0f}', (x * .995, y, .46), (.035, .055, .14), red, .015)

# Slim lighting and signature red center accents.
for x in (-.48, .48):
    cube('Front LED', (x, -2.01, .75), (.22, .035, .045), light, .02, rotation=(0, 0, math.radians(x * 18)))
    cube('Rear LED', (x, 1.91, .73), (.24, .035, .045), red, .02)
cube('Nose accent', (0, -1.7, .86), (.035, .43, .025), red, .012)
cube('Rear center exhaust', (0, 2.1, .68), (.16, .08, .07), carbon, .03)

for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        obj.select_set(True)

bpy.ops.export_scene.gltf(
    filepath='/private/tmp/mercedes-amg-one-source.glb',
    export_format='GLB', export_apply=True, export_yup=True,
    export_materials='EXPORT', export_cameras=False, export_lights=False,
)
print('EXPORTED /private/tmp/mercedes-amg-one-source.glb')
