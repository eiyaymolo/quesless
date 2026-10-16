QUEUELESS - COMPLETE PROJECT

1. Unzip this file. Open the "queueless_full" folder in VS Code
   (File > Open Folder).

2. Open Terminal > New Terminal, then run one at a time:
   python -m pip install django
   python manage.py makemigrations documents
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver

3. Open http://127.0.0.1:8000/admin/ and log in with your superuser.
   Add Document types (Barangay Clearance, Indigency, Residency)
   and Pickup slots (date, time, capacity).
   To make someone barangay staff, tick "Staff status" on their user.

4. Open http://127.0.0.1:8000/ to use the site (no new migration needed for the redesign).

SENDING A DOCUMENT ONLINE:
Staff > Update a request > "Document file" > Choose File (PDF only)
> set status to Ready > Save. The resident sees "Download PDF" in
My Requests. Pickup slot is optional if you send the file online.

IF YOU UPDATED FROM AN OLDER ZIP: copy these files over your existing
folder (keep your db.sqlite3), then run:
   python manage.py makemigrations documents
   python manage.py migrate

Do not press the Run button on single files. Always use the terminal
commands above.

PYTHONANYWHERE: upload and unzip, make a web app (Manual config),
point the WSGI file to queueless.settings, set the source and
virtualenv paths, then run makemigrations/migrate in a Bash console.


TWO LINKS
Residents:        http://127.0.0.1:8000/
Barangay portal:  http://127.0.0.1:8000/barangay/   (staff and admin together)
(The old /admin/ page still works as a backup.)
