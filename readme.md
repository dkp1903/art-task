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

Terminal 3
```
cd client
npm i
npm run dev
```