from cx_Freeze import setup, Executable
import sys

if sys.platform == "win32":
    base = "Win32GUI"

target = Executable(
    script="radmapper.py",
    base=base,
    #compress=False,
    #copyDependentFiles=True,
    #appendScriptToExe=True,
    #appendScriptToLibrary=False,
    icon="trefoil.ico"
    )

setup(
    name="Radmapper V1.5",
    options={"build_exe": {"packages":["pygame", "numpy", "matplotlib", "random", "time", "sys"],
                           "include_files":["font", "music", "plots", "textures", "trefoil.ico"]}},
    executables = [target]

    )