import os
from distutils.core import setup
"""
NOTE: Borrowed from django's setup.py
"""
root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)
package_dir = 'django_google_adwords'

def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join)
    in a platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)

EXCLUDE_FROM_PACKAGES = []

def is_package(package_name):
    for pkg in EXCLUDE_FROM_PACKAGES:
        if package_name.startswith(pkg):
            return False
    return True

# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, package_data = [], {}

for dirpath, dirnames, filenames in os.walk(package_dir):
    # Ignore PEP 3147 cache dirs and those whose names start with '.'
    dirnames[:] = [d for d in dirnames if not d.startswith('.') and d != '__pycache__']
    parts = fullsplit(dirpath)
    package_name = '.'.join(parts)
    if '__init__.py' in filenames and is_package(package_name):
        packages.append(package_name)
    elif filenames:
        relative_path = []
        while '.'.join(parts) not in packages:
            relative_path.append(parts.pop())
        relative_path.reverse()
        path = os.path.join(*relative_path)
        package_files = package_data.setdefault('.'.join(parts), [])
        package_files.extend([os.path.join(path, f) for f in filenames])

setup(name="django-google-adwords",
    version="0.1.0",
    description=("A Django app that provides helpers for the Google Adwords API."),
    author="Alex Hayes",
    author_email="alex.hayes@roi.com.au",
    url="https://bitbucket.org/alexhayes/django-google-adwords",
    packages=packages,
    package_data=package_data
)
