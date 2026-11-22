# Contribution guidelines
## License
UsagiBot is licensed under the GNU AGPL 3.0 license. As such, all contributions must be made under the same license or a compatible license. By making a contribution to this repository, you agree that your contribution may be used under the terms of the AGPL 3.0 and you assert that you are legally able to do so.

**Preference**: Either put your contribution(s) under AGPL itself, or a permissive license that allows it to be included under the AGPL (such as MIT or Apache).

## AI-generated Code
AI-generated code is forbidden from this project given the many issues it presents ethically and legally. In the view of the developers of this project AI models must comply with the licenses of the code they are trained on, and any model currently out there is almost certainly trained on enough conflicting licenses to make it poisonous.

By submitting a contribution to this repository, you certify that none of the code in your contribution was created using an LLM or any other form of AI.

## General Code Guidelines
- Due to this being ran on a Raspberry Pi, we prefer to not use libraries outside of the Python Standard Library and the dependencies of Discord.Py as much as possible
  - As such, helper functions are encouraged because they can be shipped with the bot
  - This can cut down on the dependency list considerably, making it easier for the little Pi to handle
- As stated above, this bot runs on an old Raspberry Pi
  - The CPU has a single core and around one Gigahertz of frequency
    - The CPU is also on a legacy ARM architecture
  - There is around half a gigabyte of RAM available
  - In general, be mindful of the hardware being used
- Helper functions should go in the helper functions file, not the main.py
- We use camelCase for most variable names, and screaming snake case for constants and similar global variables
