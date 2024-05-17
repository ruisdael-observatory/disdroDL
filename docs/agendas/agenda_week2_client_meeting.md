# Agenda Week 2 - Client Meeting

## 30-04-2024

## Chairman: Noky Soekarman
## Minutetaker: Mels Lutgerink

- Getting data from the raspberry pi
  - In the last meeting we talked about getting data from the pi using ssh, and we already talked about this meeting being a rubbing duck session. We want to go through the steps one more time to get the data from the pi now that everyone has ssh setup.
- GUI for netCDF that was shown in an earlier meeting
  -	In one of the earlier meetings a GUI was shown to get a visual representation of the data collected from the disdrometer, do we have access to this tool? If so, how do we use it?
- Project plan
  -	Last week we made a project plan, this will be attached to the email. We want to have some feedback on this regarding the project description and if we described everything correctly and did not misinterpret something
- Yaml schema for Thies
  -	In the existing repository, there is a yaml schema defined for the Parsivel sensor. Do we have to create this file ourselves for the Thies sensor, or is such a file already available?
- Forking the repo
  -	As mentioned earlier in the mail, there are still some issues with forking the repository, are these problems solvable or do we have to settle for just copying the existing files? To reiterate, the current problem is that our TA cannot fork the repository even since she was added as a maintainer to the project.

# Minutes

- Repo
	- Fork existing DisdroDL repository 
	- **Dont** want deep copy of existing repository
	- Later merge back into disdroDL repository

- discuss project plan
	- we mention that the requirements for the project are not extensive
	- project plan can be extended with more concrete steps
	- we need to look at the past/existing Software Project to get a better understanding of what. why and how
	
- challenge
	- experiment with raspberryPi 
	- start disdroDl main.py
    - export NetCDFs for 2024.04.29 and 2024.04.28

- discuss existing software
	- Rubber ducking
	- important classes can be found in the modules folder