from ZenPacks.community.ConstructionKit.Construct import *
from ZenPacks.community.ConstructionKit.ZenPackConstruct import *
import Definition

init = Initializer(Definition)
for c in init.constructs: exec c.onCollectorInstalled()

class ZenPack(ZenPackConstruct):
    constructs = init.constructs
    packZProperties = init.props
    definitions = init.definitions

