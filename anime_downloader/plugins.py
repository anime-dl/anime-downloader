import os, sys
from anime_downloader.config import APP_DIR

def plugins(PluginData):
	PluginFolderPath = os.path.join(APP_DIR, "plugins")

	PluginPath = list()
	Plugins = list()

	for root, directories, file in os.walk(PluginFolderPath):
		for file in file:
			if(file.endswith(".py")):
				Plugins.append(str(os.path.join(file.strip(".py"))))
				PluginPath.append(str(os.path.join(root,file)))

	import importlib
	import importlib.util

	#Plugins.pop(0)
	#sPluginPath.pop(0)

	for a, b in zip(PluginPath, Plugins):
		#print(a,b)
		spec = importlib.util.spec_from_file_location(b, a)
		module = importlib.util.module_from_spec(spec)
		sys.modules[spec.name] = module
		spec.loader.exec_module(module)
		importlib.import_module(b)
		print("\n")
		print("-----")
		print(f"Running Plugin {b} \n")
		module.plugin(PluginData)
		#print("\n")
		print("\nPlugin Finished")
		print("-----", "\n")
