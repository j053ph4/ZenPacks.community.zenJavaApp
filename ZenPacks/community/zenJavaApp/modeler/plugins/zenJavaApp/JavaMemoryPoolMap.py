from ZenPacks.community.zenJavaApp.lib.CommonMBeanMap import *
from ZenPacks.community.zenJavaApp.Definition import *

__doc__ = """JavaMemoryPoolMap

JavaMemoryPoolMap detects JVM Memory Pools on a per-JVM basis.

This version adds a relation to associated ipservice and javaapp components.

"""

class JavaMemoryPoolMap(CommonMBeanMap):
    """Map JMX Client output table to model."""
    
    constr = Construct(JavaMemoryPoolDefinition)
    relname = constr.relname
    modname = constr.zenpackComponentModule
    baseid = constr.baseid
    searchMBean = 'java.lang:type=MemoryPool,name=*'


