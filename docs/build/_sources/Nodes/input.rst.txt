Input
===================

Import Data
#####################

Imports EEG data into the system to be manipulated by the user

Attributes
-----------

+------------------------------------------------------------------------------+
|                                  Output                                      |
+----------+----------+--------------------------------------------------------+
| **Name** | **Type** | **Description**                                        |
+----------+----------+--------------------------------------------------------+
| Raw      | rawEEG   | Contains the channel data for the EEG dataset          |
+----------+----------+--------------------------------------------------------+
| Events   | events   | Contains the event times and types for the EEG dataset |
+----------+----------+--------------------------------------------------------+

Settings Interface
---------------------

.. image:: ../Images/Nodes/ImportData.png
    :width: 700
    :align: center

BDF Files
***********

+-------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **Setting** | **Description**                                                                                                                                                                                            |
+-------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Event Mask  | The binary mask that isolates the signal data from the event information in the BDF file. Default can be left as 255 to use the first 2 bytes of the data for the signal and the 3rd as the event carrier. |
+-------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

Numpy Files
*************

+---------------+---------------------------------------------------------------------------------------------------------+
| **Setting**   | **Description**                                                                                         |
+---------------+---------------------------------------------------------------------------------------------------------+
| Channel Types | A text file that contains the type (eeg/eog/ecg) of each channel of the data as a comma seperated list. |
+---------------+---------------------------------------------------------------------------------------------------------+
| Sample Freq   | The sample frequency of the data in Hz                                                                  |
+---------------+---------------------------------------------------------------------------------------------------------+

Import Epochs
###############

Imports a single epoch file. Multiple file input similar to the Import Data node is in development

Attributes
-----------

+-----------------------------------------------------+
| Output                                              |
+------------+----------+-----------------------------+
| **Name**   | **Type** | **Description**             |
+------------+----------+-----------------------------+
| Epoch Data | epoch    | Epoch data loaded from file |
+------------+----------+-----------------------------+

Settings Interface
---------------------

.. image:: ../Images/Nodes/ImportEpochs.png
    :width: 400
    :align: center
    
Import Evoked
###############

Imports a single evoked file. Multiple file input similar to the Import Data node is in development

Attributes
-----------

+------------------------------------------------------+
| Output                                               |
+------------+----------+------------------------------+
| **Name**   | **Type** | **Description**              |
+------------+----------+------------------------------+
| Epoch Data | evoked   | Evoked data loaded from file |
+------------+----------+------------------------------+

Settings Interface
---------------------

See `Import Epochs`_

Import ICA
###############

Imports a single ICA solution. Multiple file input similar to the Import Data node is in development

Attributes
-----------

+--------------------------------------------------------+
| Output                                                 |
+--------------+----------+------------------------------+
| **Name**     | **Type** | **Description**              |
+--------------+----------+------------------------------+
| ICA Solution | ICA      | ICA solution loaded from file|
+--------------+----------+------------------------------+

Settings Interface
---------------------

See `Import Epochs`_