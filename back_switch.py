import os
import platform
import ctypes
import subprocess
from PIL import Image

def get_fit_style(image_path, user_resolution):
    image = Image.open(image_path)
    image_width, image_height = image.size
    image.close()
    user_width, user_height = user_resolution

    image_aspect_ratio = image_width / image_height
    user_aspect_ratio = user_width / user_height

    if image_aspect_ratio == user_aspect_ratio:
        return 'fill'
    elif image_aspect_ratio > user_aspect_ratio:
        return 'fit' if (image_aspect_ratio / user_aspect_ratio) >= 2 else 'center'
    else:
        return 'span' if (user_aspect_ratio / image_aspect_ratio) >= 2 else 'fill'


def change_wallpaper(file_path, fit):
    system = platform.system()

    if system == "Windows":
        # Windows
        fit_styles = {
            'center': 0,
            'tile': 1,
            'stretch': 2,
            'fit': 6,
            'fill': 10
        }
        style = fit_styles.get(fit.lower(), 2)  # Default to 'stretch' if fit not found
        ctypes.windll.user32.SystemParametersInfoW(20, 0, file_path, style)


    elif system == "Darwin":
        #Mac does not support fit styles.
        script = 'tell application "System Events" to set picture of every desktop to "{}" as POSIX file'.format(file_path)
        subprocess.run(['osascript', '-e', script])

    elif system == "Linux":
        fit_styles = {
            'center': 'centered',
            'fill': 'centered',
            'fit': 'scaled',
            'stretch': 'stretched',
            'span': 'scaled'
        }
        style = fit_styles.get(fit.lower(), 'wallpaper')  # Default to 'wallpaper' if fit not found
        
        script = r'gsettings set org.gnome.desktop.background picture-uri "file:{}" '.format(file_path)
        os.system(script)
        script = r'gsettings set org.gnome.desktop.background picture-options "{}" '.format(style)
        os.system(script)
    else:
        print("Unsupported operating system: {}".format(system))
