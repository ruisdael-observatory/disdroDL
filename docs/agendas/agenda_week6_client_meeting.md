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
- Database choice between MySQL and SQLite
    - What are Andre's reasons for wanting the change? We believe it is unnecessary, since the benefits from using MySQL would be in term of performance, but we do not execute complex queries.