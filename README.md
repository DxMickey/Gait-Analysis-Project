# Andrii_B_MSc_Python_Code
Python code from TalTech MSc Andrii Boryshkevych

-----------------------------------------------------------------------AndriiMSc_Number_of_Peaks.py--------------------------------------------------------------------

This piece of code was specifically used to calculate the number of peaks that were occuring at single gait event area. This phenomena can be clearly seen in the Figure 4.3 in the Thesis work.

The code requires as an input direcotry with excel files, line 13 in the code.
Then, at line 29 one should specify location to be analysed.

The Threshold for peaks identification is specified automatically based on the studied location, see lines 31 - 36.
Function _Peaks_ helps to identify the region of interest, in the case of this thesis it was 7 gait events.
Later with fucntion _Cut_ this region of interst is specified, function takes as an input 3 parameters: i - analysed dataset, start - beginning of the region of interest, end - end of the region of interest.
Later to see the outcome function _NewPeaks_ should be evoked, and its output is the chopped pieces of filtered and unfiltered data with outlined number of peaks in each of them.

There are additional functions in the code, such as: Plot, DefineArray and ActualLength that were used for different purposes during data analysis process, but for the final version of the code they are not required.

**NB!IMPORTANT**
Note that the code is built in a way that excel files are to be improted fo analysis. Initially sensor's data is avaliable as .txt file and has to be transferred to excel first. Once imported to excel, dataset has 13 columns each representing the specific measurement from the build in into device sensors. First thing that has to be done is to add 1 additional column that should be put before column that represents the time stamps (column A in excel). Then in the first new column time stamps have to be converted into seconds, to do that use the following equiation: "B1/1000-$B$1/1000". Next the TOTAL ACCELERATION or MAGNITUDE OF THE ACCELERATION VECTOR has to be calculated (see formula 3.2 in the thesis text). The following equation has to be inserted to the column O in Excel (15th column): "SQRT((F1^2)+(G1^2)+(H1^2))". Once these two steps are done excel file is ready to be imported and processed with the code. The whole procedure is also explained in the thesis text in section "Pilot study 1".

-----------------------------------------------------------------------------------------------------------------------------------------------------------------------

-----------------------------------------------------------------------AndriiMSc_Phase_Shift_Solver.py-----------------------------------------------------------------

This piece of code was used in order to find optimal parameters for S-G filter. Results of utilization of this code are presented in section 4.3 of the thesis.
Basically, increase in the window length of the filter causes the peak shift from the initial peak(in the raw data).

The code requires as an input direcotry with excel files, line 36 in the code.
Then, at line 98 and 99 one should specify location and subject to be analysed.
At lines 39 - 94 S-G filters with different window lengths are defined.
Then files are imported by the principle, identical to the first code (see **NB!Importnat**).

Then all datasets from current location are printed.
Since only first gait event was the region of interest for this study, function _Peaks_ was introduced. It asks for 3 inputs: i - analysed dataset, start - beginning of the region of interest, end - end of the region of interest. FOR THIS STUDY REGION OF INTEREST ENDS WITH THE FIRST GAIT EVENT

The outcome of the Peaks function is the distance between the HIGHEST peak the original data and the HIGHEST peak in the filtered data.
Functions ShiftCheck and SingleGraph were added as a tool to simplify the process of introducing limits to the Peaks function. To see the results of calcutaion command "all_results" should be used.

-----------------------------------------------------------------------------------------------------------------------------------------------------------------------

-----------------------------------------------------------------------AndriiMSc_General_Motif.py-----------------------------------------------------------------

This piece of code was used in order to check the efficiency of General Motif approach. The idea of this apporach is covered in section 3.4 (specfically - Novel gait analysis data processing). Results are discussed in section 4.4 of the thesis.

Code is splitted into two main parts: Specifying General Motif and General Motif Matrix Profiling

1. Specifying General Motif

The code requires as an input direcotry with excel files, line 16 in the code.
Then, at line 36 one should specify location.
Once limits of the General Motif are known, one can specify them using varibale "gaitCyclePattern". Examples for each sensor location can be found on line 58 - 62.

2. General Motif Matrix Profiling

The code requires as an input direcotry with excel files, line 81 in the code.
Then, at line 84 one should specify location. Name was defined based on the analysed file.
Then files are imported by the principle, identical to the first code (see **NB!Importnat**).
The Threshold for peaks identification is specified automatically based on the studied location, see lines 97 - 101.

Once everything is specified and code is executed, as an outcome appears a graph with filtered data marked as blue and identified motif overlayed over it in orange. An array with peaks identified in the found Motif is also printed above the graph. An example can be found in Figure 3.16 in the thesis text.


-----------------------------------------------------------------------------------------------------------------------------------------------------------------------

-----------------------------------------------------------------------AndriiMSc_Subject-Based_Motif.py----------------------------------------------------------------

This piece of code was used in order to check the efficiency of Subject-Based Motif approach. The idea of this apporach is covered in section 3.4 (specfically - Novel gait analysis data processing). Results are discussed in section 4.4 of the thesis.

Code is splitted into two main parts: Specifying Subject-Based Motif and Subject-Based Motif Matrix Profiling

1. Specifying Subject-Based Motif

The code requires as an input direcotry with excel files, line 16 in the code.
Then, at line 35 one should specify location.
Then files are imported by the principle, identical to the first code (see **NB!Importnat**).
The Threshold for peaks identification is specified automatically based on the studied location, see lines 57 - 63.

The _Ref_Peaks_ function plots the first dataset from the specified directory, along with the peaks identified in this dataset.
Once done, Motif is defined (lines 82 - 95). For that an input from the user is asked (time stamps of the first and last gait event from the region of interest). Then 20 cs are added to the both start and end point of the motif. This was done to extend slightly the region of interest, because otherwise, often eaither first or last peak was missed by the algorithm.

2. Subject-Based Motif Matrix Profiling

The rest of the code is executed automatically. Comments in the code will help to understand the conesuent specific steps. The outcome of the execution is identical to the General Motif approach shown in Figure 3.16 in the thesis text. 

-----------------------------------------------------------------------------------------------------------------------------------------------------------------------
