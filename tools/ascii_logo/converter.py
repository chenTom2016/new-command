import ascii_magic
from colorama import Fore, Style
import os

def image_to_ascii_color(path, columns=80):
   
    try:
        art = ascii_magic.from_image_file(path, columns=columns, mode=ascii_magic.Modes.COLOR)
        ascii_magic.to_terminal(art)
    except Exception as e:
        print(Fore.RED + f"Unable to display image: {e}" + Style.RESET_ALL)

def save_ascii_logo_color(path, output_path="ascii_logo_color.txt", columns=80):
    """
    Generate color ASCII LOGO and save it as ANSI color text file.
    """
    try:
        art = ascii_magic.from_image_file(path, columns=columns, mode=ascii_magic.Modes.COLOR)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(ascii_magic.to_string(art))
        print(Fore.CYAN + f"Color ASCII LOGO has been saved to {output_path}" + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"Build Failure: {e}" + Style.RESET_ALL)
