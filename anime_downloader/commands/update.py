import subprocess
command = """pip install --upgrade --force-reinstall git+git://github.com/vn-ki/anime-downloader.git --user"""
subprocess.run(command, shell=True)
exit()
