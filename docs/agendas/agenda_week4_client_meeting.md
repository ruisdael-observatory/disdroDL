# Agenda Week 4 - Client Meeting

## 14-05-2024

## Chairman: Jesse Vleeschdraager
## Minutetaker: Vasil Chirov

### Approval of the agenda
- summary of agenda points
    - SQLite vs mySQL
    - .yml file

### Discussion points:
- update on progress so far
    - refactored previously existing code
    - small framework for dynamically choosing what general .yml config file to use based on the specific .yml site config file
    - serial connection with Thies
- plan for this week
    - finish a prototype for logging and exporting
    - making a structure with a sensor class with subclasses for specific sensor types
- should we rework the database from SQLite to mySQL?
    - mySQL seems to be more for bigger databases, while this one only is ~700 MB and doesn't have difficult querying
    - table can still be updated / reworked, but what reasons are there to move to mySQL?
- what should the .yml file for the Thies include?
    - we found a .yml file from ruisdael/thiesDL, is that still being used? is it okay to use that .yml file? 
    - features 82-519 is a carthesian product of drop size and velocity, which are missing, are these important? in general, what data do you want?
- contact via gitlab
    - how should we exactly contact you via gitlab? make an issue and assign, or something else?
- midterm meeting date
    - confirmation for the date (Tuesday May 28 14:00)
    - do we then also meet in week 6 (there's a meeting planned for that day at 10:00)

### Any other business
    - 
