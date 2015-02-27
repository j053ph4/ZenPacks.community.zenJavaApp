from ZenPacks.community.zenJavaApp.lib.CommonMBeanMap import *
from ZenPacks.community.zenJavaApp.Definition import *

__doc__ = """JavaGarbageCollectorMap

JavaGarbageCollectorMap detects JVM Garbage Collectors on a per-JVM basis.

This version adds a relation to associated ipservice and javaapp components.

"""

class JavaGarbageCollectorMap(CommonMBeanMap):
    """Map JMX Client output table to model."""
    
    constr = Construct(JavaGarbageCollectorDefinition)
    relname = constr.relname
    modname = constr.zenpackComponentModule
    baseid = constr.baseid
    
    searchMBean = 'java.lang:type=GarbageCollector,name=*'

