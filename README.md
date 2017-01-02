# MultiManager

# Description: MultiManager is a website that allows multimedia editors on The Harvard Crimson order, fulfill, pickup, 
return, and update photography equipment. 

# Definitions:
Multimedia = photography and video
Pitch = photography/video assignment
Comper = a trainee
JE = junior editor
Exec = executive editor. A leader on the multimedia board who delivers pitches and have admin access.

The website can be accessed by executing these commands and opening the web server:
cd project
flask run


New users must register to create an account. Current users can login.

# Compers/JEs:
A user can view the current inventory to see what is available. If a user in o photography assignment and they require
equipment, they can go to the navigation bar and click "Request Equipment." This will link to a page with a form for 
ordering equipment. Here, a user can type in a short description of the pitch they are doing. The user can then
select if they need a camera, lens, microphone, and/or tripod. The user can then enter a time they will need the equipment
by. They can then select an Exec to request the equipment from. The Exec is typically the person who assigned the user
the pitch. The user must then agree to the terms and conditions for borrowing equipment. After the form is filled out,
the user can request the equipment. This generates an email to the Exec that was selected stating that they have a 
new equipment request from that user. Once the user receives an email from an Exec describing what locker the equipment
is in, the user can go to "My Orders". The user can click "Pick Up" to confirm that they've taken the equipment from
the locker and are going to use it. After they are done with their pitch, the user returns the equipment back into
the locker and on the website, they go to "My Orders" and click "Return." This automatically generates an email to the
Exec notifying them the equipment has been returned. 

# Execs:
Execs are notified via email when a new equipment request has been made. Execs can login into their account. Once logged
in, they are also presented with an inventory of equipment. Execs, when fulfilling orders, can know at a glance what
equipment is available or not. Execs can then go to the navigation bar and click "Fulfill Orders", which redirects them
to a table of all the orders that are waiting for them. To fulfill a request, an Exec clicks on the Comper/JE's name which
redirects the Exec to the fulfillment page. The Exec can choose what equipment they will be leaving the requester as well
as what locker it will be in. When the Exec submits the form by clickign "Done", an email is generated to the requester,
notifying that their order has been fulfilled and which locker the equipment is in. Once the Exec receives an email
when the requester has returned the equipment, the Exec can go to the navigation bar and click on "Dayslot". The Exec
can see in real life if the equipment has been returned. If it has, in "Dayslot", the Exec can click on "Return to Main
Locker" to update the inventory. The Exec can also free up the locker to be able to be used again by clicking on "Free".
After the equipment has been returned, the Exec, in "Dayslot", can click on "Complete Order" it removes it from the Exec's
"Fulfill Orders" and the requester's "My Orders". This completes one whole cycle of equipment fulfillment. An Exec can 
also sign out equipment themselves by clicking "Sign Out Equipment" in the navigation bar. Once that form is submitted,
the inventory is updated to show any changes in an equipment's availability. An Exec can modify current equipment by 
clicking on the equipment's "Equipment Code" on the landing page, accessed by clicking "MultiManager" in the navigation
bar. An Exec can also add equipment to the inventory by clicking "Add a new item" on the landing page. Moreover, an Exec
can view the history of orders by clicking "Order History" in the navigation bar.
