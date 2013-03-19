Developed by: Joseph Anderson
Description:

This zenpack allows a modified version of the standard JMX template to work
for multiple JVMs running on the same device.  Each JMX-capable application is
detected by a modeler plugin that checks responsive ports from a given list of
potential ports. 

Components:

The ZenPack has the following Objects

    JavaApp Template provides a component-level modified version of the
standard "Java" template that ships with zenJMX ZenPack.

The ZenPack also provides:

    A modeler plugin JavaAppMap that models available JMX-capable servers
    A new zProperty zJavaAppPorts that contains a list of port numbers to be
scanned by the modeler plugin
    A CLI-based jmx agent used by the modeling process

Installation:

Describe the install process if anything is needed before or after standard
ZenPack installation.

Requirements:

    Zenoss Versions Supported: 3.x, 4.x
    External Dependencies: None
    ZenPack Dependencies:
    Installation Notes: zopectl restart; zenhub restart after installing this
ZenPack.
    Configuration: zJavaAppPortRange needs to be populated with a range of ports to scan

History:

Change History:

    1.0 initial release
    1.1
        "javaAuth" attribute to determine authentication True or False
        made component attributes changable from the Details pane
        added CLI-based JMX client file missing from 1.0
        removed Device class "/Server/Linux/Java"
    1.2
        Revised modeler plugin and corrected issue when run from zenmodeler
    1.3
        Added support for monitor flag in component menu
        Added support for manual deletion of components
        Removed clear text display of password on Component Details pane
    1.4
        Using different python method to extract JMX output from cmdline utility
2.0
    added Zenoss 4.X support
    new dependency on "ConstructionKit" ZenPack to simplify current/future development
    <https://github.com/j053ph4/ZenPacks.community.ConstructionKit>
    modeler plugin uses nmap-based method to scan and profile ports within a given range.

Tested
======
This ZenPack was tested with versions 3.2.1, 4.2.3

Source:
https://github.com/j053ph4/ZenPacks.community.zenJavaApp

Known issues:  
