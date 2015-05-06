# LSD
Layer on top of PySDL2 to interace with SDL2 in a more 'object oriented' or 'pythonic' way, while maintaining its flexibility. The module has been written in Python 2 but should be Python 3 ready. Documentation and API descriptions will follow when the module has matured a bit more.
For now, the test files in the main folder give the best example of how this module can be used.

## Installation
A setup.py will soon follow. To use LSD, you need to have installed both the pysdl2 module and the SDL2 libraries 

### PySDL2
Installing pysdl2 is the same for every OS. Simply use pip!:

    pip install pysdl2

You can do this even before you have installed the SDL2 libraries themselves.

### SDL2
#### Linux (Ubuntu)
In linux it's very easy to compile all SDL2 libraries yourself, but if you are using Ubuntu or one of its varieties, it's of course even easier to use the repositories

    sudo apt-get install libsdl2-2.0-0 libsdl2-gfx-1.0-0 libsdl2-ttf-2.0-0 libsdl2-image-2.0-0 libsdl2-mixer-2.0-0 libsdl2-net-2.0-0

#### OS X
The easiest way is to use Homebrew

    brew update
    brew install sdl2 sdl2_gfx sdl2_ttf sdl2_mixer sdl2_net sdl2_image
    
#### Windows
As often, Windows is the problem child a bit. It is a bit more troublesome to get SDL2 work, but once you get that far, it works really well! You need to get the SDL2 DLL files from the appropriate sites and place them in a folder on your system.
Then you will need to create and environment variable called "PYSDL2_DLL_PATH" that points to this folder. I plan on including the relevant SDL2 DLL's with future releases of this module.
