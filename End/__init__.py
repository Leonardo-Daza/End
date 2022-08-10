# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "End",
    "author": "Leonardo Daza",
    "version": (1, 0),
    "blender": (3, 0, 1),
    "location": "File > Import-Export",
    "description": "Imports and Exports End3D and EndAnim files",
    "warning": "",
    "doc_url": "",
    "category": "Import-Export",
}

modulesNames = ['End_Importer', 'End_Exporter']

import sys
import importlib
 
modulesFullNames = {}
for currentModuleName in modulesNames:
    if 'DEBUG_MODE' in sys.argv:
        print('Using DEBUG_MODE')
        modulesFullNames[currentModuleName] = ('{}'.format(currentModuleName))
    else:
        print('Using RELEASE_MODE')
        modulesFullNames[currentModuleName] = ('{}.{}'.format(__name__, currentModuleName))
 
for currentModuleFullName in modulesFullNames.values():
    if currentModuleFullName in sys.modules:
        importlib.reload(sys.modules[currentModuleFullName])
    else:
        globals()[currentModuleFullName] = importlib.import_module(currentModuleFullName)
        setattr(globals()[currentModuleFullName], 'modulesNames', modulesFullNames)
 
def register():
    for currentModuleName in modulesFullNames.values():
        if currentModuleName in sys.modules:
            if hasattr(sys.modules[currentModuleName], 'register'):
                sys.modules[currentModuleName].register()
 
def unregister():
    for currentModuleName in modulesFullNames.values():
        if currentModuleName in sys.modules:
            if hasattr(sys.modules[currentModuleName], 'unregister'):
                sys.modules[currentModuleName].unregister()
    
import bpy
from bpy.props import (
        BoolProperty,
        FloatProperty,
        StringProperty,
        EnumProperty,
        )
from bpy_extras.io_utils import (
        ImportHelper,
        ExportHelper,
        path_reference_mode,
        axis_conversion,
        )
        
import os
End_Importer = sys.modules[modulesFullNames.get('End_Importer')]
End_Exporter = sys.modules[modulesFullNames.get('End_Exporter')]

class ImportEnd3D(bpy.types.Operator, ImportHelper):
    """Import a End3D file by selection"""
    bl_idname = "import_scene.end3d"
    bl_label = "Import End3D"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".End3D"
    filter_glob: StringProperty(
            default="*.End3D",
            options={'HIDDEN'},
            )
    
    def execute(self, context):
        filePath = self.filepath
        filePaths = filePath.split('/')
        fileName = str(filePaths[-1])
        filePath = filePath.replace(fileName, "")
        print("filePath = " + filePath)
        print("fileName = " + fileName)
        return End_Importer.import_End3D(filePath, fileName)
    
    def draw(self, context):
        pass

class ImportEndAnim(bpy.types.Operator, ImportHelper):
    """Import a EndAnim file by selection"""
    bl_idname = "import_scene.endanim"
    bl_label = "Import EndAnim"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".EndAnim"
    filter_glob: StringProperty(
            default="*.EndAnim",
            options={'HIDDEN'},
            )
    
    def execute(self, context):
        filePath = self.filepath
        filePaths = filePath.split('/')
        fileName = str(filePaths[-1])
        filePath = filePath.replace(fileName, "")
        print("filePath = " + filePath)
        print("fileName = " + fileName)
        return End_Importer.import_EndAnim(filePath, fileName)
    
    def draw(self, context):
        pass

class ExportEnd3D(bpy.types.Operator, ExportHelper):
    """Export a End3D File by selection"""

    bl_idname = "export_scene.end3d"
    bl_label = 'Export End3D'
    bl_options = {'PRESET'}

    filename_ext = ".End3D"
    filter_glob: StringProperty(
            default="*.End3D",
            options={'HIDDEN'},
            )
    
    def execute(self, context):
        filePath = self.filepath
        filePaths = filePath.split('/')
        fileName = str(filePaths[-1])
        filePath = filePath.replace(fileName, "")
        print("filePath = " + filePath)
        print("fileName = " + fileName)
        return End_Exporter.export_End3D(filePath, fileName)
    
    def draw(self, context):
        pass

class ExportEndAnim(bpy.types.Operator, ExportHelper):
    """Export a EndAnim File by selection"""

    bl_idname = "export_scene.endanim"
    bl_label = 'Export EndAnim'
    bl_options = {'PRESET'}

    filename_ext = ".EndAnim"
    filter_glob: StringProperty(
            default="*.EndAnim",
            options={'HIDDEN'},
            )
    
    def execute(self, context):
        filePath = self.filepath
        filePaths = filePath.split('/')
        fileName = str(filePaths[-1])
        filePath = filePath.replace(fileName, "")
        print("filePath = " + filePath)
        print("fileName = " + fileName)
        return End_Exporter.export_EndAnim(filePath, fileName)
    
    def draw(self, context):
        pass

def menu_func_import_end3D(self, context):
    self.layout.operator(ImportEnd3D.bl_idname, text="End3D (.End3D)")
def menu_func_import_endAnim(self, context):
    self.layout.operator(ImportEndAnim.bl_idname, text="EndAnim (.EndAnim)")

def menu_func_export_end3D(self, context):
    self.layout.operator(ExportEnd3D.bl_idname, text="End3D (.End3D)")
def menu_func_export_endAnim(self, context):
    self.layout.operator(ExportEndAnim.bl_idname, text="EndAnim (.EndAnim)")

classes = (
    ImportEnd3D,
    ImportEndAnim,
    ExportEnd3D,
    ExportEndAnim,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import_end3D)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import_endAnim)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export_end3D)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export_endAnim)

def unregister():
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import_end3D)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import_endAnim)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export_end3D)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export_endAnim)
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
