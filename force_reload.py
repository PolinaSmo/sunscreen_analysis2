import sys
import os
import importlib

def force_reload():
    modules_to_reload = [
        'src.ui.roi_setter',
        'src.core.intensity_analyzer', 
        'src.data.exporter',
        'src.core.image_loader',
        'src.visualization.plotter'
    ]
    
    for module_name in modules_to_reload:
        if module_name in sys.modules:
            importlib.reload(sys.modules[module_name])
            print(f"Reloaded: {module_name}")

if __name__ == "__main__":
    force_reload()