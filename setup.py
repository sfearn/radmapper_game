import cx_Freeze

executables = [cx_Freeze.Executable("radmapper_dev.py")]

cx_Freeze.setup(
    name="Radmapper V1.4",
    options={"build_exe": {"packages":["pygame", "numpy", "matplotlib", "random", "time", "sys"],
                           "include_files":["font/PixeloidMono-d94EV.ttf", "music/adventure.mp3",
                                            "music/menu.mp3", "music/platforming.mp3"]}},
    executables = executables

    )