# -*- coding: utf-8 -*-
"""
Created on Fri Apr 28 09:04:11 2023

@author: osjac
"""

import pandas as pd
import numpy as np
import os
import jdcal
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.colors as colors
import math
import matplotlib.colors as colors
from copy import copy, deepcopy

# Function to load data from a CSV file
def loadDataCSV(file):
    # Use Pandas to read the CSV file
    df = pd.read_csv(file)
    # Convert the Pandas DataFrame to a Numpy array
    data = df.to_numpy()
    # Return the Numpy array
    return data

# Function to load data from all CSV files in a directory for a specific year
def loadYear(year,direc):
    
    year_str = str(year)

    allData = []
    # Initialize the number of columns in the data
    colNum = 0
    # Construct the directory path for the specific year
    directory_str = direc + "/" + year_str
    directory = os.fsencode(directory_str)

    # Iterate through the files in the directory
    for file in os.listdir(directory):
         filename = os.fsdecode(file)
         # Load the data from the CSV file if it ends with ".csv"
         if filename.endswith(".csv"):
             # Load the data using the loadDataCSV function and remove the first row
             df = pd.read_csv(directory_str + "/" + filename)   
             # Print the filename and the dimensions of the data
             print("Loading: " + filename + " Dimensions:")
             
             allData.append(df)
            
    dataCombined = pd.concat(allData)
    
    dataCombined.pop(dataCombined.columns[0])   
    dataCombined = dataCombined.sort_values(by=['jd'])         
    
    # Return the combined data
    return dataCombined



def loadMonth(year,month,direc):
    year_str = str(year)
    month_str = str(month)
    directory_str = direc + "/" + year_str + month_str + "processedRCC.csv"
    df = pd.read_csv(directory_str)
    return df


def inverseExtendedJD(JulianDate):
    year, month, day, day_frac = jdcal.jd2gcal(0, JulianDate)

    total_seconds = int(day_frac * 24 * 60 * 60)
    hours = total_seconds // 3600 
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60 

    return [year, month, day, int(hours), int(minutes), seconds]


def extendedJD(year, month, day, hour, minute, second):
    JulianDate = sum(jdcal.gcal2jd(year, month, day))
    ExtendedPart =  hour/24 + minute/1440 + second/86400
    
    return JulianDate + ExtendedPart



def selectTimeFrame(allData, initial_time_gc, final_time_gc):
    initial_time = extendedJD(initial_time_gc[0], initial_time_gc[1], initial_time_gc[2], initial_time_gc[3], initial_time_gc[4], final_time_gc[5])
    final_time = extendedJD(final_time_gc[0], final_time_gc[1], final_time_gc[2], final_time_gc[3], final_time_gc[4], final_time_gc[5])
    selected_data = allData.loc[(allData['jd'] >= initial_time) & (allData['jd'] <= final_time)]
    
    return selected_data


def plot_timeframe(data, beam=None, start_time=None, end_time=None, time_adj=extendedJD(1996,0,0,0,0,0), param="v", size = 1,CMAP = 'viridis',str_title = " ",distance="slist",y_range = (0,75*45)):
    
    if (start_time or end_time) is not None:
        plot_time_start = extendedJD(start_time[0], start_time[1], start_time[2], start_time[3], start_time[4], start_time[5]) #- time_adj
        plot_time_end = extendedJD(end_time[0], end_time[1], end_time[2], end_time[3], end_time[4], end_time[5]) #- time_adj
        data_time = data.loc[(data['jd'] <= plot_time_end) & (data['jd'] >= plot_time_start)]
    else:
        start_time =  inverseExtendedJD(data['jd'].iloc[0])
        end_time = inverseExtendedJD(data['jd'].iloc[-1])
        data_time = deepcopy(data)
    
    if beam is not None:
      data_time = data_time.loc[( data_time["bmnum"] == beam )]
    else:
      beam = data_time["bmnum"].iloc[0]

    data_time["jd"] = data_time["jd"] - time_adj

    str_start = str(start_time[0]) + "/" + str(start_time[1]) + "/" + str(start_time[2]) + " " + str(start_time[3]) + ":" + str(start_time[4]) + ":" + str(start_time[5])
    str_end = str(end_time[0]) + "/" + str(end_time[1]) + "/" + str(end_time[2]) + " " + str(end_time[3]) + ":" + str(end_time[4]) + ":" + str(end_time[5])
    str_full = "|| " + str_start + "  to  " + str_end + " || beam " + str(beam) + " || " + str_title 
    print(str_full)

    if param == 'v':
      norm = colors.Normalize(vmin=-2000, vmax=2000)
    else:
      norm = colors.Normalize(vmin=data_time[param].min(), vmax=data_time[param].max())
    
    plt.scatter(data_time["jd"],
                data_time[distance]*45,
                c=data_time[param],
                s=size,
                cmap=CMAP,
                norm = norm)
    
    #plt.pcolormesh([data_time["jd"],data_time[distance]*45,],data_time[param],cmap=CMAP,norm = norm), marker = "|"


    plt.title(str_full)
    plt.xlabel("Extended JD without year (days)")
    plt.ylabel("Distance from radar (km)")
    #plt.colorbar(label = "Velocity (m/s)")
    plt.ylim(y_range)
    plt.colorbar(label = param)
    fig = plt.gcf()
    fig.set_size_inches(20, 5)
    #fig.set_size_inches(12, 8)
    ax = plt.gca()
    ax.set_facecolor('grey')
    ax.grid(False)
    plt.show()
    
    
    
def feature_plots(dataframe, beam = None, param = "v", cluster = None):

  if beam is not None:
    dataframe = dataframe.loc[( dataframe["bmnum"] == beam )]
  else:
    beam = dataframe["bmnum"].iloc[0]
  
  if cluster is not None:
    dataframe = dataframe.loc[( dataframe[param] == cluster )]


  # Create a figure with subplots for each unique combination of columns
  fig, axs = plt.subplots(3, 3, figsize=(30, 10))


  temp1 = axs[0,0].scatter(dataframe["v"],dataframe["slist"], c = dataframe[param],cmap= 'viridis',alpha=0.5)
  axs[0,0].set_xlabel('velocity')
  axs[0,0].set_ylabel('range gate')
  plt.colorbar(temp1)

  temp2 = axs[0,1].scatter(dataframe["v"],dataframe["p_l"], c = dataframe[param],cmap= 'viridis',alpha=0.5)
  axs[0,1].set_xlabel('velocity')
  axs[0,1].set_ylabel('power')
  plt.colorbar(temp2)

  temp3 = axs[1,0].scatter(dataframe["v"],dataframe["w_l"], c = dataframe[param],cmap= 'viridis',alpha=0.5)
  axs[1,0].set_xlabel('velocity')
  axs[1,0].set_ylabel('spetral width')
  plt.colorbar(temp3)

  temp4 = axs[1,1].scatter(dataframe["w_l"],dataframe["p_l"], c = dataframe[param],cmap= 'viridis',alpha=0.5)
  axs[1,1].set_xlabel('spetral width')
  axs[1,1].set_ylabel('power')
  plt.colorbar(temp4)

  temp5 = axs[1,2].scatter(dataframe["w_l"],dataframe["slist"], c = dataframe[param],cmap= 'viridis',alpha=0.5)
  axs[1,2].set_xlabel('spetral width')
  axs[1,2].set_ylabel('range gate')
  plt.colorbar(temp5)

  temp6 = axs[0,2].scatter(dataframe["p_l"],dataframe["slist"], c = dataframe[param],cmap= 'viridis',alpha=0.5)
  axs[0,2].set_xlabel('power')
  axs[0,2].set_ylabel('range gate')
  plt.colorbar(temp6)
 
  temp7 = axs[2,0].scatter(dataframe["jd"],dataframe["v"], c = dataframe[param],cmap= 'viridis',alpha=0.5)
  axs[2,0].set_xlabel('time')
  axs[2,0].set_ylabel('velocity')
  plt.colorbar(temp7)

  temp8 = axs[2,1].scatter(dataframe["jd"],dataframe["p_l"], c = dataframe[param],cmap= 'viridis',alpha=0.5)
  axs[2,1].set_xlabel('time')
  axs[2,1].set_ylabel('power')
  plt.colorbar(temp8)

  temp9 = axs[2,2].scatter(dataframe["jd"],dataframe["w_l"], c = dataframe[param],cmap= 'viridis',alpha=0.5)
  axs[2,2].set_xlabel('time')
  axs[2,2].set_ylabel('spetral width')
  plt.colorbar(temp9)


  fig.suptitle('Feature Plots')