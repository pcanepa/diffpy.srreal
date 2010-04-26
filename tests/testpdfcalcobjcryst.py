#!/usr/bin/env python

"""Unit tests for pdfcalculator.py on ObjCryst crystal structures
"""

# version
__id__ = '$Id$'

import os
import re
import unittest

import numpy
from diffpy.srreal.pdfcalculator import PDFCalculator

from testpdfcalculator import _maxNormDiff

# useful variables
thisfile = locals().get('__file__', 'file.py')
tests_dir = os.path.dirname(os.path.abspath(thisfile))
testdata_dir = os.path.join(tests_dir, 'testdata')

# helper functions

def _loadTestStructure(basefilename):
    from pyobjcryst.crystal import CreateCrystalFromCIF
    fullpath = os.path.join(testdata_dir, basefilename)
    crst = CreateCrystalFromCIF(open(fullpath))
    return crst


def _loadExpectedPDF(basefilename):
    '''Read expected result and return a tuple of (r, g, cfgdict).
    '''
    rxf = re.compile(r'[-+]?(\d+(\.\d*)?|\.\d+)([eE][-+]?\d+)?')
    fullpath = os.path.join(testdata_dir, basefilename)
    cfgdict = {}
    for line in open(fullpath):
        if line[:1] != '#':  break
        w = line.split()
        has_cfgdata = (len(w) == 4 and w[2] == '=')
        if not has_cfgdata:  continue
        cfgdict[w[1]] = w[3]
        if rxf.match(w[3]):  cfgdict[w[1]] = float(w[3])
    r, g = numpy.loadtxt(fullpath, usecols=(0, 1), unpack=True)
    rv = (r, g, cfgdict)
    return rv


def _makePDFCalculator(crst, cfgdict):
    '''Return a PDFCalculator object evaluated for a pyobjcryst.Crystal crst.
    '''
    inpdfcalc = lambda kv: kv[0] not in ('biso', 'type')
    pdfcargs = dict(filter(inpdfcalc, cfgdict.items()))
    pdfc = PDFCalculator(**pdfcargs)
    if 'biso' in cfgdict:
        setbiso = lambda sc: sc.mpScattPow.SetBiso(cfgdict['biso'])
        map(setbiso, crst.GetScatteringComponentList())
    if 'type' in cfgdict:
        pdfc.setScatteringFactorTable(cfgdict['type'])
    pdfc.eval(crst)
    # avoid metadata override by PDFFitStructure
    for k, v in pdfcargs.items():
        setattr(pdfc, k, v)
    return pdfc


##############################################################################
class TestPDFCalcObjcryst(unittest.TestCase):

    def _comparePDFs(self, nickname, pdfbasename, cifbasename):
        def setself(**kwtoset):
            for n, v in kwtoset.iteritems():
                setattr(self, nickname + '_' + n, v)
            return
        r, gobs, cfg = _loadExpectedPDF(pdfbasename)
        setself(r=r, gobs=gobs, cfg=cfg)
        crst = _loadTestStructure(cifbasename)
        setself(crst=crst)
        pdfc = _makePDFCalculator(crst, cfg)
        gcalc = pdfc.getPDF()
        mxnd = _maxNormDiff(gobs, gcalc)
        setself(gcalc=gcalc, mxnd=mxnd)
        return


    def test_CdSeN(self):
        '''check PDFCalculator on ObjCryst loaded CIF, neutrons
        '''
        self._comparePDFs('cdsen',
                'CdSe_cadmoselite_N.fgr', 'CdSe_cadmoselite.cif')
        self.failUnless(self.cdsen_mxnd < 0.005)
        return


    def test_CdSeX(self):
        '''check PDFCalculator on ObjCryst loaded CIF, xrays
        '''
        self._comparePDFs('cdsex',
                'CdSe_cadmoselite_X.fgr', 'CdSe_cadmoselite.cif')
        self.failUnless(self.cdsex_mxnd < 0.005)
        return


    def test_rutileaniso(self):
        '''check PDFCalculator on ObjCryst loaded anisotropic rutile
        '''
        self._comparePDFs('rutileaniso',
                'TiO2_rutile-fit.fgr', 'TiO2_rutile-fit.cif')
        self.failUnless(self.rutileaniso_mxnd < 0.057)
        return


# End of class TestPDFCalcObjcryst


if __name__ == '__main__':
    unittest.main()