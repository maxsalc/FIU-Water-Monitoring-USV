import os 
from glob import glob
from setuptools import setup

package_name = "usv_sensor_bridge"

setup(
    name=package_name,
    version="0.0.1",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        (os.path.join("share", package_name, "config"), glob("config/*.yaml")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="USV Team",
    maintainer_email="todo@example.com",
    description="Placeholder sensor bridge for USV water monitoring sensors.",
    license="MIT",
    entry_points={
        "console_scripts": [
                    "fake_sensor_node = usv_sensor_bridge.fake_sensor_node:main",

        ],
    },
)
