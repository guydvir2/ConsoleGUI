from sys import platform
from sys import path

os_type = platform
if os_type == 'darwin':
    main_path = '/Users/guy/Documents/github/Rpi/'
elif os_type == 'win32':
    main_path = 'd:/users/guydvir/Documents/git/Rpi/'
elif os_type == 'linux':
    main_path = '/home/guy/Documents/github/Rpi/'


path.append(main_path + 'GPIO_Projects/lcd')
path.append(main_path + 'SmartHome')
path.append(main_path + 'modules')
