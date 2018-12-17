bl_info = {
    "name": "Video Cube",
    "description": "",
    "author": "",
    "version": (0, 0, 1),
    "blender": (2, 70, 0),
    "location": "3D View > Create",
    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "",
    "category": "Development"
}

import bpy

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       EnumProperty,
                       PointerProperty,
                       )
from bpy.types import (Panel,
                       Operator,
                       PropertyGroup,
                       )

class VideoCubeSettings(PropertyGroup):

    max_slices = IntProperty(
        name = "Limit Slices",
        description="Maximum number of slices to generate",
        default = 400,
        min = 1,
        max = 100000
        )

    slice_thickness = FloatProperty(
        name = "Slice Thickness",
        description = "Width of each object representing a video frame",
        default = 1,
        min = 0.1,
        max = 10
        )
        
    slice_size = FloatProperty(
        name = "Slice Size",
        description = "Relative size of each object representing a video frame",
        default = 1,
        min = 0.1,
        max = 10
        )

    default_path = bpy.path.abspath("//Frames\\")
    file_path = bpy.props.StringProperty \
      (
      name = "File Path",
      default = default_path,
      description = "Define a directory to pull video frames from",
      subtype = 'DIR_PATH'
      )

# ------------------------------------------------------------------------
#    operators
# ------------------------------------------------------------------------

class HelloWorldOperator(bpy.types.Operator):
    bl_idname = "wm.hello_world"
    bl_label = "Generate"

    def execute(self, context):
        scene = context.scene
        mytool = scene.my_tool

        # Set rendering engine to Cycles
        bpy.context.scene.render.engine = "CYCLES"

        # List of objects representing video frames
        layers = []
        # Import images into scene to use as object textures
        for i in range(1, 421):
        	# Name of image file
        	name = str(i).zfill(4) + ".jpg"
        	# File path (relative to .blend file)
        	filepath = mytool.file_path + name
        	# Load image into scene
        	image = bpy.data.images.load(filepath, check_existing=True)
        	#bpy.data.images[name].name = str(i)

        	# Add objects and materials
        	size = image.size
        	# Add new cube to scene (one video frame)
        	bpy.ops.mesh.primitive_cube_add(location=(0, 0, i * (mytool.slice_thickness / 100 * 2)))
        	# Resize cube to be thinner
        	bpy.ops.transform.resize(value=(size[0] / 1e3 * mytool.slice_size, size[1] / 1e3 * mytool.slice_size, mytool.slice_thickness / 100))
        	# Selected object
        	ob = bpy.context.active_object
        	# Rename slice
        	ob.name = "Video Slice " + str(i)
        	# Add slice to list of layers
        	layers.append(ob)

        	# Check if material exists
        	mat = bpy.data.materials.get(str(i))
        	if mat is None:
        		# Create new material if none exists
        		mat = bpy.data.materials.new(name=str(i))
        	
        	# Set material to use node editor
        	mat.use_nodes = True;
        	# List of nodes in material node tree
        	nodes = mat.node_tree.nodes
        	# Remove all nodes from material
        	for node in nodes:
        		nodes.remove(node)
        		
        	# Add nodes
        	output = nodes.new("ShaderNodeOutputMaterial")
        	diff = nodes.new("ShaderNodeBsdfDiffuse")
        	texture = nodes.new("ShaderNodeTexImage")
        	coord = nodes.new("ShaderNodeTexCoord")
        	trans = nodes.new("ShaderNodeBsdfTransparent")
        	mix = nodes.new("ShaderNodeMixShader")
        	
        	# Set source image for texture
        	texture.image = bpy.data.images[str(i).zfill(4) + ".jpg"]
        	mix.inputs[0].default_value = 0
        	
        	# Create links between material nodes
        	mat.node_tree.links.new(texture.inputs["Vector"], coord.outputs["Generated"])
        	mat.node_tree.links.new(diff.inputs["Color"], texture.outputs["Color"])
        	mat.node_tree.links.new(mix.inputs[1], diff.outputs["BSDF"])
        	mat.node_tree.links.new(mix.inputs[2], trans.outputs["BSDF"])
        	mat.node_tree.links.new(output.inputs["Surface"], mix.outputs["Shader"])

        	# Assign material to object
        	if ob.data.materials:
        		ob.data.materials[0] = mat
        	else:
        		ob.data.materials.append(mat)

        # Select all slices
        for layer in layers:
        	layer.select = True
        # Combine layers
        bpy.ops.object.join()
        # Set origin to center of geometry
        bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY")
        # Set name of object
        bpy.context.object.name = "Video Cube"
        # Deselect
        bpy.ops.object.select_all(action="TOGGLE")

        return {'FINISHED'}

class BasicMenu(bpy.types.Menu):
    bl_idname = "OBJECT_MT_select_test"
    bl_label = "Select"

    def draw(self, context):
        layout = self.layout

class OBJECT_PT_my_panel(Panel):
    bl_idname = "OBJECT_PT_Video_Cube"
    bl_label = "Video Cube"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Create"
    bl_context = "objectmode"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool

        layout.prop(mytool, "max_slices")
        layout.prop(mytool, "slice_thickness")
        layout.prop(mytool, "slice_size")
        layout.prop(mytool, "file_path")
        layout.operator("wm.hello_world")

def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.my_tool = PointerProperty(type=VideoCubeSettings)

def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.my_tool

if __name__ == "__main__":
    register()