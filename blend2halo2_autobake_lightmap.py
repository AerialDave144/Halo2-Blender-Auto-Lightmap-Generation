# ##### BEGIN MIT LICENSE BLOCK #####
#
# MIT License
#
# Copyright (c) 2021 David Barnes
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# ##### END MIT LICENSE BLOCK #####


### Set directories to be used (needs to be added to UI eventually)
#   Location of directory to save baked image files:
save_directory = 'C:\\Program Files (x86)\\Microsoft Games\\Halo 2 Map Editor\\data\\scenarios\\multi\\BSP\\auto_baked'
#   Location of the bitmap_mapping.txt file generated by H2Codez when running the lightmap-dump command:
index_mapping_txt_path = 'C:\\Program Files (x86)\\Microsoft Games\Halo 2 Map Editor\\data\\scenarios\\multi\\BSP\\BSP.bitmap_mapping.txt'
#   Location of lightmap_truecolor_bitmaps tag located in the scenerio tag directory:
bitmap_tag_edit_path = 'C:\\Program Files (x86)\\Microsoft Games\\Halo 2 Map Editor\\tags\\scenarios\\multi\\BSP\\SCENARIO_BSP_lightmap_truecolor_bitmaps'

#   Location of H2Codez installation path:
h2tool_path = 'C:\\Program Files (x86)\\Microsoft Games\\Halo 2 Map Editor\\'

### Set Options (needs to be added to UI eventually)
#   Render resolution scale coefficient for unprocessed baked image:
bake_res_scale = 16.0
#   Render resolution scale coefficient for post processing baked image:
post_bake_res_scale = 0.0625
#   Enable or disable denosing in post processing:
use_denoise = True
#   Enable or disable auto execution of H2tool to edit bitmap tags:
run_h2codez_bitmap_edit = True
#   Apply gamma correction in post processing:
apply_gamma = 1.0
#   Apply view transform in post processing:
apply_view_transform = 'Filmic'
#   Apply contrast/look in post processing:
apply_look = 'Very High Contrast'
#   Appy exposure correction in post processing:
apply_exposure = -1.0


### Read information from bitmap_mapping.txt file (stored in name[name, index, width, height])

f=open(index_mapping_txt_path,"r")
lines=f.readlines()

obj_dict = {}

for line in lines:
    line_split = line.rstrip('\n').split('\t')
    obj_dict[line_split[0]] = line_split
f.close()

### Set scene render settings:

import bpy
scene = bpy.context.scene
if use_denoise is True:
    scene.render.image_settings.file_format = 'OPEN_EXR_MULTILAYER'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.image_settings.color_depth = '32'
    file_extension = '.exr'
    scene.view_settings.view_transform = 'Raw'
    scene.view_settings.look = 'None'
    scene.view_settings.gamma = 1.0
    scene.view_settings.exposure = 0
else:
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.image_settings.color_depth = '16'
    file_extension = '.png'
object_list = list(scene.objects)
bake_from_obj = bpy.context.view_layer.objects.active

#Some stuff that might be used later
#scene_collection = bpy.context.view_layer.layer_collection
#bpy.context.view_layer.active_layer_collection = scene_collection
#bpy.ops.object.mode_set(mode='OBJECT')
#print('\Configuring default bake settings to be used for all meshes...')
#bake_settings = bpy.types.BakeSettings
#bake_settings.use_pass_diffuse = True
#bake_settings.use_selected_to_active = True
#bake_settings.use_pass_direct = True
#bake_settings.use_pass_indirect = True
#bake_settings.use_pass_color = False

### Begin main bake steps:

print('Starting...\n')

#List to store all object names in specified collection:
name_list = []
bpy.ops.object.mode_set(mode = 'OBJECT')
bpy.ops.object.select_all(action='DESELECT')

#Hide all objects from render in specified collection:
for obj in bpy.data.collections['lightmap'].objects:
    obj.hide_render = True
    
#Iterate through all objects in specified collection:
for obj in bpy.data.collections['lightmap'].objects:
    print('\n\nCluster/Instance Object: ' + obj.name)
    try:
        res_x = float(obj_dict[obj.name][2]) * float(bake_res_scale)
        res_y = float(obj_dict[obj.name][3]) * float(bake_res_scale)
        
        print('Original Width: ' + str(obj_dict[obj.name][2]))
        print('Original Height: ' + str(obj_dict[obj.name][3]))
        
        print('Render Width: ' + str(int(res_x)))
        print('Render Height: ' + str(int(res_y)))
    except:
        #Need to replace this with something else
        res_x = 32
        res_y = 32
    bpy.ops.object.select_all(action='DESELECT')
    #Unhide object from render
    obj.hide_render = False
    
    bpy.context.view_layer.objects.active = obj
    uv1 = obj.data.uv_layers[1].name
    obj.data.uv_layers.active = obj.data.uv_layers[uv1]
    
    #Remove all materials from object
    for material in obj.material_slots:
        for i in range(len(obj.material_slots)):
            obj.active_material_index = i
            bpy.ops.object.material_slot_remove()
    print('All materials removed for ' + obj.name)
    
    #Set up material with node tree for texture baking:
    bpy.ops.object.material_slot_add()
    print('\nSetting up materials for ' + obj.name)
    try:
         mat = bpy.data.materials[obj.name]
         obj.data.materials[0] = mat
    except:
        mat = bpy.data.materials.new(name=obj.name)
        obj.data.materials[0] = mat
    mat.use_nodes = True

    uv_node = mat.node_tree.nodes.new('ShaderNodeUVMap')
    try:
        if bpy.data.images[obj.name] is not None:
            bpy.data.images.remove(bpy.data.images[obj.name])
    except:
        pass
    
    #Set up image to bake to
    if use_denoise is True:
        lightmap_image = bpy.data.images.new(obj.name, res_x, res_y, alpha=True, float_buffer=True, stereo3d=False, is_data=False, tiled=False)
        #lightmap_image.alpha_mode = 'PREMUL'
        #lightmap_image.is_float = True
        lightmap_image.colorspace_settings.name = 'Raw'
    else:
        lightmap_image = bpy.data.images.new(obj.name, res_x, res_y, alpha=True, float_buffer=False, stereo3d=False, is_data=False, tiled=False)
        #lightmap_image.alpha_mode = 'PREMUL'
        #lightmap_image.is_float = True
        lightmap_image.colorspace_settings.name = 'sRGB'
    if lightmap_image is None:
        lightmap_image = bpy.data.images.new(obj.name, res_x, res_y)
    for node in mat.node_tree.nodes:
        #print(node.type)
        if node.type == 'TEX_IMAGE':
            if node.image == lightmap_image:
                mat.node_tree.nodes.remove(node)
            mat.node_tree.nodes.remove(node)
        elif node.type == 'UVMAP':
            mat.node_tree.nodes.remove(node)
        #if node.type ==       
    uv_node = mat.node_tree.nodes.new('ShaderNodeUVMap')
    tex_node = mat.node_tree.nodes.new('ShaderNodeTexImage')
    tex_node.image = lightmap_image
    tex_node.select = True
    mat.node_tree.links.new(uv_node.outputs['UV'], tex_node.inputs['Vector'])

    uv_node.uv_map = uv1
    mat.node_tree.nodes.active = tex_node
    print('Materials set up for ' + obj.name)
    
    #Select object to bake from and set as active object:
    bake_from_obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    
    #Bake normal map if denoising is enabled:
    if use_denoise is True:
        print('\nBeginning normal texture bake for object ' + obj.name)
        bpy.ops.object.bake(type='NORMAL', save_mode='EXTERNAL')
        print('Normal texture baking complete for ' + obj.name + '!')
        print('\nSaving normal texture for ' + obj.name)
        normal_save_path = save_directory + '\\auto_baked_normal\\' + obj.name + file_extension
        lightmap_image.save_render(normal_save_path, scene = None)
        print('Image saved successfully to ' + normal_save_path)
        name_list.append(obj.name)
        
    #Bake diffuse map:
    print('\nBeginning diffuse texture bake for object ' + obj.name)
    bpy.ops.object.bake(type='DIFFUSE', save_mode='EXTERNAL')
    print('Diffuse texture baking complete for ' + obj.name + '!')
    print('\nSaving diffuse texture for ' + obj.name)
    color_save_path = save_directory + '\\auto_baked_color\\' + obj.name + file_extension
    lightmap_image.save_render(color_save_path, scene = None)
    print('Image saved successfully to ' + color_save_path)
    
    for node in mat.node_tree.nodes:
        if node.type == 'OUTPUT_MATERIAL':
            output_node = node
    mat.node_tree.links.new(tex_node.outputs['Color'], output_node.inputs['Surface'])
    
    #Hide object from render:
    obj.hide_render = True
    print('Finished baking all texture maps\n')

#Unhide all objects in specified collection from render:
for obj in bpy.data.collections['lightmap'].objects:
    obj.hide_render = False
bpy.context.view_layer.objects.active = bake_from_obj

####    Start post processing:
#Needs re-working for when denoising is disabled
#Needs ability to run without re-baking textures
if use_denoise is True:
    print('\nStarting Denoising...\n')
    origin_scene = bpy.context.scene
    denoise_scene = bpy.data.scenes.new(name='Denoise_Scene')
    bpy.context.window.scene = denoise_scene
    denoise_scene.render.image_settings.file_format = 'PNG'
    denoise_scene.render.image_settings.color_mode = 'RGBA'
    denoise_scene.render.image_settings.color_depth = '16'
    denoise_scene.view_settings.view_transform = apply_view_transform
    denoise_scene.view_settings.look = apply_look
    denoise_scene.view_settings.gamma = apply_gamma
    denoise_scene.view_settings.exposure = apply_exposure

    denoise_scene.use_nodes = True
    comp_tree = denoise_scene.node_tree
    for node in comp_tree.nodes:
        comp_tree.nodes.remove(node)
    
    
    color_image_node = comp_tree.nodes.new(type='CompositorNodeImage')

    normal_image_node = comp_tree.nodes.new(type='CompositorNodeImage')

    denoise_node = comp_tree.nodes.new(type='CompositorNodeDenoise')
    denoise_node.use_hdr = True
    
    scale_node = comp_tree.nodes.new(type='CompositorNodeTransform')
    scale_node.filter_type = 'BICUBIC'
    scale_node.inputs[4].default_value = float(post_bake_res_scale)
    
    composite_node = comp_tree.nodes.new(type='CompositorNodeComposite')

    comp_tree.links.new(color_image_node.outputs['Image'], denoise_node.inputs['Image'])
    comp_tree.links.new(normal_image_node.outputs['Image'], denoise_node.inputs['Normal'])
    comp_tree.links.new(denoise_node.outputs['Image'], scale_node.inputs['Image'])
    comp_tree.links.new(scale_node.outputs['Image'], composite_node.inputs['Image'])

    for obj_name in name_list:
        try:
            denoise_scene.render.resolution_x = float(obj_dict[obj_name][2]) * bake_res_scale * float(post_bake_res_scale)
            denoise_scene.render.resolution_y = float(obj_dict[obj_name][3]) * bake_res_scale * float(post_bake_res_scale)
        except:
            #need to re-work
            denoise_scene.render.resolution_x = 32
            denoise_scene.render.resolution_y = 32
        denoise_save_path =  save_directory + '\\denoised\\' + obj_name + '.png'
        
        color_image_path = save_directory + '\\' + 'auto_baked_color\\' + obj_name + file_extension
        color_image_node.image = bpy.data.images.load(color_image_path)
        color_image_node.image.use_half_precision = False

        normal_image_path = save_directory + '\\' + 'auto_baked_normal\\' + obj_name + file_extension
        normal_image_node.image = bpy.data.images.load(normal_image_path)
        normal_image_node.image.use_half_precision = False
        print('\nDenoising and compositing for ' + obj_name)
        bpy.ops.render.render()
        print('Saving denoised image under ' + denoise_save_path)
        bpy.data.images['Render Result'].save_render(denoise_save_path, scene = None)

    bpy.context.window.scene = origin_scene
    bpy.data.scenes.remove(denoise_scene) 
    
if use_denoise is True:
    print('Finished Denosing\n')

### Run H2Tool edit-bitmap command if enabled:
if run_h2codez_bitmap_edit is True:
    print('Running H2Tool...')
    from os import system

    def cmd_run(com):
        com_run_str = 'cmd /c '
        system(com_run_str + '"' + com + '"')

    def h2tool_run(com):
        print(h2tool_path)
        print(com)
        cmd_run('"' + h2tool_path + 'h2tool.exe" ' + com)

    if use_denoise is True:
        replacement_image_path = save_directory + '\\denoised\\'
    else:
        replacement_image_path = save_directory + '\\auto_baked_color\\'

    for name in name_list:
        try:
            h2tool_run('edit-bitmap' + ' ' +
            '"' + bitmap_tag_edit_path + '" ' +
            obj_dict[name][1] + ' ' +
            '"' + replacement_image_path +
            name +
            '.PNG' + '"')
        except:
            pass

print('\nFinished!')
