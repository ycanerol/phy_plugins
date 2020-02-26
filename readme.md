# How to use the plugins?

- Clone the repository

- Add the path to the location to ~/.phy/phy_config.py
  ```pyhton
  c.Plugins.dirs = [r'/home/ycan/.phy/plugins', r'/home/ycan/repos/phy_plugins']
  ```
- To activate each plugin, add its name to the plugin list in the same file
  ```python
  c.TemplateGUI.plugins = ['MEAColumns', <more plugins here>]
  ```
  When you pull from the repository, you need to repeat this step to activate
  the new plugins.

- Relaunch phy


### Notes
- You should remove duplicate plugins in the ~/.phy/plugins folder, otherwise the
  loading might go wrong.
- Some plugins might require additional packages to be installed, check the import
  statements if you're unable to run a plugin.
- To get more verbose output, phy can be ran with the debug option.
  ```python
  phy template-gui --debug params.py
  ```
