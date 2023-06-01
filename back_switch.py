import os
import platform
import ctypes
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
        # macOS
        fit_styles = {
            'center': '0',
            'fill': '3',
            'fit': '5',
            'stretch': '1',
            'span': '2'
        }
        style = fit_styles.get(fit.lower(), '5')  # Default to 'fit' if fit not found
        script = 'tell application "Finder" to set desktop picture to POSIX file "{}" as alias using {}'.format(file_path, style)
        os.system('osascript -e "{}"'.format(script))
    elif system == "Linux":
        # Linux (requires feh)
        fit_styles = {
            'center': '--bg-center',
            'fill': '--bg-fill',
            'fit': '--bg-scale',
            'stretch': '--bg-max',
            'span': '--bg-fill'
        }
        style = fit_styles.get(fit.lower(), '--bg-fill')  # Default to 'fill' if fit not found
        os.system('feh {} {}'.format(style, file_path))
    else:
        print("Unsupported operating system: {}".format(system))
