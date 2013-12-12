import os
import sublime
import sys
import threading


if os.name == 'nt':
    from ctypes import windll, create_unicode_buffer


class Prefs:
    @staticmethod
    def load():
        settings = sublime.load_settings('PHPIDE.sublime-settings')
        Prefs.plugins = settings.get('plugins', [])
        Prefs.debug = settings.get('debug', 0)

Prefs.load()


def add_to_path(path):
    # Python 2.x on Windows can't properly import from non-ASCII paths, so
    # this code added the DOC 8.3 version of the lib folder to the path in
    # case the user's username includes non-ASCII characters
    if os.name == 'nt':
        buf = create_unicode_buffer(512)
        if windll.kernel32.GetShortPathNameW(path, buf, len(buf)):
            path = buf.value

    if path not in sys.path:
        sys.path.append(path)

# pull Package Control's files into our path
pc_folder = os.path.join(sublime.packages_path(), 'Package Control')
add_to_path(pc_folder)

# now we can load the Package Control code
os.chdir(pc_folder)
from package_control.package_manager import PackageManager

class PHPIDE(threading.Thread):
    def __init__(self):
        self.manager = PackageManager()
        threading.Thread.__init__(self)

    def run(self):
        installed_packages = self.manager.list_packages()
        for plugin in Prefs.plugins:
            print "- checking plugin " + plugin
            if not plugin in installed_packages:
                self.manager.install_package(plugin)


sublime.set_timeout(lambda: PHPIDE().start(), 3000)
