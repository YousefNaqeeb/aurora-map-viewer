# Aurora Map Viewer

A tool to help visually impaired players play Aurora 4X C#.

## Installation

To install Aurora Map Viewer, unzip the zip file from the releases section into your directory with the file called `auroraDB.db`. This should be where you would normally play Aurora.

After running for the first time, it will also create a file called `settings.json`, which will contain filter settings.

If updating you may have to delete the old settings.json file for it to work correctly.

## Features and Explanations

### View List

View List displays all of the things in the system, similar to the F9 menu, but it includes objects that are shown only on the tactical map, such as survey points, fleets, and colonies. From this menu, you can also pin items to sort the list from them, and copy the list, which will quietly dd it to your clipboard.

### Filters

Edit filter settings and apply filters let you customize what you want to see in the list, such as hiding objects like jump points or survey points.

### Mineral Search

Mineral Search will find all surveyed bodies with the resource you are looking for, with greater than or equal to accessibility. The minimum amount you must have in the amount spin control to search fora given mineral is 1.