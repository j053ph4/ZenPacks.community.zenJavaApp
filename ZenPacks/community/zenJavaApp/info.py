from ZenPacks.community.ConstructionKit.ClassHelper import *

def JavaGarbageCollectorgetEventClassesVocabulary(context):
    return SimpleVocabulary.fromValues(context.listgetEventClasses())

class JavaGarbageCollectorInfo(ClassHelper.JavaGarbageCollectorInfo):
    ''''''

def JavaAppgetEventClassesVocabulary(context):
    return SimpleVocabulary.fromValues(context.listgetEventClasses())

class JavaAppInfo(ClassHelper.JavaAppInfo):
    ''''''

def JavaMemoryPoolgetEventClassesVocabulary(context):
    return SimpleVocabulary.fromValues(context.listgetEventClasses())

class JavaMemoryPoolInfo(ClassHelper.JavaMemoryPoolInfo):
    ''''''


