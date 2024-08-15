# SEBAL Implementation and Guide for WIT

## Project Overview

This repository contains the guide and code for (py)SEBAL implementation, validation and results display.

### Goals
The primary goal of this project was initially to execute pysebal. For this purpose additional codes to complete the execution requirements was implemented in python (PySEBAL_code) folder. The code now serve as a testbed for all subsequent research utilizing pySEBAL. The repository will host these research work till such individual works are mature to develop their repositories. Current research implementations include:
- Validation of sebal over Indus Basin / LBDC : awaiting closure
- SWF experiment : under progress


## Installation and Setup
To run the models and scripts in this repository, ensure your system meets the following requirements:

### Prerequisites
- Python 3.8 or higher

**1. Clone the Repository**
   ```bash
   git clone https://github.com/LUMS-WIT/SEBAL.git
   cd SEBAL

**2. Install Dependencies using conda**
   ```bash
   # CPU only
   conda env create -f requirements_cpu.yml
   conda activate sebal

**3. Test Run PySEBAL**
   Once all the requirements have been satisfied, we can run PySEBAL code using the test data. The main code file is [Run_py3.py](SEBAL/PySEBAL_dev/SEBAL/Run_py3.py) and test data is located in [test_data](SEBAL/PySEBAL_dev/test_data) folder. If you cloned the repository in *D* drive then it should be *D:\SEBAL\PySEBAL_dev\test_data*. Now Open *Run_py3.py* in your code editor and ensure following:
   '''
   ##### USER INPUTS

   ##### For Linux SET THE PATH TO INPUT EXCEL SHEET #####
   #inputExcel = r"/mnt/d/PySEBAL_dev/test_data/InputEXCEL_v3_3_7_LIN.xlsx"
   ##### For Windows SET THE PATH TO INPUT EXCEL SHEET #####
   inputExcel = r"D:\SEBAL\PySEBAL_dev/test_data/InputEXCEL_v3_3_7_LIN.xlsx"
   st = 2 # starting row number
   en = 2 # ending row number
   '''

   Once done execute the PySEBAL code:
   '''bash
   # Ensure the conda environment is activated
   python Run_py3.py
   '''

   If successfully executed. There would be an *output* folder inside *D:\SEBAL\PySEBAL_dev\test_data*.
   > [!WARNING]
   > If PySEBAL_dev is not in *D:* drive, you need to update the paths in excel sheet for the dataset location.

## Usage

todo: Steps to run the code and any relevant script

## Contributing

todo: Guidelines for how others can contribute to the project

## Citation 

todo: guide to how to cite this work
