import sys
from asvzBot import *
import os
from dotenv import load_dotenv
import datetime

load_dotenv()

BOT_PATH = os.getenv("BOT_PATH")

# get job_id as command-line argument from cron job


# log errors and exceptions to signups.log
def log(msg):
    with open(f'{BOT_PATH}/signups.log','a+') as f:
            f.write(f"{str(datetime.datetime.now())}: {msg}\n\n")

# main function: given an id, find corresponding lesson_num, start signup process, and then increase lesson_num by 1
def main(job_id):
    lesson_num = ''
    
    # lookup job_id in signups_list
    with open(f'{BOT_PATH}/signups_list','r') as f:
        for l in f.readlines():
            if l.split(',')[0] == job_id:
                lesson_num = l.split(',')[1]
                break 
    if lesson_num == '':
        log(f"Id {job_id} not found!")
        return
    
        

    # start signup with lesson_num and credentials
    username = os.getenv("ETHZUSERNAME")
    password = os.getenv("ETHZPASSWORD")
    try:
        asvz_signup(['--raspbian'],lesson_num,username,password)
    except Exception as e:
        log(f"Exception when executing asvzBot.asvz_signup for id {job_id}. \n Msg: {str(e)}")

    
    # increase lesson_num by 1 (code for the same lesson one week later)
    with open(f'{BOT_PATH}/signups_list','r') as f:
        with open(f'{BOT_PATH}/tmp','w+') as tmp:
            for l in f.readlines():
                if ',' in l and l.split(',')[0] == job_id:
                    tmp.write(f'{job_id},{str(int(lesson_num)+1)}') 
                else:
                    tmp.write(l)

    os.remove(f'{BOT_PATH}/signups_list')
    os.rename(f'{BOT_PATH}/tmp',f'{BOT_PATH}/signups_list')


if __name__ == '__main__':
    job_id = sys.argv[1]
    try:
        main(job_id)
    except Exception as e:
        log(f"Exception when executing signup_script for id {job_id}. \n Msg: {str(e)}")



