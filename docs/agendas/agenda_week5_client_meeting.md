
# Agenda Client Meeting 21/05/24
## Chairman: Mels
## Minutetaker: Noky
- Can Marc and Andre see the code?
  - Yes
- Give demo/explain what is done (5 minutes)
  - Add name to contributers in netcdf file
  - Missing license in netcdf, creative commons
  - Missing field for software that produced the file
- Discuss specifics quality control (20-30 minutes)
  - The OS should run on Linux, windows is optional
  - Runs as a service on a server
  - Throw error if qc fails
  - Netcdf from any sensor, focus on parsivel and thies
  - QC in airflow
  - Python library
  - Config file with expected values
  - Generate log with error, warning, info
  - edit netcdf history that indicates that qc was done
  - store output of qc somewhere
  - Proposal for structure
  - Find existing pieces of software that are comparable
- Discuss upcoming sprint (8 minutes)
  - Mornings would be best
  - Not thursday afternoon
- Final presentation date
- Other issues

csv parsing
parsivel has data in txt and csv
csv --> NetCDF (Start with Thies, then Parsivel)


determine software version

create issue with generated thies netcdf file, and specify location of yml

are key value pairs already there for parsivel?

check how telegram should be stored in db, raw or pre processed

avoid sleeps whenever we can