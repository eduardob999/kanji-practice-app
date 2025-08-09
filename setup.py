from setuptools import setup, find_packages
from setuptools.command.install import install
import os
import re
import shutil


class PostInstallCommand(install):
    """
    Custom install command to copy bundled public assets to ~/Public/PracticeJapanese
    so the app can use user-writable/shared location after installation.
    """

    def run(self):
        # Perform standard installation first
        super().run()

        try:
            home_dir = os.path.expanduser("~")
            public_dir = os.path.join(home_dir, "public")
            target_dir = os.path.join(public_dir, "practiceJapanese")

            source_dir = os.path.join(os.path.dirname(__file__), "practicejapanese", "public")

            # Ensure destination exists
            os.makedirs(target_dir, exist_ok=True)

            if os.path.isdir(source_dir):
                for name in os.listdir(source_dir):
                    src_path = os.path.join(source_dir, name)
                    if os.path.isfile(src_path):
                        dst_path = os.path.join(target_dir, name)
                        try:
                            shutil.copy2(src_path, dst_path)
                        except Exception:
                            # Best-effort copy; continue with others
                            pass
        except Exception:
            # Never fail installation due to copy issues
            pass

def read_version(): 
    init_path = os.path.join(os.path.dirname(__file__), "practicejapanese", "__init__.py")
    with open(init_path, "r") as f:
        content = f.read()
    match = re.search(r'__version__\s*=\s*[\'"]([^\'"]+)[\'"]', content)
    return match.group(1) if match else "0.0.0"

def read_requirements():
    req_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    with open(req_path, "r") as f:
        lines = f.readlines()
    return [line.strip() for line in lines if line.strip() and not line.startswith('#')]

setup(
    name="pjapp",
    version=read_version(),
    packages=find_packages(),
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "pjapp=practicejapanese.main:main"
        ]
    },
    include_package_data=True,
    cmdclass={
        'install': PostInstallCommand,
    }
)