# DCI-Project
Deep Convection Initiation Project

_Copyright ©2024-Present Abraham Roseman & Torri Lab_

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to use
the Software for personal or non-commercial purposes only, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
The Software may not be modified, reproduced, distributed, sublicensed, or used for
commercial purposes without explicit prior written permission from the copyright holder. 
The modification or reproduction is permitted for research purposes. 
The copyright holder will continue to maintain all rights to the software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN 
THE SOFTWARE.


**Figures**
Some code used for plotting main figures for final paper.

**Tracking Algorithms**

_eulerian_CL_tracking.ipynb_
Uses local max algorithm applied at each z-level applied across y-slices to find convergence line based on "convergence threshold". 
This threshold is dependent on data and should be tested by the researcher.

_lagrangian_tracking.ipynb_
Tracks parcels from within 0-1 km above LFC back in time to when vertical velocitiy W is within 2 km of CL.
Produced tracked parcels are refered to as "tracked parcels".

_lagrangian_cloud_BFS.ipynb_
Runs BFS algorithm at each level based on tracked parcels and averages these "clouds" and creates 2D histograms.

_eulerian_updrafts.ipynb_
Makes vertical profiles of variables including W, QV, QC,TH using "eulerian averaging" of thresholded locations (w>1, qc+qi>1e-6).

_Eulerian_Budget_Profile.ipynb_
Vertical profiles of budget variables using "eulerian binning" of thresholded locations (w>1, qc+qi>1e-6).

_DEEP_Lagrangian_Budget_Profile.ipynb_
Vertical profiles of budget variables using "lagrangian parcel binning" specific to Deep Convective tracked parcels.

_lagrangian_updrafts.ipynb_
Makes vertical profiles of variables including W, QV, QC,TH using "lagrangian parcel averaging" of thresholded locations (w>1, qc+qi>1e-6).

_Eulerian + Lagrangian Updraft.ipynb_
Combines plots from "eulerian_updrafts.ipynb" and "lagrangian_updrafts.ipynb" into one figure.

_Entrainment Profiles.ipynb_
Functions to calculate entrainment. Data is binned into vertical profiles and plotted for "general" and "cloudy updrafts".

RESIDENCE.ipynb
goal is to track dry air entrainment effects on cloudy updrafts, residence times, etc. currently in testing phase.

**Cold_Pool_Tracking**
... to be continued ...
