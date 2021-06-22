import bpy
import os
#from bpy import context -- Standalone testing only

bl_info = {
 "name": "Batch Export Tool",
 "description": "Tools to batch export fbx files",
 "author": "Patrick Jezek",
 "blender": (2, 9, 0),
 "version": (1, 1, 0),
 "category": "Batch Export",
 "location": "",
 "warning": "",
 "wiki_url": "",
 "tracker_url": "",
}


class UnityBatchExportPanel(bpy.types.Panel):

    bl_idname = "PEA_Batch_Export_tools"
    bl_label = "Batch Export Tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = "objectmode"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):

        layout = self.layout

        # current selection export
        col = layout.column(align=True)
        col.label(text="Batch export:")
        col.prop(context.scene, 'pea_batch_export_path')
        col.prop(context.scene, 'pea_global_scale')
        col.prop(context.scene, 'pea_bake_space_transform')
        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("pea.batch_export_selection", text="Batch Export Selection", icon='EXPORT')			
        
        # reset scale
        col = layout.column(align=True)
        col.label(text="Unity Units Setup:")
        col.label(text="[1 Blender = 1 Unity]")
        row = col.row(align=True)
        row.operator("pea.blender_units", text="Blender Units", icon='BLENDER')

        # smooth object
        col = layout.column(align=True)
        col.label(text="Shade Smooth object or edge, face, vertex:")
        row = col.row(align=True)
        row.operator("pea.select_vertex", text="Vertex", icon='VERTEXSEL')
        row.operator("pea.select_edge", text="Edge", icon='EDGESEL')
        row.operator("pea.select_face", text="Face", icon='FACESEL')
        row = col.row(align=True)
        row.operator("pea.smooth_selection", text="Shade Smooth [Ctrl F]", icon='MOD_SUBSURF')

        # tools
        col = layout.column(align=True)
        col.label(text="Tools:")
        row = col.row(align=True)
        row.operator("object.join", text="Join [Ctrl J]", icon='AUTOMERGE_OFF')
        row.operator("mesh.separate", text="Seperate [P]", icon='UV_ISLANDSEL')
        row.operator("object.duplicate_move", text="Duplicate [Shift+D]", icon='ROTATECOLLECTION')

        # selection tools
        col = layout.column(align=True)
        col.label(text="Selection Tools:")
        row = col.row(align=True)
        row.operator("pea.invert_selection", text=" Invert All [Ctrl I]", icon="ALIGN")
        row.operator("pea.select_all", text=" All Select [A]", icon="STICKY_UVS_LOC")
        row.operator("view3d.select_border", text=" Border    Select", icon="VIEW3D_VEC")
        row.operator("view3d.select_circle", text=" Circle Select", icon="ALIASED")
        row.operator("object.select_pattern", text=" Pattern...Search Select", icon="SEQ_LUMA_WAVEFORM")

        # pivot tools
        col = layout.column(align=True)
        col.label(text="Origin to Center of Grid [Select Vertex]:")
        row = col.row(align=True)
        row.operator("pea.origin_vertex", text="O-V-CoG Origin to Vertex Center of Grid", icon='VERTEXSEL')
        row.operator("pea.origin_com", text="O-CoM-CoG Origin to Center of Mass-Center of Grid", icon='FORCE_FORCE')

        # Freeze
        col = layout.column(align=True)
        col.label(text="Freeze Transformation of object: [Ctrl+A]")
        row = col.row(align=True)
        row.operator("pea.freeze_loc", text="Freeze Location", icon='FILE_REFRESH')
        row.operator("pea.freeze_rot_scale", text="Freeze Rotation+Scale", icon='FILE_REFRESH')


class PeaBatchExportSelection(bpy.types.Operator):
    bl_idname = "pea.batch_export_selection"
    bl_label = "Choose Directory"

    def execute(self, context):
        print ("execute Pea_batch_export")

        basedir = os.path.dirname(bpy.data.filepath)
        if not basedir:
            raise Exception("Blend file is not saved")

        if context.scene.pea_batch_export_path == "":
            raise Exception("Export path not set")

        # preserve current selection
        orig_selection = bpy.context.selected_objects       

        # convert path to windows friendly notation
        dir = os.path.dirname(bpy.path.abspath(context.scene.pea_batch_export_path))
        # cursor to origin
        bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)     
        
        for obj in orig_selection:
        
            # don't process if has parent
            if obj.parent != None:
               continue
        
            # select only current object
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)

            # process children
            for obj2 in orig_selection:
                if obj != obj2 and obj2.parent == obj:
                   obj2.select_set(True)
                   print("Adding child: " + obj2.name);
            
            # use mesh name for file name
            name = bpy.path.clean_name(obj.name)
            fn = os.path.join(dir, name)
            print("exporting: " + fn)
            # export fbx
            # have to set global_scale to 0.01 so unity sets the "File Scale" in the importer to 1 
            # bake_space_transform is experimental
            bpy.ops.export_scene.fbx(filepath=fn + ".fbx", use_selection=True, global_scale=context.scene.pea_global_scale,bake_space_transform=context.scene.pea_bake_space_transform, axis_forward='-Z', axis_up='Y')
        
        # restore original selection
        bpy.ops.object.select_all(action='DESELECT')
        for obj in orig_selection:
            obj.select_set(True)
        
        return {'FINISHED'}     

class PeaBlenderUnits(bpy.types.Operator):
    bl_idname = "pea.blender_units"
    bl_label = "Minimal Operator"

    def execute(self, context):
        bpy.context.scene.unit_settings.system = 'NONE'
        bpy.context.scene.unit_settings.scale_length = 1    # 1
        bpy.context.space_data.clip_start = 1               # 0.1
        bpy.context.space_data.clip_end = 500               # 1000
        bpy.context.space_data.grid_lines = 16              # 16
        return {'FINISHED'}


class PeaVertexSelect(bpy.types.Operator):
    bl_idname = "pea.select_vertex"
    bl_label = "Minimal Operator"

    def execute(self, context):
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_mode(type='VERT')
        bpy.ops.object.mode_set(mode='OBJECT')
        return {'FINISHED'}


class PeaEdgeSelect(bpy.types.Operator):
    bl_idname = "pea.select_edge"
    bl_label = "Minimal Operator"

    def execute(self, context):
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_mode(type='EDGE')
        bpy.ops.object.mode_set(mode='OBJECT')
        return {'FINISHED'}


class PeaFaceSelect(bpy.types.Operator):
    bl_idname = "pea.select_face"
    bl_label = "Minimal Operator"

    def execute(self, context):
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_mode(type='FACE')
        bpy.ops.object.mode_set(mode='OBJECT')
        return {'FINISHED'}


class PeaSmoothSelection(bpy.types.Operator):
    bl_idname="pea.smooth_selection"
    bl_label="Minimal Operator"

    def execute(self, context):
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.faces_shade_smooth()
        bpy.ops.object.mode_set(mode='OBJECT')
        return{'FINISHED'}


class PeaInvertSelection(bpy.types.Operator):
    bl_idname = "pea.invert_selection"
    bl_label = "Minimal Operator"

    def execute(self, context):
        if bpy.context.mode.startswith("EDIT"):
            bpy.ops.mesh.select_all(action='INVERT')
        else:
            bpy.ops.object.select_all(action='INVERT')
        return {'FINISHED'}


class PeaSelectAll(bpy.types.Operator):
    bl_idname = "pea.select_all"
    bl_label = "Minimal Operator"

    def execute(self, context):
        if bpy.context.mode.startswith("EDIT"):
            bpy.ops.mesh.select_all(action='TOGGLE')
        else:
            bpy.ops.object.select_all(action='TOGGLE')
        return {'FINISHED'}


class PeaOriginVertex(bpy.types.Operator):
    bl_idname = "pea.origin_vertex"
    bl_label = "Minimal Operator"

    def execute(self, context):
        bpy.ops.view3d.snap_cursor_to_selected()
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        bpy.context.object.location[0] = 0
        bpy.context.object.location[1] = 0
        bpy.context.object.location[2] = 0
        return{'FINISHED'}


class PeaOriginCom(bpy.types.Operator):
    bl_idname = "pea.origin_com"
    bl_label = "Minimal Operator"

    def execute(self, context):
        bpy.ops.view3d.snap_cursor_to_selected()
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        bpy.context.object.location[0] = 0
        bpy.context.object.location[1] = 0
        bpy.context.object.location[2] = 0
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS')
        bpy.context.object.location[0] = 0
        bpy.context.object.location[1] = 0
        bpy.ops.view3d.snap_cursor_to_center()
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        return{'FINISHED'}


class PeaFreezeLoc(bpy.types.Operator):
    bl_idname = "pea.freeze_loc"
    bl_label = "Minimal Operator"

    def execute(self, context):
        bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
        return {'FINISHED'}


class PeaFreezeRotScale(bpy.types.Operator):
    bl_idname = "pea.freeze_rot_scale"
    bl_label = "Minimal Operator"

    def execute(self, context):
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        return {'FINISHED'}


# registers
def register():
    bpy.types.Scene.pea_batch_export_path = bpy.props.StringProperty (
        name="Export Path",
        default="",
        description="Define the path where to export",
        subtype='DIR_PATH'
    )
    
    bpy.types.Scene.pea_bake_space_transform = bpy.props.BoolProperty (
        name="Bake Space Transform",
        description="This will apply correct scale and rotation to the object.",
        default=True
    )
    
    bpy.types.Scene.pea_global_scale = bpy.props.FloatProperty(
        name="Global Scale",
        description="Global scale to use during export",
        default=1
    )
    
    bpy.utils.register_class(UnityBatchExportPanel)
    #bpy.utils.register_class(PeaBatchExport)
    bpy.utils.register_class(PeaBatchExportSelection)
    bpy.utils.register_class(PeaBlenderUnits)
    bpy.utils.register_class(PeaVertexSelect)
    bpy.utils.register_class(PeaEdgeSelect)
    bpy.utils.register_class(PeaFaceSelect)
    bpy.utils.register_class(PeaSmoothSelection)
    bpy.utils.register_class(PeaInvertSelection)
    bpy.utils.register_class(PeaSelectAll)
    bpy.utils.register_class(PeaOriginVertex)
    bpy.utils.register_class(PeaOriginCom)
    bpy.utils.register_class(PeaFreezeLoc)
    bpy.utils.register_class(PeaFreezeRotScale)


def unregister():
    del bpy.types.Scene.pea_batch_export_path
    del bpy.types.Scene.pea_bake_space_transform
    bpy.utils.unregister_class(UnityBatchExportPanel)
    #bpy.utils.unregister_class(PeaBatchExport)
    bpy.utils.register_class(PeaBatchExportSelection)
    bpy.utils.unregister_class(PeaBlenderUnits)
    bpy.utils.unregister_class(PeaVertexSelect)
    bpy.utils.unregister_class(PeaEdgeSelect)
    bpy.utils.unregister_class(PeaFaceSelect)
    bpy.utils.unregister_class(PeaSmoothSelection)
    bpy.utils.unregister_class(PeaInvertSelection)
    bpy.utils.unregister_class(PeaSelectAll)
    bpy.utils.unregister_class(PeaOriginVertex)
    bpy.utils.unregister_class(PeaOriginCom)
    bpy.utils.unregister_class(PeaFreezeLoc)
    bpy.utils.unregister_class(PeaFreezeRotScale)

if __name__ == "__main__":
    register()
