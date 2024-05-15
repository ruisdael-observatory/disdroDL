# Agenda Week 4 - Client Meeting

## 14-05-2024

## Chairman: Jesse Vleeschdraager
## Minutetaker: Vasil Chirov

### Approval of the agenda
- summary of agenda points
    - update on progress
    - plan for this week
    - SQLite vs mySQL
    - .yml file
    - contact via gitlab
    - midterm meeting

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
- coding language for auxiliary quality control and GUI software
    - would you prefer us to use a specific coding language for those pieces of software?


# Minutes

- update on progress so far
    - updated them on problem with thies throwing an error, abstract class idea, start and end flag bytes problem
    - currently an old script is used for the thies
- plan for this week
    - we want to have a prototype (working for both sensors) this week, and finish the testing next week
    - we want to create a sensor class with subclasses
- should we rework the database from SQLite to mySQL?
    - Andre's idea, Marc has no clear reason
    - Probably functionalities that MySQL offers, and SQLite doesn't
    - We can leave the question for next week when Andre is here
- what should the .yml file for the Thies include?
    - 82-519 fields are missing, but this is the most important information
    - The parsivel does log it
    - In the netCDF it should be converted to a matrix
    - We could be able to specify which fields we want
- contact via gitlab
    - Make an issue and tag them in the description
    - Tag Andre for samller code related questions, and Marc for bigger project questions
- midterm meeting date
    - 28-05-2024 at 2pm
    - scrap the regular meeting plan
- coding language for auxiliary quality control and GUI software
    - Marc doesn't really like Java, he would prefer to see Python
    - it is also a much better choice for this field
    - some people working with R
    - python would be also better for potential future studying purposes.
    - for python try not to use many external dependencies (only use the most common ones)
- other
    - could be useful to have a schematic view of the dataflow, class structure etc. in the README
    - we can still readjust the requirements or some other things about the project if needed
    - don't hesitate to justify our choices
    - send the new requirements to Marc and Andre by email (the overlief link)   