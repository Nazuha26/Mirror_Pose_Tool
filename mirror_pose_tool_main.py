import os
import json
import maya.cmds as cmds

def run():
    #Save function
    def save_settings():
        global text_fields
        settings = {
            'fields': {key: cmds.textField(field, query=True, text=True) for key, field in text_fields.items()},
            'layer_states': {
                'layer1': cmds.frameLayout('layer1_frame', query=True, collapse=True),
                'layer2': cmds.frameLayout('layer2_frame', query=True, collapse=True)
            }
        }
    
        maya_version = cmds.about(version=True)
        save_path = os.path.expanduser(f'~/Documents/maya/{maya_version}/scripts/Mirror_Pose_Tool/Saved/mirror_tool_save_settings.json')
    
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'w') as file:
            json.dump(settings, file, indent=4)

    #Load function
    def load_settings():
        global text_fields
    
        maya_version = cmds.about(version=True)
        load_path = os.path.expanduser(f'~/Documents/maya/{maya_version}/scripts/Mirror_Pose_Tool/Saved/mirror_tool_save_settings.json')
    
        if os.path.exists(load_path):
            with open(load_path, 'r') as file:
                settings = json.load(file)
    
                for key, value in settings.get('fields', {}).items():
                    if key in text_fields:
                        cmds.textField(text_fields[key], edit=True, text=value)
    
                layer_states = settings.get('layer_states', {})
                cmds.frameLayout('layer1_frame', edit=True, collapse=layer_states.get('layer1', True))
                cmds.frameLayout('layer2_frame', edit=True, collapse=layer_states.get('layer2', True))

    #Insert btn's function
    def insert_selected_object(field_names):
        selected_objects = cmds.ls(selection=True)
        if not selected_objects:
            cmds.warning("No objects selected.")
            return
    
        selected_object = selected_objects[0]
        for field_name in field_names:
            if not cmds.textField(text_fields[field_name], query=True, text=True):
                cmds.textField(text_fields[field_name], edit=True, text=selected_object)
                break

    #UI function
    def create_custom_ui():
        global text_fields
        text_fields = {}

        if cmds.window("customUI", exists=True):
            cmds.deleteUI("customUI")

        window = cmds.window("customUI", title="Mirror pose tool", width=350, height=500, closeCommand=save_settings, sizeable=False)  # Adjusted height for additional fields
        #Edge offset
        window = cmds.frameLayout(labelVisible=False, marginWidth=10, marginHeight=10)
        #Scroll bar
        scroll_layout = cmds.scrollLayout(horizontalScrollBarThickness=0, verticalScrollBarThickness=16)

        main_layout = cmds.columnLayout(adjustableColumn=True, parent=scroll_layout)

        #Left - Right objects layer
        layer1_frame = cmds.frameLayout('layer1_frame', label="Left - Right objects", collapsable=True, parent=main_layout)
        layer1_layout = cmds.rowLayout(numberOfColumns=2, parent=layer1_frame)

        #Left objects
        cmds.columnLayout(adjustableColumn=True, parent=layer1_layout)
        cmds.text(label='Left objects')
        for i in range(1, 21):  #Create 20 fields
            field_name = f'input_field_{i}'
            text_fields[field_name] = cmds.textField(width=150, height=25)
        cmds.button(label='Insert', height=30, command=lambda x: insert_selected_object([f'input_field_{i}' for i in range(1, 21)]))
        cmds.setParent('..')

        #Right objects
        cmds.columnLayout(adjustableColumn=True, parent=layer1_layout)
        cmds.text(label='Right objects')
        for i in range(21, 41):  #Create 20 fields
            field_name = f'input_field_{i}'
            text_fields[field_name] = cmds.textField(width=150, height=25)
        cmds.button(label='Insert', height=30, command=lambda x: insert_selected_object([f'input_field_{i}' for i in range(21, 41)]))
        cmds.setParent('..')

        cmds.setParent(main_layout)
        
        cmds.separator(height=10, style='none', parent=main_layout)

        #Central objects layer
        layer2_frame = cmds.frameLayout('layer2_frame', label="Central objects", collapsable=True, parent=main_layout)
        cmds.columnLayout(adjustableColumn=True, parent=layer2_frame)
        cmds.text(label='Central objects')
        for i in range(41, 61):  #Create 20 fields
            field_name = f'input_field_{i}'
            text_fields[field_name] = cmds.textField(width=150, height=25)
        cmds.button(label='Insert', height=30, command=lambda x: insert_selected_object([f'input_field_{i}' for i in range(41, 61)]))
        cmds.setParent('..')
    
        #Separator
        cmds.separator(height=10, style='none', parent=main_layout)
    
        #Mirror Button
        cmds.button(label="Mirror", height=40, command=lambda x: mirror_attributes(), backgroundColor=[1, 1, 0], parent=main_layout)
    
        load_settings()
    
        cmds.showWindow("customUI")
    
    #Central obj mirror function
    def negate_attributes():
        for i in range(41, 61):  #From 41 to 61
            field_name = f'input_field_{i}'
            obj = cmds.textField(text_fields[field_name], query=True, text=True)

            if not cmds.objExists(obj):
                continue

            #Translation and rotation only for Y and Z axes
            for attr in ['translate', 'rotate']:
                current_values = cmds.getAttr(f"{obj}.{attr}")[0]
                negated_values = [current_values[0], -current_values[1], -current_values[2]]
                cmds.setAttr(f"{obj}.{attr}", *negated_values, type="double3")

    #Left-right obj mirror function
    def mirror_attributes():
        negate_attributes()
        pairs = []
        for i in range(1, 21):  #From 1 to 21
            pairs.append((f"input_field_{i}", f"input_field_{i+20}"))

        for source_field_name, target_field_name in pairs:
            source_obj = cmds.textField(text_fields[source_field_name], query=True, text=True)
            target_obj = cmds.textField(text_fields[target_field_name], query=True, text=True)

            if not cmds.objExists(source_obj) or not cmds.objExists(target_obj):
                continue

            # Store original translation and rotation values for both objects
            original_source_values = {}
            original_target_values = {}
            for attr in ['translate', 'rotate']:
                original_source_values[attr] = cmds.getAttr(f"{source_obj}.{attr}")[0]
                original_target_values[attr] = cmds.getAttr(f"{target_obj}.{attr}")[0]

            # Swap attributes between source and target
            for attr in ['translate', 'rotate']:
                source_values = [round(v, 4) for v in original_source_values[attr]]
                target_values = [round(v, 4) for v in original_target_values[attr]]

                cmds.setAttr(f"{source_obj}.{attr}", *target_values, type="double3")
                cmds.setAttr(f"{target_obj}.{attr}", *source_values, type="double3")
    
    create_custom_ui()