# BIG-FC-Code
The BeagleBone and TLC code for NASA's 2020 BIG Idea Challenge, Penn State team.



## dummy_rover.py

The `dummy_rover.py` script will open up two TCP ports and listen on them. The "Rover" TCP port is `654` and the "TLC" TCP port is "321". Run this script before running the main program with dummy serial mode enabled.
The script will also generate a randomized TLC datastream (serial from TLC to the BBB) for testing the parsing of the datastream and reporting thermal status.
