EEG Toolkit for WARIO
=======================================

A set of nodes for use in the `WARIO pipeline development suite <https://github.com/McMasterRS/WARIO>`_ that use the MNE python library to perform analysis on EEG related data.

Usage
========================================
Pipelines using this toolkit can be built through the use of the WARIO Editor (see below). 

For more a more detailed guide see `the user guide <user.html>`_

Installation
========================================    

1. Download the `WARIO Editor <https://github.com/McMasterRS/WARIO-Editor>`_
2. Install the WARIO backend library by using :code:`pip install wario`
3. Download the EEG Toolkit
4. Add the EEG Toolkit to the WARIO Editor (see WARIO Editor tutorial)

.. toctree::
    :hidden:
    
    user
    
.. toctree::
    :hidden:
    :caption: Nodes
    
    Nodes/input
    Nodes/processing
    Nodes/output
    Nodes/plotting