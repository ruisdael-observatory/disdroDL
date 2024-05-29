# Sprint Retrospective

## Group: 007D
## Iteration: 2

## Tasks:

| User Story | Task | Assignee | Time Estimated | Time Spent | Done (Yes/No) | Notes                                                                                                                                                                                                                      |
|------------|------|----------|----------------|------------|---------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| ---        | #1   | Ella     | 15min          | 15m        | Yes           | Because Mels was ill, Ella took over this issue                                                                                                                                                                            |
| #26        | #21  | Mels     | --             | 2.5h       | Yes           |                                                                                                                                                                                                                            |
| #26        | #25  | Noky     | --             | 10h        | Yes           | Mocking took some more time since I didn't use mocking in python before                                                                                                                                                    |
| #26        | #49  | Vasil    | 5h             | ???        | Yes           |                                                                                                                                                                                                                            |
| #26        | #53  | Vasil    | 3h             | ???        | Yes           |                                                                                                                                                                                                                            |
| #26        | #54  | Vasil    | --             |            | Yes           |                                                                                                                                                                                                                            |
| #27        | #24  | Jesse    | --             | 6h         | Yes           | Finished but not merged yet since that it will be part of a bigger MR when the full user story has a functioning prototype                                                                                                 |
| #27        | #52  | Ella     | 1h             | 1h         | Yes           |                                                                                                                                                                                                                            |
| #27        | #58  | Ella     | 5h             | 4h         | Yes           | Some of the already existing code can be used to help create a NetCDF using the configuration files, a lot of things do need to change for the NetCDF to be able to read all the variables for the Thies and populate them |
| #27        | #59  | Ella     | 32h            | 17h        | No            | Achieved progress, NetCDFs are structured the right way with the variables from the configuration files, but still can't populate them with values                                                                         |
| #28        | #55  | Jesse    | 2h             | 3.5h       | Yes           | Got stuck for a bit because something was copy pasted wrong, but was overall relatively simple                                                                                                                             |

## Main Problems Encountered

- For exporting NetCDFs the main issue is that we want to extend already existing software and not re-invent the wheel. Unfortunately the existing software is not documented that well, variables have unclear or similar names and the code is strongly coupled. We assume that this will be/know it already was/is an issue for other parts of the project as well. 
- Another issue is that code libraries that were used are quite specific and the manuals for the disdrometers are vague.


- Mitigation: We will aim to fix these issues by commenting/documenting the code well before handover and by making the code more modular (at least our part/still have to discuss in the future if we want to refactor the already existing code base and to what degree).