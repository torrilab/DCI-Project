#!/usr/bin/env python
# coding: utf-8

# In[3]:


# ============================================================
# TrackedProfiles_DataLoading_CLASS
# ============================================================

#Libraries
import os
import pickle
from datetime import datetime, timedelta

class TrackedProfiles_DataLoading_CLASS:
    """
    A utility class for saving and loading tracked profile results
    """

    @staticmethod
    def SaveProfile(ModelData,DataManager, Dictionary, dataName, t):
        profileType = "TrackedProfiles"
        timeString = t if isinstance(t, str) else ModelData.timeStrings[t]
        
        fileName = f"{profileType}_{dataName}_{ModelData.res}_{ModelData.t_res}_{ModelData.Nz_str}nz_{timeString}.pkl"
        filePath = os.path.join(DataManager.outputDataDirectory,fileName)
        
        with open(filePath, "wb") as f:
            pickle.dump(Dictionary, f, protocol=pickle.HIGHEST_PROTOCOL)
    
        print(f"Saved output to {filePath}","\n")

    @staticmethod
    def LoadProfile(ModelData, DataManager, dataName, t):
        """
        Load a saved TrackedProfiles .pkl file for a given time index t.
        """
        profileType = "TrackedProfiles"
        timeString = t if isinstance(t, str) else ModelData.timeStrings[t]
        
        fileName = f"{profileType}_{dataName}_{ModelData.res}_{ModelData.t_res}_{ModelData.Nz_str}nz_{timeString}.pkl"
        filePath = os.path.join(DataManager.outputDataDirectory,fileName)
    
        with open(filePath, "rb") as f:
            Dictionary = pickle.load(f)
    
        # print(f"Loaded profile dictionary from {filePath}\n")
        return Dictionary

    @staticmethod
    def ExtractProfileStandardErrorArrays(profileDict,ProfileStandardError):
        """
        From a nested dictionary like trackedProfileArrays, compute standard error arrays
        using ProfileStandardError(profile_array, profile_array_squares) for each variable,
        and return a new dictionary with the same structure, but only 'profile_array_SE'.
        """
        output = {}
    
        for category, depth_dict in profileDict.items():
            output[category] = {}
    
            for depth, var_dict in depth_dict.items():
                output[category][depth] = {}
    
                for varName, arrays in var_dict.items():
                    profile     = arrays.get("profile_array")
                    profile_sq  = arrays.get("profile_array_squares")
    
                    if profile is not None and profile_sq is not None:
                        profile_SE = ProfileStandardError(profile, profile_sq)
                        output[category][depth][varName] = {
                            "profile_array_SE": profile_SE
                        }
        return output

    @staticmethod
    def ConvertTimeStringsToDatetime(timeStrings):
        """
        '0-00-00' → 2022-06-22 06:00
        'hour-min-sec' = '0-00-00'
        end_time: 5 pm
        """
        startDatetime = datetime(2022, 6, 22, 6, 0, 0)
    
        datetimeList = []
        for t in timeStrings:
            hour, minute, second = map(int, t.split("-"))
    
            dt = startDatetime + timedelta(
                hours=hour,
                minutes=minute,
                seconds=second
            )
            datetimeList.append(dt)
    
        return np.array(datetimeList)

    @staticmethod
    def FindTimeWindowIndices(timeDatetimes, startHour, endHour):
        startTime = timeDatetimes[0].replace(hour=startHour, minute=0)
        endTime   = timeDatetimes[0].replace(hour=endHour, minute=0)
    
        return [
            i for i, dt in enumerate(timeDatetimes)
            if startTime <= dt < endTime
        ]


#Example Call
#IMPORT CLASSES
# sys.path.append(os.path.join(mainCodeDirectory,"3_Project_Algorithms","3_Tracked_Profiles"))
# from CLASSES_TrackedProfiles import TrackedProfiles_DataLoading_CLASS

#Example Run
#saving
# TrackedProfiles_DataLoading_CLASS.SaveProfile(ModelData,DataManager_TrackedProfiles, profileArraysDictionary, t)
#loading
# TrackedProfiles_DataLoading_CLASS.LoadProfile(ModelData,DataManager_TrackedProfiles, t)


# In[3]:


# ============================================================
# TrackedProfiles_Plotting_CLASS
# ============================================================

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.lines import Line2D

class TrackedProfiles_Plotting_CLASS:

    @staticmethod
    def ProfileMean(profile): 
        """
        Input Requires Three Column Array 
        with Sum in 1st Column, Count in 2nd Column, and Index in 3rd Column
        Returns 1st and 3rd Column (removing zero rows)
        """
        #gets rid of rows that have no data
        profile_mean=profile[ (profile[:, 1] > 1)]; 
        #divides the data column by the counter column
        profile_mean=np.array([profile_mean[:, 0] / profile_mean[:, 1], profile_mean[:, 2]]).T 
        return profile_mean

    # === Category and depth styles ===
    category_styles = {"CL": "solid", "nonCL": "dashed", "SBF": "dashdot"}
    depth_colors = {"SHALLOW": "green", "DEEP": "blue"}

    @staticmethod
    def PlotSE(axis, profile, SE_profile, color, multiplier=1, switch=1, alpha=0.1, min_value=None):
        lower = multiplier * profile[:, 0] - multiplier * SE_profile[:, 0] * switch
        upper = multiplier * profile[:, 0] + multiplier * SE_profile[:, 0] * switch
        
        if min_value is not None:
            lower = np.maximum(lower, min_value)
        axis.fill_betweenx(profile[:, -1], lower, upper, color=color, alpha=alpha)

    @staticmethod
    def GetHLines(LevelsDictionary):
        hLine_1 = LevelsDictionary["min_all_cloudbase"]
        hLine_2 = LevelsDictionary["MeanLFC"]
    
        hLines = (hLine_1,hLine_2)
        hLineColors = ("purple","#FF8C00")
        return hLines,hLineColors
    @staticmethod
    def PlotHLines(axis,hLines,hLineColors):
        for (hLine,hLineColor) in zip(hLines,hLineColors):
            axis.axhline(hLine, color=hLineColor, linestyle='dashed', zorder=-10)
    @staticmethod
    def GetTimeSlice(ModelData,timeIndiceRange):
        if timeIndiceRange == "":
            timeSlice = np.arange(ModelData.Ntime)
        else:
            split = timeIndiceRange.split('-'); a=int(split[0][1:]); b=int(split[1])
            timeStrings_datetime=TrackedProfiles_DataLoading_CLASS.ConvertTimeStringsToDatetime(ModelData.timeStrings)
            timeSlice = TrackedProfiles_DataLoading_CLASS.FindTimeWindowIndices(timeStrings_datetime,a,b)
        return timeSlice
    @staticmethod
    def UpdateMeanLFC(ModelData,timeIndiceRange,LevelsDictionary,LFC_profile):    
        timeSlice = TrackedProfiles_Plotting_CLASS.GetTimeSlice(ModelData,timeIndiceRange)
        MeanLFC = np.nanmean(LFC_profile[timeSlice])
        LevelsDictionary['MeanLFC']=MeanLFC
        return LevelsDictionary
    @staticmethod
    def ApplyXLimFromZLim(axis, zlim, buffer=0.05):
        """
        Adjust the x-limits of the axis by examining all lines plotted on it.
        Only considers x-values where y is within the zlim range.
        """
        x_all = []
        y_all = []
    
        for line in axis.get_lines():
            xdata = line.get_xdata()
            ydata = line.get_ydata()
            x_all.append(xdata)
            y_all.append(ydata)
    
        if not x_all or not y_all:
            return  # No lines to process
    
        x_all = np.concatenate(x_all)
        y_all = np.concatenate(y_all)
    
        mask = (y_all >= zlim[0]) & (y_all <= zlim[1])
        if np.any(mask):
            xmin = np.min(x_all[mask])
            xmax = np.max(x_all[mask])
            delta = xmax - xmin if xmax > xmin else xmax * buffer
            axis.set_xlim(xmin - delta * buffer, xmax + delta * buffer)
    
        axis.set_ylim(zlim)

    # @staticmethod
    # def AddCategoryLegend(fig, parcelTypes=["CL", "nonCL", "SBF"], loc='upper center', bbox=(0.5, 0.93)):
    #     """
    #     Adds a custom legend for parcel types based on linestyle (e.g., CL, nonCL, SBF).
    #     """
    #     linestyle_map = {
    #         "CL": "solid",
    #         "nonCL": "dashed",
    #         "SBF": "dashdot"
    #     }
    
    #     custom_lines = [
    #         Line2D([0], [0], color='black', linestyle=linestyle_map[ptype],
    #                linewidth=1.5, label=ptype)
    #         for ptype in parcelTypes if ptype in linestyle_map
    #     ]
    
    #     fig.legend(
    #         handles=custom_lines,
    #         loc=loc,
    #         ncol=len(custom_lines),
    #         fontsize=10,
    #         title='Parcel Types',
    #         title_fontsize=12,
    #         bbox_to_anchor=bbox,
    #         borderaxespad=0,
    #         frameon=True
    #     )

    @staticmethod
    def AddCategoryLegend(fig, parcelTypes=["CL", "nonCL", "SBF"], loc='upper center', bbox=(0.5, 0.93)):
        """
        Adds a custom legend using a list comprehension to avoid an explicit for-loop block.
        """
        styles = ["solid", "dashed", "dashdot", "dotted"]
    
        # This single list comprehension replaces the entire loop and mapping logic
        custom_lines = [
            Line2D([0], [0], color='black', linestyle=styles[i % len(styles)], 
                   linewidth=1.5, label=ptype)
            for i, ptype in enumerate(parcelTypes)
        ]
    
        fig.legend(
            handles=custom_lines,
            loc=loc,
            ncol=len(custom_lines),
            fontsize=10,
            title='Parcel Types',
            title_fontsize=12,
            bbox_to_anchor=bbox,
            borderaxespad=0,
            frameon=True
        )

    @staticmethod
    def AddDepthLegend(axis, depths=["ALL", "SHALLOW", "DEEP"], loc='upper right'):
        """
        Adds a legend to a specific axis for cloud depth categories (color-coded).
        """
        color_map = {
            "SHALLOW": "green",
            "DEEP": "blue"
        }
    
        legend_lines = [
            Line2D([0], [0], color=color_map[d], linestyle='solid',
                   linewidth=2, label=d)
            for d in depths if d in color_map
        ]
    
        axis.legend(
            handles=legend_lines,
            loc=loc,
            title='Cloud Types',
            title_fontsize=10,
            fontsize=9,
            frameon=True
        )
    
    # === Level 3: Plot one line ===
    @staticmethod
    def PlotProfileLine(axis, profile, SE_profile, parcelType, parcelDepth,
                        multiplier=1, color=None,
                        linestyle_override=None):
        avg = TrackedProfiles_Plotting_CLASS.ProfileMean(profile)
        x = multiplier * avg[:, 0]
        y = avg[:, 1]
    
        #Allow explicit color override (new behavior)
        color = color or TrackedProfiles_Plotting_CLASS.depth_colors.get(parcelDepth, "gray")
        linestyle = linestyle_override if linestyle_override is not None else TrackedProfiles_Plotting_CLASS.category_styles.get(parcelType, "solid") 
        label = f"{parcelType}-{parcelDepth}"
    
        # Plot main line
        axis.plot(x, y, color=color, linestyle=linestyle, linewidth=1, label=label)
    
        # Plot SE band
        if SE_profile is not None:
            TrackedProfiles_Plotting_CLASS.PlotSE(axis, avg, SE_profile,
                                                  color=color, multiplier=multiplier)
    
    
    # === Level 2: Plot all depths for a given parcelType ===
    @staticmethod
    def PlotAllDepths(axis, profiles, profilesSE, parcelType, variableName,
                      parcelDepths, multiplier=1, color=None, zlim=(0, 6),
                      locationSubset="",linestyle_override=None):
        for parcelDepth in parcelDepths:
            profile = profiles[parcelType][parcelDepth][variableName][f"profile_array{locationSubset}"]
            SE_profile = None
            if profilesSE:
                SE_profile = profilesSE[parcelType][parcelDepth][variableName].get(f"profile_array{locationSubset}_SE")
    
            #Pass color downstream
            TrackedProfiles_Plotting_CLASS.PlotProfileLine(axis, profile, SE_profile, parcelType, parcelDepth,
                                                           multiplier=multiplier, color=color,
                                                           linestyle_override=linestyle_override)
    
        TrackedProfiles_Plotting_CLASS.ApplyXLimFromZLim(axis, zlim)
    
    
    # === Level 1: Plot one variable to a single axis ===
    @staticmethod
    def PlotSingleVariable(axis, profiles, profilesSE, variableName, variableInfo,
                           parcelTypes, parcelDepths, hLines, hLineColors,
                           color=None, zlim=(0,6),
                           locationSubset=""):
        label = variableInfo[variableName]["label"]
        units = variableInfo[variableName]["units"]
        multiplier = variableInfo[variableName].get("multiplier", 1)
    
        for i, parcelType in enumerate(parcelTypes):
            styles = ["solid", "dashed", "dashdot", "dotted"]
            current_linestyle = styles[i % len(styles)]
            TrackedProfiles_Plotting_CLASS.PlotAllDepths(axis, profiles, profilesSE, parcelType, variableName,
                                                         parcelDepths, multiplier=multiplier, color=color, zlim=zlim,
                                                         locationSubset=locationSubset,linestyle_override=current_linestyle)
            if variableName in ['VMF_g']:
                TrackedProfiles_Plotting_CLASS.PlotAllDepths(axis, profiles, profilesSE, parcelType, "VMF_c",
                                                             parcelDepths, multiplier=multiplier, color=color, zlim=zlim,
                                                             locationSubset=locationSubset,linestyle_override=current_linestyle)
    
        axis.set_ylabel("Height (km)")
        axis.set_xlabel(f"{label} {units}")
        axis.grid(True, linestyle="--", alpha=0.4)
        TrackedProfiles_Plotting_CLASS.PlotHLines(axis, hLines, hLineColors)

    # === Level 1: Plot one variable to a single axis (for operations between multiple variables)
    @staticmethod
    def PlotCompositeVariable(axis, profiles, variableName, variableInfo, 
                              parcelTypes, parcelDepths,
                              color=None, zlim=(0, 6), 
                              printstatement=False,
                              locationSubset="",
                              linestyle_override=True):
        """
        Plots derived variables defined by multi-step operations in variableInfo['splits'].
        e.g., ["TransferE_c", "-", "TransferE_g", "/", "E_c"]
        """
    
        info = variableInfo[variableName]
        label = info["label"]
        units = info["units"]
        multiplier = info.get("multiplier", 1)
        splits = info.get("splits")
    
        if splits is None:
            raise ValueError(f"'splits' not defined for {variableName}")

        styles = ["solid", "dashed", "dashdot", "dotted"]
    
        for idx, parcelType in enumerate(parcelTypes):
            current_linestyle = styles[idx % len(styles)]
            for parcelDepth in parcelDepths:
    
                # Load first variable
                first_var = splits[0]
                try:
                    result_prof = profiles[parcelType][parcelDepth][first_var][f"profile_array{locationSubset}"]
                    result = TrackedProfiles_Plotting_CLASS.ProfileMean(result_prof)[:, 0]
                    z = TrackedProfiles_Plotting_CLASS.ProfileMean(result_prof)[:, 1]
                except KeyError:
                    print(f"Missing first variable '{first_var}', skipping this combination.")
                    continue
    
                # Apply operations in sequence
                i = 1
                while i < len(splits):
                    op = splits[i]
                    varname = splits[i + 1]
    
                    try:
                        next_prof = TrackedProfiles_Plotting_CLASS.ProfileMean(
                            profiles[parcelType][parcelDepth][varname][f"profile_array{locationSubset}"]
                        )[:, 0]
                    except KeyError:
                        next_prof = np.zeros_like(result)
                        print(f"Missing '{varname}', using zeros for '{op}' operation")
    
                    # Perform operation
                    if op == "-":
                        if printstatement==True:
                            print(f"    Performing: ({first_var} - {varname})")
                        result = result - next_prof
                        first_var = f"({first_var}-{varname})"
                    elif op == "/":
                        if printstatement==True:
                            print(f"    Performing: ({first_var} / {varname})")
                        result = np.divide(result, next_prof, out=np.zeros_like(result), where=next_prof != 0)
                        first_var = f"({first_var}/{varname})"
                    else:
                        raise ValueError(f"Unsupported operator '{op}'")
    
                    i += 2  # move to next operator-variable pair
    
                # Apply multiplier
                x = result * multiplier
                y = z
    
                color_use = color or TrackedProfiles_Plotting_CLASS.depth_colors.get(parcelDepth, "gray")
                linestyle = current_linestyle if linestyle_override is True else TrackedProfiles_Plotting_CLASS.category_styles.get(parcelType, "solid")
                label_line = f"{parcelType}-{parcelDepth}"
    
                axis.plot(x, y, color=color_use, linestyle=linestyle, linewidth=1, label=label_line)
    
        axis.set_xlabel(f"{label} {units}")
        axis.set_ylabel("Height (km)")
        axis.grid(True, linestyle="--", alpha=0.4)
        TrackedProfiles_Plotting_CLASS.ApplyXLimFromZLim(axis, zlim)


# In[ ]:


# ============================================================
# LocationSubset_Plotting_CLASS
# ============================================================

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.lines import Line2D
import numpy as np

class LocationSubset_Plotting_CLASS:
    
    
    @staticmethod
    def AddDepthLegend(fig, depthTypes=["SHALLOW", "DEEP"],
                                      loc='upper center', bbox=(0.5, 0.93)):
        """
        Adds a custom legend for depth categories (e.g., SHALLOW, DEEP)
        based on linestyle.
        """
        linestyle_map = {
            "SHALLOW": "--",
            "DEEP": "-"
        }
    
        custom_lines = [
            Line2D([0], [0], color='black',
                   linestyle=linestyle_map.get(dtype, "-"),
                   linewidth=2.0, label=dtype)
            for dtype in depthTypes
        ]
    
        fig.legend(
            handles=custom_lines,
            loc=loc,
            ncol=len(custom_lines),
            fontsize=10,
            title='Depth Category',
            title_fontsize=11,
            bbox_to_anchor=bbox,
            borderaxespad=0.5,
            frameon=True,
            fancybox=True,
            framealpha=0.9
        )
    
    @staticmethod
    def AddSubsetLegend(fig,
                                       subset_labels=['everywhere', 'left of SBF', 'right of SBF'],
                                       colors=['black', '#1E90FF', '#D32F2F'],
                                       loc='upper center', bbox=(0.5, 0.98)):
        """
        Adds a custom legend for SBF subset categories (everywhere, left, right)
        based on color.
        """
        custom_lines = [
            Line2D([0], [0], color=color, linestyle='-', linewidth=2.0, label=label)
            for label, color in zip(subset_labels, colors)
        ]
    
        fig.legend(
            handles=custom_lines,
            loc=loc,
            ncol=len(custom_lines),
            fontsize=10,
            title='SBF Subset',
            title_fontsize=11,
            bbox_to_anchor=bbox,
            borderaxespad=0.5,
            frameon=True,
            fancybox=True,
            framealpha=0.9
        )

    @staticmethod
    def GetVariableAxes(fig, variableName):
        return [ax for ax in fig.get_axes()
                if getattr(ax, "variableName", None) == variableName]

    @staticmethod
    def PlotProfiles(trackedProfileArrays, variableInfo,
                        parcelTypes=["CL", "nonCL", "SBF"],
                        variableNames=None,
                        subsetTypes=["", "_left", "_right"],
                        labels=['everywhere', 'left of SBF', 'right of SBF'],
                        colors=['black', '#1E90FF', '#D32F2F'],
                        depthTypes=['SHALLOW', 'DEEP'],
                        linestyles=['--', '-'],
                        zlim=(0,6),
                        figsize_scale=7,
                        top_adjust=0.82,
                        ncols_inner = 3):
        """
        Create a 1×N grid of parcel-type subplots (e.g., CL, nonCL, SBF),
        each containing multiple variable panels.
        """
        # === Helper functions ===
        def GetProfileAverage(parcelType,depthType,varName,subsetType):
            profile = trackedProfileArrays[parcelType][depthType][varName][f'profile_array{subsetType}']
            return TrackedProfiles_Plotting_CLASS.ProfileMean(profile)
    
        def Plot(ax, multiplier, profileAverage, color, linestyle):
            xvals = multiplier * profileAverage[:, 0]
            yvals = profileAverage[:, 1]
            ax.plot(xvals, yvals, color=color, linestyle=linestyle)
    
        # === Auto-fill variableNames if not specified ===
        if variableNames is None:
            variableNames = list(variableInfo.keys())
    
        # # === Figure setup === (old)
        # n_parcels = len(parcelTypes)
        # fig = plt.figure(figsize=(figsize_scale * n_parcels, 10))
        # outer_gs = gridspec.GridSpec(1, n_parcels, figure=fig, wspace=0.15)
    
        # ncols_inner = 3
        # nrows_inner = int(np.ceil(len(variableNames) / ncols_inner))
        # === Figure setup ===
        n_parcels = len(parcelTypes)
        nrows_inner = int(np.ceil(len(variableNames) / ncols_inner))
        
        # dynamically scale height by number of variable rows
        base_row_height = 3.2  # inch per row, tweak as needed
        fig_height = base_row_height * nrows_inner
        
        fig = plt.figure(figsize=(figsize_scale * n_parcels, fig_height))
        outer_gs = gridspec.GridSpec(1, n_parcels, figure=fig, wspace=0.15)
    
        # === Loop through parcel types ===
        for i, parcelType in enumerate(parcelTypes):
            inner_gs = outer_gs[i].subgridspec(nrows_inner, ncols_inner, wspace=0.25, hspace=0.35)
    
            for j, variableName in enumerate(variableNames):
                r, c = divmod(j, ncols_inner)
                ax = fig.add_subplot(inner_gs[r, c])
                ax.variableName = variableName
    
                info = variableInfo.get(variableName, {"label": variableName, "units": "", "multiplier": 1})
                multiplier = info["multiplier"]
    
                # --- Plot profiles ---
                for (subsetType, label, color) in zip(subsetTypes, labels, colors):
                    for (depthType, linestyle) in zip(depthTypes, linestyles):
                        var_list = [variableName]
                        if variableName == "VMF_g":
                            var_list.append("VMF_c")
                        for v in var_list:
                            profileAverage = GetProfileAverage(parcelType, depthType, v, subsetType)
                            Plot(ax, multiplier, profileAverage, color, linestyle)
    
                # --- Formatting ---
                TrackedProfiles_Plotting_CLASS.ApplyXLimFromZLim(ax, zlim)
                ax.set_title(f"{info['label']} {info['units']}", fontsize=11)
                if c == 0:
                    ax.set_ylabel("Height (km)")
                else:
                    ax.set_yticklabels([])
                    ax.set_yticks([])
    
            # === Block title ===
            ax_title = fig.add_subplot(outer_gs[i])
            ax_title.set_title(parcelType, fontsize=14, pad=20, weight="bold")
            ax_title.axis("off")
    
        # === Legends ===
        LocationSubset_Plotting_CLASS.AddSubsetLegend(fig, subset_labels=labels, colors=colors, bbox=(0.5, 0.985))
        LocationSubset_Plotting_CLASS.AddDepthLegend(fig, depthTypes=depthTypes, bbox=(0.5, 0.93))
    
        fig.subplots_adjust(top=top_adjust)
    
        return fig
    
    # === Composite version: for derived variables using variableInfo["splits"] ===
    @staticmethod
    def PlotCompositeProfiles(trackedProfileArrays, variableInfo,
                              parcelTypes=["CL", "nonCL", "SBF"],
                              variableNames=None,
                              subsetTypes=["", "_left", "_right"],
                              labels=['everywhere', 'left of SBF', 'right of SBF'],
                              colors=['black', '#1E90FF', '#D32F2F'],
                              depthTypes=['SHALLOW', 'DEEP'],
                              linestyles=['--', '-'],
                              zlim=(0,6),
                              figsize_scale=7,
                              top_adjust=0.82,
                              ncols_inner=3):
        """
        Similar to PlotProfiles, but computes and plots derived variables
        defined in variableInfo[var]['splits'] (multi-step operations).
        """
        def ComputeCompositeProfile(parcelType, depthType, varName, subsetType):
            info = variableInfo[varName]
            splits = info.get("splits")
            if splits is None:
                raise ValueError(f"'splits' not defined for {varName}")
            
            # --- Load first variable ---
            first_var = splits[0]
            try:
                prof = trackedProfileArrays[parcelType][depthType][first_var][f'profile_array{subsetType}']
                result_prof = TrackedProfiles_Plotting_CLASS.ProfileMean(prof)
                result = result_prof[:, 0]
                z = result_prof[:, 1]
            except KeyError:
                return None, None  # skip if missing
            
            # --- Apply operations ---
            i = 1
            while i < len(splits):
                op = splits[i]
                next_var = splits[i + 1]
                try:
                    next_prof = trackedProfileArrays[parcelType][depthType][next_var][f'profile_array{subsetType}']
                    next_prof_mean = TrackedProfiles_Plotting_CLASS.ProfileMean(next_prof)[:, 0]
                except KeyError:
                    next_prof_mean = np.zeros_like(result)
                
                if op == "-":
                    result = result - next_prof_mean
                elif op == "/":
                    result = np.divide(result, next_prof_mean, out=np.zeros_like(result), where=next_prof_mean != 0)
                else:
                    raise ValueError(f"Unsupported operator '{op}' in splits for {varName}")
                i += 2
            
            return np.column_stack((result, z)), info.get("multiplier", 1)
    
        # === Auto-fill variableNames if not specified ===
        if variableNames is None:
            variableNames = [v for v in variableInfo if "splits" in variableInfo[v]]
    
        # === Figure setup ===
        n_parcels = len(parcelTypes)
        nrows_inner = int(np.ceil(len(variableNames) / ncols_inner))
        base_row_height = 3.2
        fig_height = base_row_height * nrows_inner
    
        fig = plt.figure(figsize=(figsize_scale * n_parcels, fig_height))
        outer_gs = gridspec.GridSpec(1, n_parcels, figure=fig, wspace=0.15)
    
        # === Loop through parcel types ===
        for i, parcelType in enumerate(parcelTypes):
            inner_gs = outer_gs[i].subgridspec(nrows_inner, ncols_inner, wspace=0.25, hspace=0.35)
    
            for j, variableName in enumerate(variableNames):
                r, c = divmod(j, ncols_inner)
                ax = fig.add_subplot(inner_gs[r, c])
                ax.variableName = variableName
    
                info = variableInfo.get(variableName, {"label": variableName, "units": "", "multiplier": 1})
                multiplier = info.get("multiplier", 1)
    
                # --- Plot derived profiles ---
                for (subsetType, label, color) in zip(subsetTypes, labels, colors):
                    for (depthType, linestyle) in zip(depthTypes, linestyles):
                        prof_data, multiplier_local = ComputeCompositeProfile(parcelType, depthType, variableName, subsetType)
                        if prof_data is None:
                            continue
                        x = prof_data[:, 0] * multiplier_local
                        y = prof_data[:, 1]
                        ax.plot(x, y, color=color, linestyle=linestyle)
    
                # --- Formatting ---
                TrackedProfiles_Plotting_CLASS.ApplyXLimFromZLim(ax, zlim)
                ax.set_title(f"{info['label']} {info['units']}", fontsize=11)
                if c == 0:
                    ax.set_ylabel("Height (km)")
                else:
                    ax.set_yticklabels([])
                    ax.set_yticks([])
    
            # === Block title ===
            ax_title = fig.add_subplot(outer_gs[i])
            ax_title.set_title(parcelType, fontsize=14, pad=20, weight="bold")
            ax_title.axis("off")
    
        # === Legends ===
        LocationSubset_Plotting_CLASS.AddSubsetLegend(fig, subset_labels=labels, colors=colors, bbox=(0.5, 0.985))
        LocationSubset_Plotting_CLASS.AddDepthLegend(fig, depthTypes=depthTypes, bbox=(0.5, 0.91))
    
        fig.subplots_adjust(top=top_adjust)
        return fig


# In[ ]:


# ============================================================
# PiecewiseScale Class
# ============================================================

import matplotlib.scale as mscale
import matplotlib.transforms as mtransforms

class PiecewiseScale_CLASS(mscale.ScaleBase):
    """
    Allows for non-linear axis ticks
    Custom piecewise y-axis scaling. The axis is linear below a specified height (yBreak), and compressed above it by a constant factor (scaleFactor).
    This case the break is at y=2 and above y=2, the tick spacing is compressed by 0.3.
    """
    name = 'piecewise'

    def __init__(self, axis, **kwargs):
        super().__init__(axis)
        self.yBreak = kwargs.get('yBreak', 2)
        self.scaleFactor = kwargs.get('scaleFactor', 0.3)

    def get_transform(self):
        return self.PiecewiseTransform(self.yBreak, self.scaleFactor)

    def set_default_locators_and_formatters(self, axis):
        pass  # keep defaults

    class PiecewiseTransform(mtransforms.Transform):
        input_dims = output_dims = 1
        is_separable = True

        def __init__(self, yBreak, scaleFactor):
            super().__init__()
            self.yBreak = yBreak
            self.scaleFactor = scaleFactor

        def transform_non_affine(self, y):
            y = np.array(y)
            return np.where(
                y < self.yBreak,
                y,
                self.yBreak + (y - self.yBreak) * self.scaleFactor
            )

        def inverted(self):
            return PiecewiseScale_CLASS.InvertedPiecewiseTransform(self.yBreak, self.scaleFactor)

    class InvertedPiecewiseTransform(mtransforms.Transform):
        input_dims = output_dims = 1
        is_separable = True

        def __init__(self, yBreak, scaleFactor):
            super().__init__()
            self.yBreak = yBreak
            self.scaleFactor = scaleFactor

        def transform_non_affine(self, y):
            y = np.array(y)
            return np.where(
                y < self.yBreak,
                y,
                self.yBreak + (y - self.yBreak) / self.scaleFactor
            )

# Register it
mscale.register_scale(PiecewiseScale_CLASS)

