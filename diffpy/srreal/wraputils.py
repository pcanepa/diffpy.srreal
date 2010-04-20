##############################################################################
#
# diffpy.srreal     by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2010 Trustees of the Columbia University
#                   in the City of New York.  All rights reserved.
#
# File coded by:    Pavol Juhas
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################


"""Local utilities helpful for tweaking interfaces to boost python classes.
"""

# module version
__id__ = "$Id$"


# Routines -------------------------------------------------------------------

def propertyFromExtDoubleAttr(attrname, doc):
    '''Create property wrapper to a DoubleAttr in C++ extension object.

    attrname -- string name of the double attribute
    doc      -- docstring for the Python class property

    Return a property object.
    '''
    def fget(self):
        return self._getDoubleAttr(attrname)
    def fset(self, value):
        self._setDoubleAttr(attrname, value)
        return
    rv = property(fget, fset, doc=doc)
    return rv


# End of file
