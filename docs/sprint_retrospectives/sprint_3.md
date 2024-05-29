# Sprint Retrospective

## Group: 007D
## Iteration: 3

## Tasks:

| User Story | Task | Assignee | Time Estimated | Time Spent | Done (Yes/No) | Notes                                                                                                                                                  |
|------------|------|----------|----------------|------------|---------------|--------------------------------------------------------------------------------------------------------------------------------------------------------|
| #29        | #29  | Mels     | 6h             | 12h        | No            |                                                                                                                                                        |
| #32        | #57  | Mels     | 3h             | 0h         | No            |                                                                                                                                                        |
| #27        | #59  | Ella     | 15h            | 17h 30min  | Yes           | Exports NetCDF correctly, some changes regarding naming of varaibles and which values are included will likely still be changed after input from client |
| ---        | #62  | Ella     | 1h             | 30min      | no            | Issue for communication                                                                                                                                |
| #63*       | #64  | Ella     | 1h             | 30min      | no            | Have to disscus with group how twe want the wiki to look, we want the whole project documented well for handover                                       |
| #63*       | #65  | Noky     |                |            |               |                                                                                                                                                        |
| #63*       | #66  | Jesse    | 15m            | 15m        | Yes           |                                                                                                                                                        |
| ---        | #67  | Vasil    |                |            |               |                                                                                                                                                        |
| ---        | #68  | Noky     |                |            |               |                                                                                                                                                        |
| ---        | #69  | Ella     | 6 h            | 30 mins    | No            |                                                                                                                                                        |
| #70*       | #71  | Jesse    | ---            | 3h         | Yes           |                                                                                                                                                        |
| #70*       | #72  | Vasil    | 6h             | 7h         | Yes           |                                                                                                                                                        |
| #70*       | #73  | ---      | ---            | ---        | No            | This issue is still blocked                                                                                                                            |

## Notes
- *these are not actual user stories, but they are still split up in smaller issues

## Main Problems Encountered

- The main issue we ran into was that there was a lot of unexpected work with fixing bugs and improving documentation of the code, leaving a lot less time for the issues we intended to do in this sprint.
- In general the strong coupling and lack of clarity of the already existing code base still caused a few issues.
- #29 caused a lot of problems. Exporting from csv to netCDF was more difficult than expected due to the csv's that are stored in different formats. The value's from e.g. Parsivel are stored without keys in some files while the telegram that is originally sent out does have corresponding keys.
- Due to not being able to finish #29, Mels didn't start on #32.
