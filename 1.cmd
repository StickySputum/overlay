@echo off
call myenv\Scripts\activate
pip install -r requirements.txt
python main.py
