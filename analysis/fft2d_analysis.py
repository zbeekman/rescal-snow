import os
import sys
import time as t
import numpy as np
import pandas as pd

can_plot = True
try:
    #Import graphing libraries if needed
    import imageio
    import matplotlib.pyplot as pl
    from mpl_toolkits.mplot3d import Axes3D as pl3d
    
except:
    can_plot = False
    pass

#Reads a file (1 row per line, each row should have same number of column values, separated by whitespaces), returns a numpy array
#filename -> the name of the file to open
#datatype -> the datatype of the values within the file (int, or float)
def read_data(filename,datatype):
    
    sig_2d = []
    f = open(filename, 'r')
    try:
        for line in f.readlines():
            line=line.strip()
            sig_2d.append(map(datatype,line.split()))
    finally:
        f.close()
        arr = np.array(sig_2d)
        try:
            x, y = arr.shape
            return np.array(sig_2d)
        except:
            print("\nError in data in file: {}\nData is not formatted correctly or missing. Check file is correct.".format(filename))
            exit()
        return np.array([])
    
#Reads all files in directory with specific extension and creates a list of numpy arrays containing numerical data
#dir_path -> The directory containing data files
#pref -> The standard prefix of datafiles
#datatype -> The type of data stored in each files (int or float data)
#skip_files -> Number of data files to skip, e.g. 5 = every 5th file is read, instead of all files.
#skip_file = 1 to not skip any files.
def read_directory(dir_path,pref,datatype,skip_files):

    print("Sorting through data files...")
    #Get array list of all files to open
    files = []
    try:
        for f in os.listdir(dir_path):
            if f.startswith(pref):
                files.append(os.path.join(dir_path,f))
    except:
        print("An error occured, check correct directory was passed.")    

    files.sort()
    count = 0.0
    max = len(files)/skip_files
    #Create list of numpy arrays containing data for each file
    print("Reading data files..")
    all_data = []
    for i, f in enumerate(files):
        if i % skip_files == 0:
            all_data.append(read_data(f,datatype))
            count += 1
            progress = (count / max) * 100.0
            sys.stdout.write('\r[{}] {}%'.format('#'*int(progress/5), round(progress,2)))
            sys.stdout.flush()
    return all_data


#Performs fft2d analysis on the data taken from input file and returns single quadrant fft result.
#data -> data to perform fft on
def fft2d_analyze(data):

    #Data points for x and y axis
    dpx, dpy = data.shape
        
    #Create x, y axis for graphing 2d
    x = np.arange(0,dpx)
    y = np.arange(0,dpy)

    #Set DC frequency bin to 0
    fft_data = data - np.mean(data)

    #Get fft2d and resize to single quadrant
    return np.fft.fft2(fft_data)[0:dpx/2,0:dpy/2]*2/(dpx*dpy)

#Performs fft2d analysis on all data in data list
#all_data -> a list of 2d numpy arrays containing data
def all_fft2d_analysis(all_data):
    
    all_fft_results = []
    for data in all_data:
        all_fft_results.append(fft2d_analyze(data))
    
    return all_fft_results

#Calculates all the amplitudes of the fft_analysis results
#all_fft -> fft results taken from all the data in a directory
def all_amplitudes(all_fft):
    
    all_amps = []
    for data in all_fft:
        all_amps.append(np.abs(data))
    return all_amps

#Calculates all the phases of the fft_analysis results
#all_fft -> fft results taken from all the data in a directory
def all_phases(all_fft):
    
    all_phases = []
    for data in all_fft:
        all_phases.append(np.angle(data)%(2*np.pi))
    return all_phases

#Locates the dominant frequencies within amplitude data by filtering with a threshold value
#Returns a list of dominant frequencies as well as a full list of all data of interest
#all_amps -> a list of numpy arrays containing amplitude data from fft results
#threshold -> the value used to filter out and detect dominant frequencies
def get_dominant_freqs(all_amps, threshold):
    dominant_freqs = []
    for amps in all_amps:
        top = top_percent(amps, threshold)
        if len(top) == 1:
            coords = (top[0][1],top[0][2])
            if coords not in dominant_freqs:
                dominant_freqs.append(coords)
    return dominant_freqs

#Creates a list of frequencies which meet the minimum amplitude threshold set
def purge_noise_freqs(all_amps, threshold):
    freqs = []
    l, w = all_amps[0].shape

    for amps in all_amps:
        if np.amax(amps) < threshold:
            continue
        else:
            for y in range(0,l-1):
                for x in range(0,w-1):
                    if amps[y][x] >= threshold and not (x,y) in freqs:
                        freqs.append((x,y))

    return freqs

#Get the top values based on a percentile threshold. Returns a list of values [value, x, y]
#E.g. .8 threshold will return data points with values >= (max-min)*.8 + min.
#values -> 2d array containing the values to threshold
#threshold -> thresholding percentage as a decimal (0.8=80%)
def top_percent(values, threshold):
    
    min = np.amin(values)
    max = np.amax(values)
    thresh_value = (max-min)*threshold+min
    
    top = []
    
    for i, y in enumerate(values):
        for ii, x in enumerate(y):
            if x >= thresh_value:
                top.append([x,ii,i])
                  
    return top


#Filters out all values below specified threshold, returns a list of values [value, x, y]
#values -> 2d array containing the values to filter
#threshold -> values that are below threshold are removed
def value_threshold(values, threshold):
    
    top = []
    for i, y in enumerate(values):
        for ii, x in enumerate(y):
            if x >= thresh_value:
                top.append([x,ii,i])
                  
    return top


#Returns 
def top_values(values, threshold, d_freqs):
    
    min = np.amin(values)
    max = np.amax(values)
    thresh_value = (max-min)*threshold+min
    
    top = []
    
    for i, y in enumerate(values):
        for ii, x in enumerate(y):
            if (ii, i) in d_freqs:
                top.append([x,ii,i,True])
            elif x >= thresh_value:
                top.append([x,ii,i,False])
                  
    return top

#Calculates all of the phase velocities of all files
#all_phases -> a list of 2d numpy arrays of all phase data
#all_amps -> a list of 2d numpy arrays with all amplitudes
#time_delta -> the time change between one array and another
def get_all_velocities(all_phases, all_amps, time_delta):
    
    p_velocities = []

    for i, phase in enumerate(all_phases[1:]):
        p_velocities.append((phase-all_phases[i])/time_delta)

    return p_velocities

#Calculates features at a specific x,y frequency
#time -> the current time to calculate
#x, y -> frequencies to calculate
#amps, phases, velocities -> set of amplitudes, phases and phase velocities for that specific time
#d_freqs -> dominant frequencies that were discovered
def get_data_at_freq(time,x,y,amps,phases,velocities,d_freqs):
    dom = (x,y) in d_freqs
    amp = amps[y][x]
    phases = phases[y][x]
    pv = velocities[y][x]
    if x > 0:
        wave = 1.0/x
    else:
        wave = 1
    aspect = amp/wave
    data = [time,dom,x,y,amp,phases,pv,wave,aspect]
    return data

#Creates a pandas dataframe containing all data for a specific frequency at all times of simulation
#time_step -> the amount of time per data file
#x,y -> frequency that the dataframe is about
#all_amps, all_phases etc -> lists of 2d numpy arrays containing all the data taken from files
#d_freqs -> dominant frequencies
def build_frame(time_step,x,y,all_amps,all_phases,all_velocities,d_freqs):

    stats = []
    total_time = len(all_amps)

    for t in range(1,total_time):
        stats.append(get_data_at_freq(t*time_step,x,y,all_amps[t],all_phases[t],all_velocities[t-1],d_freqs))

    return pd.DataFrame(stats,columns=['Time','Dominant','X','Y','Amplitude','Phase','PhaseVelocity','Wavelength','Amp/Wave'])

#Creates a master dataframe that contains all data frames from all frequencies which have a max amplitude equal or above the threshold
#Also creates a summary dataframe with information about the entire set
def build_all_frames(freqs,time_step,all_amps,all_phases,all_velocities,d_freqs):
    
    frames = []
    summary_data = []
    #Build frames for each x, y frequency 
    for coords in freqs:
        x = coords[0]
        y = coords[1]
        
        frame = build_frame(time_step,x,y,all_amps,all_phases,all_velocities,d_freqs)
        frames.append(frame)
        
        #Use frame to get some more information about this frequency
        avgPV = frame["PhaseVelocity"].mean()
        wave = frame["Wavelength"].iloc(0)
        avgAmp = frame["Amplitude"].mean()
        totalTime = frame["Time"].iloc(-1)
        summary_data.append([totalTime,frame["X"].iloc(0),frame["Y"].iloc(0),wave,avgPV,avgAmp])
    
    summary_frame = pd.DataFrame(summary_data,columns=["Total Time","X","Y","Wavelength","Avg. Phase Velocity","Avg. Amplitude"])

    #Concatenate all frames into single large data frame and return along with summary frame
    return [pd.concat(frames),summary_frame]

#Returns the fft results as a Pandas dataframe 
#timestep -> the current frame/time of the data being passed
#threshold -> the threshold value of data to track when providing the stats
#amps -> 2d array that contains the amplitude results of fft
#phases -> 2d array that contains the phase results of fft
#d_freqs -> a list of the dominant frequencies found among all data
def get_stats(timestep,threshold,amps,phases,d_freqs):

    #get stats for top values
    top_vals = top_values(amps, threshold, d_freqs)

    stats = []

    for i, data in enumerate(top_vals):
        amp = data[0]
        x = data[1]
        y = data[2]
        dom = data[3]
        phase = phases[y][x]
        if x > 0:
            wave = 1.0/x
        else:
            wave = 1
        aspect = amp/wave
        stats.append([timestep,dom,x,y,amp,phase,wave,aspect])
    
    return pd.DataFrame(stats,columns=['Time','Dominant Freq.','X','Y','Amplitude','Phase','Wavelength','Amp/Wave'])

#Returns one large dataframe containing all the results taken from fft analysis of all files in directory
#skip_val -> The amount of timesteps skipped.
#threshold -> the threshold value of data to track when providing the stats
#d_freqs -> a list of the dominant frequencies found among all data
#all_phases -> a list of numpy arrays containing the phase data taken from all the files
#all_amps -> a list of numpy arrays conatining all the amplitude data
def get_all_stats(skip_val, threshold, d_freqs, all_phases, all_amps):
    
    frames = []
    for i, amp in enumerate(all_amps):
        frames.append(get_stats(i*skip_val,threshold,amp,all_phases[i],d_freqs))

    #Create large dataframe, skip first one since its all noise
    master_frame = pd.concat(frames[1:])
    
    return master_frame
    
#Graphs desired data at specific intervals and saves the graph as a png to specified directory, creates a GIF of all images and saves with specified name
#Returns the total number of images produced
#int -> the plot interval, e.g. 10 means every 10th element in the data list will be graphed and saved as png, 0 means no graphing
#dir -> the directory to save the graphs to
#GIF_name -> the full file name (directory + name + .gif) to use when creating the GIF animation
#basename -> the base filename to use, each name will be given a index number to make it unique, e.g "filename{}" -> filename0.png, filename1.png... etc.
#data -> a list of several numpy arrays of 2d data for plotting
#graph_type -> plot type to use, 'surf'->surface, 'wire'->wireframe, 'scat'->scatter, 'cont'->contour
#fig_size -> (optional) size of the figure to plot
#x_label,y_label,z_label -> (optional) labels to use for x,y and z-axis
#title -> (optional) the title to use for plot, note if you have a title like: 'title a {id}' the {id} will be replaced by the index of that data snapshot
def graph_all(interval,dir,GIF_name,basename,data,graph_type,fig_size,x_label,y_label,z_label,title):

    import imageio

    if interval == 0:
        return 0

    count = 0.0
    max = len(data)/interval
    images = []
    for i, d in enumerate(data):
        if i % interval == 0:
            count += 1
            progress = count / max * 100
            sys.stdout.write('\r[{}] {}%'.format('#'*int(progress/5), round(progress,2)))
            sys.stdout.flush()
            fig = plot_data(d,graph_type,fig_size,x_label,y_label,z_label,title.format(id=i))
            fname = dir + basename.format(i)
            save_to_png(fig,fname)
            pl.close()
            images.append(imageio.imread(fname+'.png'))
    
    #Create gif animation from images
    imageio.mimsave(GIF_name,images)

    return len(images)

#Creates a plot of amplitude data and returns the figure
#data -> a numpy array of 2d data for plotting             
#type -> plot type to use, 'surf'->surface, 'wire'->wireframe, 'scat'->scatter, 'cont'->contour
#fig_size -> (optional) size of the figure to plot
#x_label,y_label,z_label -> (optional) labels to use for x,y and z-axis
#title -> (optional) the title to use for plot
def plot_data(data,type='wire',fig_size=(10,10),x_label='x',y_label='y',z_label='Amplitude',title='Graph of FFT2d Amplitude Spectrum'):
    w, l = data.shape
    data_x, data_y = np.meshgrid(np.arange(0,w),np.arange(0,l), indexing='ij')        
    fig = pl.figure(figsize=fig_size)
    ax = fig.add_subplot(111, projection='3d')
    ax.set(xlabel=x_label,ylabel=y_label,zlabel=z_label,title=title)
    if type == 'wire':
        ax.plot_wireframe(data_x,data_y,data)
    elif type == 'surf':
        ax.plot_surface(data_x,data_y,data)
    elif type == 'scat':
        ax.scatter(data_x,data_y,data,s=5)
    elif type == 'cont':
        ax.contour(data_x,data_y,data)
    else:
        ax.plot_wireframe(data_x,data_y,data)

    return fig
    
#Saves the figure as a png image
def save_to_png(figure, fname):
    figure.savefig(fname+'.png',bbox_inches='tight')

#directory -> The directory that holds the log files to analyze
#image_interval -> A graph will be made and saved at every interval. E.g 50 = every 50th data file will be graphed.
#Note: if image interval is set to 0, no graphs are made.
def main(directory="input_data/ALT_DATA1/",output_dir="ALT_DATA1_OUT",output_name="fft_analysis",image_interval=100,base_pref='ALTI',skip_int=5):

    MAIN_DATA_DIR = directory
    SKIP_FILES = skip_int
    PNG_OUTPUT_DIR = output_dir + "png_output/"
    DATA_OUTPUT_DIR = output_dir
    CSV_OUTPUT_NAME = output_name + ".csv"
    GIF_OUTPUT_NAME = output_name + ".gif"
    GRAPH_TYPE = 'surf' #Options available to use, 'surf'->surface, 'wire'->wireframe, 'scat'->scatter, 'cont'->contour
    XLABEL = 'x'
    YLABEL = 'y'
    ZLABEL = 'Amplitude'
    TITLE = 'Graph of FFT2d Amplitudes at t={id}' #id is replaced by index of snapshot
    FIG_SIZE = (10,10)
    SNAPSHOT_INTERVAL = image_interval #A png image of graph is saved at each interval
    BASE_FILE_NAME = "ALTI{:05d}_t0"
    BASE_PREF = base_pref
    THRESHOLD = 0.8
    AMP_THRESHOLD = 1.0
    DATA_TYPE = int
    TIME_DELTA = 10 #Time change between data files

    #Check parent directories exists
    directories = [MAIN_DATA_DIR]
    for d in directories:
        if not os.path.exists(d):
            print("The specified path: {} was not found. Analysis cancelled.".format(d))
            return 1

    #Make directories if needed
    if image_interval > 0 and not os.path.exists(PNG_OUTPUT_DIR):
        os.makedirs(PNG_OUTPUT_DIR)
        
    if not os.path.exists(DATA_OUTPUT_DIR):
        os.makedirs(DATA_OUTPUT_DIR)

    #Get all data from the main directory
    t0 = t.time()
    all_data = read_directory(MAIN_DATA_DIR,BASE_PREF,DATA_TYPE,SKIP_FILES)
    t1 = t.time()

    #Check input files exists
    file_count = len(all_data)
    if file_count == 0:
        print("No files with the prefix: '{}' were found. Analysis cancelled.".format(BASE_PREF))
        return 1
    t_read = t1-t0
    print("\rTotal files read: {} Read time: {}s\nCalculating fft2d data on all files...".format(file_count,t_read))
    
    #Get all fft2d data for calculating
    t0 = t.time()
    all_fft2d = all_fft2d_analysis(all_data)
    t1 = t.time()
    t_fft2d = t1-t0
    print("FFT calculations time: {}s\nCalculating phase data...".format(t_fft2d))

    #Get all phase data
    t0 = t.time()
    all_phase_data = all_phases(all_fft2d)
    t1 = t.time()
    t_phases = t1 - t0
    print("Phases calculation time: {}s\nCalculating amplitudes...".format(t_phases))

    #Get all amplitude data
    t0 = t.time()
    all_amps = all_amplitudes(all_fft2d)
    t1 = t.time()
    t_amps = t1-t0
    print("Amplitude calculation time: {}s\nCalculating phase velocities...".format(t_amps))

    #Get all phase velocities
    t0 = t.time()
    all_velocities = get_all_velocities(all_phase_data, all_amps, TIME_DELTA)
    t1 = t.time()
    t_velocities = t1-t0
    print("Phase Velocity calculation time: {}s\nFinding dominant frequencies...".format(t_velocities))

    #Find dominant frequencies
    t0 = t.time()
    d_freqs = get_dominant_freqs(all_amps,THRESHOLD)
    t1 = t.time()
    t_freqs = t1-t0
    print("{} dominant frequencies found at threshold {}%, time: {}s\nDeriving all data and writing to csv...".format(len(d_freqs),THRESHOLD*100,t_freqs))
    
    #Concatenate and save data results
    t0 = t.time()
    freqs = purge_noise_freqs(all_amps,AMP_THRESHOLD)
    master_frame, summary = build_all_frames(freqs,TIME_DELTA,all_amps,all_phase_data,all_velocities,d_freqs)
    #all_stats = get_all_stats(SKIP_FILES,THRESHOLD,d_freqs,all_phase_data,all_amps)
    #all_stats.to_csv(DATA_OUTPUT_DIR + CSV_OUTPUT_NAME)
    master_frame.to_csv(DATA_OUTPUT_DIR + CSV_OUTPUT_NAME)
    summary.to_csv(DATA_OUTPUT_DIR + CSV_OUTPUT_NAME + "summary")
    t1 = t.time()
    t_stats = t1 - t0

    print("Data calculation and concatenation time: {}".format(t_stats))

    #Graph resulting data at specific intervals and save as images to directory, create GIF of pngs
    if image_interval > 0 and can_plot:

        print("Plotting data at intervals of {} and creating PNG images...".format(t_stats,SNAPSHOT_INTERVAL))
        t0 = t.time()
        im_count = graph_all(SNAPSHOT_INTERVAL,PNG_OUTPUT_DIR,DATA_OUTPUT_DIR+GIF_OUTPUT_NAME,BASE_FILE_NAME,all_amps,'surf',FIG_SIZE,XLABEL,YLABEL,ZLABEL,TITLE)
        t1 = t.time()
        t_plot = t1-t0
        t_total = t_read + t_fft2d + t_phases + t_amps + t_freqs + t_stats + t_plot
        print("\r{} PNG's created in: {}s.\nGIF animation complete.\nAnalysis process complete!\nTotal time: {}s".format(im_count,t_plot,t_total))
    else:
        t_total = t_read + t_fft2d + t_phases + t_amps + t_freqs + t_stats
        print("No PNG images or GIF animation made.\nAnalysis process complete!\nTotal time: {}s".format(t_total))

args = sys.argv

if len(args) > 6:
    main(args[1],args[2],args[3],int(args[4]),args[5],int(args[6]))
elif len(args) > 5:
    main(args[1],args[2],args[3],int(args[4]),args[5])
elif len(args) > 4:
    main(args[1],args[2],args[3],int(args[4]))
elif len(args) > 3:
    main(args[1],args[2],args[3])
elif len(args) > 2:
    main(args[1],args[2])
elif len(args) > 1:
    main(args[1])
else:
    main()
