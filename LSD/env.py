import sdl2

class SDL2Environment(object):

	def __init__(self, window, resolution, renderer, texture_factory, surface_factory, lsd_version):
		self.window = window
		self.resolution = resolution
		self.renderer = renderer
		self.texture_factory = texture_factory
		self.surface_factory = surface_factory
		self.active_framebuffers = []
		self.lsd_version = lsd_version

		# Get the rest of the info by quering SDL2 itself
		# Only for screen 1 for now
		self.pysdl2_version = sdl2.__version__
		self.sdl2_version = "{}.{}.{}".format(sdl2.version.SDL_MAJOR_VERSION, 
			sdl2.version.SDL_MINOR_VERSION, sdl2.version.SDL_PATCHLEVEL)

		self.cpu_count = sdl2.SDL_GetCPUCount()
		self.display_count = sdl2.SDL_GetNumVideoDisplays()

		self.displays = []
		for dispnum in range(self.display_count):
			dispinfo = sdl2.SDL_DisplayMode()
			res = sdl2.SDL_GetCurrentDisplayMode(dispnum, dispinfo)
			if res == 0:
				self.displays.append(dispinfo)

		self.display_drivers = [sdl2.video.SDL_GetVideoDriver(i) for i in \
			range(sdl2.video.SDL_GetNumVideoDrivers())]
		self.current_display_driver = sdl2.SDL_GetCurrentVideoDriver()

	def __str__(self):
		infostring = (""
		"SDL2 environment information\n"
		"\n"
		"General:\n"
		"	LSD version {}\n".format(self.lsd_version) +
		"	PySDL2 version: {}\n".format(self.pysdl2_version) +
		"	SDL2 version: {}\n".format(self.sdl2_version) +
		"	CPU count: {}\n".format(self.cpu_count) +
		"\n"
		"Displays:\n"
		"	Available display drivers: {}\n".format(self.display_drivers) +
		"	Current display driver: {}\n".format(self.current_display_driver) +
		"	Number of displays detected: {}\n\n".format(self.display_count))

		for dispnum, display in enumerate(self.displays):
			infostring += (""
			"	Display {}:\n".format(dispnum) +
			"		Resolution: ({},{})\n".format(display.w, display.h) +
			"		Refresh rate: {} fps\n\n".format(display.refresh_rate))
		
		return infostring

	def __repr__(self):
		return self.__str__()

	def info(self):
		info = {
			"LSD version":self.lsd_version,
			"PySDL2 version":self.pysdl2_version,
			"SDL2 version":self.sdl2_version,
			"CPU count":self.cpu_count,
			"Current display driver":self.current_display_driver,
			"Display count":self.display_count,
			"Window dimensions":self.window.size,
			"Available display drivers":self.display_drivers,
		}

		for dispnum, display in enumerate(self.displays):
			cur_disp_info = {}
			cur_disp_info["Resolution"] = (display.w, display.h)
			cur_disp_info["Refresh rate"] = display.refresh_rate
			info["Display {}".format(dispnum)] = cur_disp_info

		return info

	def get_available_display_drivers(self):
		drivers = []
		for vd in range(sdl2.SDL_GetNumVideoDrivers()):
			drivers.append(sdl2.SDL_GetVideoDriver(vd))
		return drivers