import os, glob
import numpy as np
import matplotlib.pylab as plt
from astropy.io import fits

import jwst
import jwst.pipeline as jpip

from jwst import datamodels

print('JWST pipeline version',jwst.__version__)

root = './'
data_dir = 'stage0'
s1_dir = 'stage1'
s2_dir = 'stage2'
s3_dir = 'stage3'

do1          = False
do_wcs       = False
do_ps        = False
do_fringe    = False
do_fluxcal   = False
do_cube      = False
do_extract   = False
plot_extract = True

if do1:
    # Now let's look for input files in our (cached) mirisim simulation directory
    sstring = os.path.join(root,data_dir,'det*exp1.fits')
    simfiles = sorted(glob.glob(sstring))

    for simfile in simfiles:
        det1              = jpip.Detector1Pipeline()  # Instantiate the pipeline
        det1.output_dir   = s1_dir                    # Specify where the output should go
        det1.refpix.skip  = True                      # Skip the reference pixel subtraction (as it doesn't                                                 interact well with simulated data)
        det1.save_results = True                      # Save the final resulting _rate.fits files
        det1(simfile)                                 # Run the pipeline on an input list of files

if do_wcs:
    # Look for our _rate.fits files produced by the Detector1 pipeline
    sstring   = os.path.join(root,s1_dir,'det*rate.fits')
    ratefiles = sorted(glob.glob(sstring))
    
    # Call the step, specifying that we want results saved into the spec2_dir directory
    for ratefile in ratefiles: 
        jwst.assign_wcs.AssignWcsStep.call(ratefile,save_results=True,output_dir=s2_dir)

if do_ps:
    # Look for our _rate.fits files produced by the Detector1 pipeline
    sstring  = os.path.join(root,s2_dir,'det*assignwcsstep.fits')
    wcsfiles = sorted(glob.glob(sstring))

    # Loop over files kludging the source type to POINT
    for wcsfile in wcsfiles:
        hdulist = fits.open(wcsfile, mode='update')
        hdulist['SCI'].header['SRCTYPE'] = 'POINT'
        hdulist.flush()
        hdulist.close()
        
if do_fringe:
      
    sstring  = os.path.join(root,s2_dir,'det*assignwcsstep.fits')
    wcsfiles = sorted(glob.glob(sstring))
    
    for wcsfile in wcsfiles:
        jwst.fringe.FringeStep.call(wcsfile,save_results=True,output_dir=s2_dir)

if do_fluxcal:
    
    sstring     = os.path.join(root,s2_dir,'det*fringestep.fits')
    fringefiles = sorted(glob.glob(sstring))
    
    for fringefile in fringefiles:
        jwst.photom.PhotomStep.call(fringefile,save_results=True,output_dir=s2_dir)

if do_cube:
    
    sstring      = os.path.join(root,s2_dir,'det*photomstep.fits')
    fluxcalfiles = sorted(glob.glob(sstring))

    for fluxcalfile in fluxcalfiles: # Note that the 'multi' makes this function like in the spec2 pipeline
        jwst.cube_build.CubeBuildStep.call(fluxcalfile,output_type='multi',save_results=True,output_dir=s2_dir)

if do_extract:

    sstring   = os.path.join(root,s2_dir,'det*s3d.fits')
    cubefiles = sorted(glob.glob(sstring))
    
    for cubefile in cubefiles:
        jwst.extract_1d.Extract1dStep.call(cubefile,save_results=True,output_dir=s2_dir)

if plot_extract:
    
    sstring   = os.path.join(root,s2_dir,'det*extract1dstep.fits')
    spec1dfiles = sorted(glob.glob(sstring))

    for spec1dfile in spec1dfiles:
        spec1d = fits.getdata(spec1dfile)
        plt.scatter(spec1d['WAVELENGTH'],spec1d['FLUX'],s=0.3)
        #plt.errorbar(spec1d['WAVELENGTH'],spec1d['FLUX'],yerr=spec1d['FLUX_ERROR'])
 
    plt.show()
    
breakpoint()
