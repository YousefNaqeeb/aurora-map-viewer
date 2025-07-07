
# Aurora map viewer
A tool to help visually impaired players play aurora 4x c#.
## Installation
To install aurora map viewer, unzip the zip file from the releases section into your directory with the file called auroraDB.db this should be where you would normally play aurora.
After running for the first time, it will also create a file called settings.json, which will contain filter settings.
## Features and explanations
### View list
View list this lists all of the things in the system, similar to the f9 menu, but it includes objects that are shown only on the tactical map, such as survey points, fleets, and colonies.
### Filters
Edit filter settings and apply filters let you customize what you want to see in the list, such as hiding objects like jump points or survey points.
### Pinned items
Pin item takes you to a search where you can find what you would like to pin, which will then be used to sort or check distance to a specific item, this is so you can get a better idea of where something is in the system in relation to  the other objects in the system.
### Mineral search
Mineral search works similarly to how it does in game.
You enter first the mineral you are looking for, then the amount, and lastly the access level
For example:
```
duranium 250000 0
Neutronium 38320 0.5
tritanium 125000 1
```
Case doesn’t matter for mineral names
The search will return the bodies that have the greatest amount of minerals you wanted when added together, as long as they meet all the requirements such as accessibility for each mineral.

