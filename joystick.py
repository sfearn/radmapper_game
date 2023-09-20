import pygame

pygame.init()

j = pygame.joystick.Joystick(0)
j.init()

try:
    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.JOYBUTTONDOWN:
                print("Button Pressed")
                print(event.button)
            elif event.type == pygame.JOYBUTTONUP:
                print("Button Released")
            elif event.type == pygame.JOYAXISMOTION:
                print("Axis Moved")
                print(event.axis)
                print(event.value)
            elif event.type == pygame.JOYHATMOTION:
                print("Hat Moved")
                print(event.hat)
                print(event.value)

except KeyboardInterrupt:
    print("EXITING NOW")
    j.quit()