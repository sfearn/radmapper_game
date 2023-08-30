from cx_Freeze import setup, Executable

target = Executable(
    script="radmapper_dev.py",
    base="Win32GUI",
    #compress=False,
    #copyDependentFiles=True,
    #appendScriptToExe=True,
    #appendScriptToLibrary=False,
    icon="trefoil.ico"
    )

setup(
    name="Radmapper V1.5",
    options={"build_exe": {"packages":["pygame", "numpy", "matplotlib", "random", "time", "sys"],
                           "include_files":["font", "music", "plots", "textures"]}},
    executables = [target]

    )