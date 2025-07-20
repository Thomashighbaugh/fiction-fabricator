# Project To-Do List

My rough list and attempt to keep some order and sanity in my work on this project moving forward. Using special highlighting and todo tracking via GitHub issues and Neovim plugins that _hopefully_ will prompt me to refer back to this list and keep it updated.

## Of Immediate Concern

These are items I am intending to get to sooner rather than later, this list will guide subsequent commits I make to the project repo directly.

- [ ] TODO debug cycle by using project to create at least 3 books and catch any errors during that process.
  - [x] DONE Book 1: Still too short, need to break the scene generation into smaller chunks
  - [x] DONE Book 2: Still too short, cut off in critique phase and cut offs in the beginning contextual generation, which have been fixed and the generation cycle is now more iterative. Still getting more errors than I would like from the word count minimum checks but we will see how it goes.
- [ ] TODO Create a tool to write short stories using the project's infrastructure, using the same prompt as a novel but with a shorter length
- [ ] TODO Create a unified menu the user can use to select if they want to generate a book, short story, generate ideas or generate a novel prompt

- [ ] TODO create a tool to write individual chapters for a web based lightnovel or CYOA style story

## Intended in Future

These are not pressing needs, but medium to long term mile markers along the project roadmap (**_pull requests always welcome_**).

- [ ] TODO means of picking back up from an uncompleted generation attempt
- [ ] TODO failover for when API calls exceed rate limits (because I do use the free tier of course, I am poor)

## Archive

These are items that have been completed, obviously. Kept here for posterity and as a means of seeing how much progress has been made trekking towards that horizon of feature-completeness.

- [x] DONE rebase on original project, refactoring while preserving more of original functionality
- [x] DONE integrate Nvidia NIM endpoints efficiently
- [x] DONE Integrating at least some of the Github Models using the means provided on the model playground pages _vis-a-vis_ GitHub Models
- [x] DONE timeout for generations, preventing hanging calls from compromising generation pipeline
- [x] DONE Create tool to generate the ideas to feed into `Tools/PromptGeneration.py`
- [x] DONE create documentation for the project and link to it on the README.md
