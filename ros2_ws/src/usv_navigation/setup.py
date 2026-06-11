from setuptools import setup

package_name = "usv_navigation"

setup(
    name=package_name,
    version="0.0.1",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="USV Team",
    maintainer_email="todo@example.com",
    description="Navigation logic for the USV.",
    license="MIT",
    entry_points={
        "console_scripts": [
            "navigation_node = usv_navigation.navigation_node:main",
        ],
    },
)
