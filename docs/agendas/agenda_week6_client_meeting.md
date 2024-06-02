# Agenda Week 6 - Client Meeting

## 28-05-2024

## Chairman: Vasil Chirov
## Minute taker: Jesse Vleeschdraager

### Discussion points
- Quality control
    - How would you like to have the final **report**? Currently the project report is focused only on disdroDL. Would you like a seperate report for QC, add it as an appendix, have it as a chapter in the current report or something else?
    - Could we get some structure proposal?
- CSV parsing
    - Do we know in what format the data is stored as for the Parsivel? There are some inconsistencies between files - some have (date) | (timestamp) | (telegram as string), while others have just a table with key-value pairs.
    - There is something wrong with the example telegram for the Parsivel (does not match with the manual).
    - Do you want to have it done for the Thies or for the Parsivel first?
- Database choice between MySQL and SQLite
    - What are Andre's reasons for wanting the change? We believe it is unnecessary, since the benefits from using MySQL would be in term of performance, but we do not execute complex queries.

### Notes
- Quality Control
    - Report
        - already discussed at end of midterm meeting, they don't care
    - Structure proposal
        - python library since it's not much about hardware limitations
        - investigate how to publish to IPI(?)

- CSV parsing
    - 3 columns: date - timestamp - everything else. misses keys (not key:value)
    - Cabauw 20220701 example of shitty csv
    - field 61 is all particles of the moment (tuple of lists)
    - incorporating field 61 would give a lot of points
    - Andre will go back through history of code and ask colleagues (remind Andre about it)
    - csv was formed by making one requests where all fields are written down in sequence
    - parsing thies csv should be easier
    - the difficult part will be testing
    - example telegram doesn't match up? Andre: can be fishy because of different ways of asking for Telegrams
    - look through history of commits for Andre's work on it
    - parsivel and thies should be separated
    - try using the config files
    - Andre prefers parsing csv separated from pi if we use new dependencies
    - maybe use a separate requirements.txt for if you want to do this
    - running recursive script over folders with csv files would be a good way to do it
    - make sure to document what way we do it
    - tool csvtk

- Database choice between SQLite and MySQL
    - keep it at SQLite

- Specific values in config files
    - Mark sent feedback, when it's done just ask again in that issue
