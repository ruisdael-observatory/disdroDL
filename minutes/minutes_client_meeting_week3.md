# Client meeting week 3
## New requirements
- Data quality control can be expended
	- SEPARATE PIECE OF SOFTWARE FROM THE MAIN LOGGER
    - Integrity of the files 
	- Consistency of the data
	- Validating file structure
	- Some checksums
	- File size
	- Consistency of the dimensions (descriptions in the netcdf file)
	- Variable integrity check, all if the variables have the right types
	- All the variables have the correct attributes (names)
	- Min max bounds of the stored/incoming data
	- If the correlations between the variables is correct
	- All of this should only be done on netcdf files, so first log the data as is
	- Make quality control for netcdf not specific to one sensor, have a config file for a sensor on which tests to run

- Should have
	- Parsing of previous data (ie data in csv format)
	- Different parsers of different types of data (csv, txt)

- GUI
	- Should be a separate part from the main logger
    - Maybe have a GUI for installing the software on the pi

## Other notes

- First should can be more specific
- Test it as well as possible, no fixed number for coverage
- Code metrics can also be taken into account when assessing code quality
- In a deployed situation, there is one sensor connected to one raspberry pi