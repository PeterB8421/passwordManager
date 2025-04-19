# Password Manager
## Author: Petr Balok, xbalok00
## BZA project 2024/2025

### Dependencies
You will need a Python environment and MySQL database.
After setting up your database, change the values in *config.cfg* according to your database.
And import the database schema from *db_schemesql.sql*.

To set up Python environment, use command `virtualenv .venv`, then activate your virtual environment
using `.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (Linux).

Now install Python modules required using `pip install -r requirements.txt`.

For Linux, you also need to have Tkinter installed, for Debian/Ubuntu use `sudo apt install python3-tk`

*config.cfg* items:

| Item     | Meaning                                           |
|----------|---------------------------------------------------|
| host     | IP address of the database server                 |
| user     | Username for user in the database system          |
| password | Password for the user with access to the database |
| database | Name of database to use                           |


### Using the Password Manager
After installing dependencies and configuring the database, run `python gui.py` to start the GUI
and follow the instructions in the GUI.
