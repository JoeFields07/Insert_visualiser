# Insert visualiser
This software provides a simple GUI to visualise tool rake angle, inclination angle, major cutting angle for longitudinal turning of a workpiece.   
This is aimed to provide visual context for tool geometry information often found in research.

# Contact
**Author:** Joseph Fields  
**Contact:** jfields1@sheffield.ac.uk

# Contents
`main.py`: Contains all functionality for defining, visualising and interacting with the simulation.

# Dependencies
Uses Python 3.13.5  
```
pip install numpy matplotlib
```

# Installation Instructions
`git clone https://github.com/JoeFields07/Insert_visualiser`  

# Usage Instructions
The program can be run through the terminal.   
The GUI has sliders to change parameters. Different parts of the visualisation can be hidden/revealed with the buttons.
 Currently, 'C (80° Rhombic)', 'D (55° Rhombic)', 'S (Square)', 'T (Triangle)' ISO inserts are available.   

# License
This code is available under an MIT License, please see the `LICENSE` file for more information.

# Disclaimer
This tool was developed to help my own understanding of tool geometry and therefore may contain mistakes. I would gladly welcome any advice or contributions to this software.

# Future Work
- A better defined coordinate system, perhaps formalising transformations from Machine > Holder > Insert > Cutting edge. 
- Import rake/inclination/major cut geometry from actual tools/holders (likely Sandvik).
- More investigation into Merchant-style modelling, especially for force.
