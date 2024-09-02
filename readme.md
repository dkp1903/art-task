## Steps to setup
The below steps can be performed on local system, or on GitHub Web Editor

For Github Web, go to github.dev/dkp1903/art-task and follow the steps below

You'll need three terminals - one for the server, one for the worker, and one for the client

Paste the .env properties for server and worker (both are the same) in the respective env files of server and worker
Once that's done, follow the below steps

Terminal 1
```
cd server
python -m venv/venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

Terminal 2
```
source server/venv/bin/activate
cd worker
pip install -r requirements.txt
python main.py
```

This should give you the server and worker running.

Copy the URL of the server, make it publicly accessible, and paste it in the .env of client.

Terminal 3
```
cd client
npm i
npm run dev
```


## Tasks
[X] Redis integration

[X] Edit, delete messages

[] Refactoring worker code

[] ARIA considerations