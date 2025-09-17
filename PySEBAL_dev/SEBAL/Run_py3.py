# -*- coding: utf-8 -*-
"""
Created on 03 Dec 2019

@author: tih, sajid pareeth
"""
import pysebal_py3
import traceback
from datetime import datetime
startTime = datetime.now()
##### USER INPUTS

##### For Linux SET THE PATH TO INPUT EXCEL SHEET #####
#inputExcel = r"/mnt/d/PySEBAL_dev/test_data/InputEXCEL_v3_3_7_LIN.xlsx"
##### For Windows SET THE PATH TO INPUT EXCEL SHEET #####
# inputExcel = r"D:\SEBAL\PySEBAL_dev\docs\InputEXCEL_swf_modis_rabi_2023.xlsx"
# inputExcel = r"D:\SEBAL\PySEBAL_dev\docs\InputEXCEL_swf_modis_rabi_2023.xlsx"

inputExcel = r"D:\SEBAL\PySEBAL_dev\docs\InputEXCEL_LBDC_149039.xlsx"
# inputExcel = r"D:\SEBAL\PySEBAL_dev\docs\InputEXCEL_LBDC_150039.xlsx"

# inputExcel = r"D:\SEBAL\PySEBAL_dev\docs\InputEXCEL_calibrations_RIs.xlsx"
# inputExcel = r"D:\SEBAL\PySEBAL_dev\docs\InputEXCEL_calibrations_Rms.xlsx"
# inputExcel = r"D:\SEBAL\PySEBAL_dev\docs\InputEXCEL_calibrations_Rwf.xlsx"
# inputExcel = r"D:\SEBAL\PySEBAL_dev\docs\InputEXCEL_calibrations_Src.xlsx"
st = 2 # starting row number
en = 97 # ending row number

####### USER INPUTS FINISH HERE

print ('\n--------------------\n')
print('Total number of lines to run:', (en - st + 1))
print('Input Excel:', "149039")
print ('\n--------------------\n')
for number in range(st, en + 1):
    try:
        startTime_line = datetime.now()
        print ('starting line num: %d' % number)
        pysebal_py3.SEBALcode(number,inputExcel)
        print ('--------------------\n')
        print ('line num: %d done' % number)
        print('Time taken by this line :',datetime.now() - startTime_line)   
    except:  # amir
        print ('--------------------\n')
        print ('SEBAL did not run line %d fully' % number)
        print ('\n******* ERROR *******\n')
        traceback.print_exc()
        
        print ('\n--------------------\n')
print ('--------------------\n')
print('\n Total Execution time :',datetime.now() - startTime)
print ('--------------------\n') 