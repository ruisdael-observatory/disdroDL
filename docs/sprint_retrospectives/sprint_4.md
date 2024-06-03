# Sprint Retrospective

## Group: 007D
## Iteration: 4

## Tasks:

| User Story | Task  | Assignee | Time Estimated | Time Spent | Done (Yes/No) | Notes                                                                                                                                                                             |
|------------|-------|----------|----------------|------------|---------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| #29        | #77   | Mels    | 5H             | 7H         | Yes           |      Finally got this to work, still took longer than expected, see notes for the general issues with .csv's and .txt's               |
| #29        | #78   | Mels    | 6H             | 8H         | No            | This was also harder than expected, do expect to finish it next sprint though |                                                                                                                                                                                   |
| #29        | #79   | Mels      | 6H             | 0H         | No           | Didn't get to it due to previous issues |                                                                                                                                                                                   |
| #57        | #82   | Vasil    | 16h | 2h | Yes | Was much easier than expected                                                                                                                                                                                  |
| #57        | #85   | Jesse    | 6h             | 3h         | Yes           | The time estimate was quite high since setting up the boilerplate code for a project was something completely new, but didn't end up taking that long                             |
| #57        | #87   | Jesse    | 2h             | 1.5h       | Yes           |                                                                                                                                                                                   |
| #63        | #64   | Ella     | 1h 20min       | 30min      | no            | still needs to be finished, focused more on the code in this sprint                                                                                                               |
| #63        | #65   | Noky     | 1h             | 1h         | Yes           |                                                                                                                                                                                   |
| ---        | #62   | Ella     | 1h             | 30min      | mostly        | Discussing with client how to change configuration file                                                                                                                           |
| ---        | #68   | Noky     | 3h             | 6h         | Yes           | This issue had some problems after more than a day of running, also the integration with parsivel wasn't fully working anymore. That is why there was way more time spent on this |
| ---        | #69   | Ella     | 6h             | 6h         | almost        | Client gave detailed list of desired changes, over 90% of changes implemented ,some mostly cosmetic ones still need to be discussed with the client                               |
| ---        | #73   | Noky     | 12h            | 13h        | Yes           | Testing the main loop was a bit difficult since it contains a while True loop                                                                                                     |
| ---        | #80   | Ella     | 1h             | 6h         | yes           | Restructuring thies telegram processing to match the way it is done for parsivel telegrams took longer than expected due to small errors/inconsistencies and merged changes.      |
| ---        | #81   | Ella     | 7h             | 4h         | yes           | After reworking code base for previous testing and getting the hang of pytest fixtures done quicker then expected                                                                 |
| ---        | #83   | Ella     | 7h             | 12h 30min  | yes           | Took longer due to newly implemented pytest fixtures and strong code coupling + some issues wrong implementation within the codebase that the testing discovered                  |
| ---        | #89   | Jesse    | 3h             | 4.5h       | Yes           | Went a bit over the estimated time because of some issues with getting test databases for the Thies to work                                                                       |                                                                                                      |
| ---        | #90   | Ella+Noky | 1h             | 20min      | yes           | was and eassy fix once the telegram class was refactored, some code still will need to be deleted after merging                                                                   |
| ---        | #92   | Noky     | 1h             | 1h         | Yes           |                                                                                                                                                                                   |
| ---        | #93   | Jesse    | 3h             | 3h         | Yes           |                                                                                                                                                                                   |
| ---        | #102  | Vasil    | 7h | 8h | Yes | Figuring out some details before starting to code takes some time, and hence this issue is more time consuming.                                                                                                                                                                                  |

## Main Problems Encountered

- Many of the issues involved parts that are new to the person doing them. Therefore, issue time estimation was a bit off.
- Because of the previous point some issues ended up taking much more time.
- Parsing old .csv's and .txt's are still difficult, since there is little consistency in naming conventions and the way the data is logged in the respective files. For example, the telegram data is stored in a massive string, making no distinction between single data values and list's of data values.
- This week has been quite busy with meeting and presentations. Therefore, we all couldn't spend that much time actually coding.