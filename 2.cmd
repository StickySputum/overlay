@echo off
start steam://rungameid/570
call myenv\Scripts\activate
pip install -r requirements.txt
python main.py
