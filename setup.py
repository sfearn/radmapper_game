from cx_Freeze import setup, Executable
import sys

if sys.platform == "win32":
    base = "Win32GUI"

sys.setrecursionlimit(5000)

target = Executable(
    script="radmapper.py",
    base=base,
    icon="trefoil.ico"
    )

setup(
    name="Radmapper V1.6",
    options={"build_exe": {"packages":["pygame", "numpy", "matplotlib", "random", "time", "sys"],
                           "include_files":["font", "music", "plots", "textures"]}},
    executables = [target]

    )