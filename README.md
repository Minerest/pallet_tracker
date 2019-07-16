# Pallet Tracker
## Warehouse App for the Company, Essendant.


### The Why's
This is a tool that is supposed to be utilized by the Bulk Picking team and the Shipping Team.
The problem we encounter is that we are not tracking who's responsible to pick which items. When labels for items are lost, there is no accountability as to who lost them.

Another issue we are having is that no body knows who has which item at a certain time, so if a truck is about to leave and the item hasn't hit the floor, often times, the shippers would ask a random associate to grab what they're missing leading to the same item being picked twice, inventory issues, and the item being shipped twice.
  
The shipping team also has the issue of not having all the data available in one place. Currently, they use up to 4 different websites to do their job which leads to an inefficient workforce. If the shipping team knows that their items are currently being picked by a specific associate, they know who to find to expediate an urgent order while also giving them a timeline as to when the associate grabbed the labels and their last time they dropped things off.

### The Control Flow
Everything for the Bulk Picking team is handled by a barcode scanner. Javascript is used to ensure that there is no need for a mouse or a keyboard.

#### 1. Create the barcodes
  1. navigate to url/display_barcodes
  2. Either enter a number to print a certain amount of "Master Batches" or a name you'd like to use as a new user.
  3. A new window should open up, ctrl + P to print the page. Currently the page isn't formatted to use our specific sized labels.
#### 2. Manager UI
  1. navigate to url/manager-ui
  2. Scan a "Master Batch" to start assigning batches of product to a single barcode
  3. Scan as many batches as necessary to group all the labels together
  4. Finally, scan the "submit" barcode to tie everything together and send it to the database. 
#### 3. Picker UI
  1. This is designed to be fastest for the pickers.
  2. Scan the picker nametag
  3. Scan the master batch
  4. Scan "submit"
  5. I'm thinking about auto-submitting after the 2 fields are scanned in.
#### 4. Drop Station
  * This section does not have a Front End. It is meant to be run on a raspberry pi where the only thing attached to it is a barcode scanner
  *  Basically, the pickers would scan their nametag or the master batch to log that they've been to a certain location. 
  * Since I don't have access to the companies backend, I can only give clues as to where each item may be. 
  * Currently the Master Batch is being used to track what items are where.
#### 5. Batch Viewer
  * This the front end for the Shipping team.
  * This shows you who has which batches of items.
  * Each batch has a time stamp from when an associate has last updated that "Master Batches" location
  * There is a column that shows you each location visited for that master batch or if they are currently picking.
  * Each batch cell is a hyperlink to a view that contains all the items within that batch.
  * You can also search by specific items, Truck Routes, Order Numbers and Batches to narrow down what the shipping team may be looking for.
  
  
  
### The How's
This tool is built with Flask, SQLAlchemy, Pillow, Barcode.py, and SQLite3. There are plans to change the database to either MYSQL or postgreSQL for long term use. Due to the fact that I have limited access to the work computers, browser choice, and no direct access to the company backend, I have to use webscrapers built with Excel/VBA [because every computer has excel here] to gather the data I'm missing.

When there are batches logged from the Manager UI tab, a CSV file is created/updated. This CSV file is read by the web scraper to start looking for the items associated with those batches. Once that process is done, a separate CSV file is created. The seperate CSV file is then read with Python and logged to a database to create the links between batches scanned with the web UI and and the company backend.

The webscrapers and database updating would be run in separate processes from the main Flask backend thread.
