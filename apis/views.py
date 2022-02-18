from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import HttpResponse, render, redirect
import re
from .config import db_config
import mysql.connector
from .master_reset import * # master_reset_add, master_reset_fetch, master_reset_delete
from datetime import datetime
import bcrypt
import hashlib
import os
import boto3
import matplotlib.image as mpimg
import io
import random

import smtplib, ssl   # pip install smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from string import Template

sender_email = "arif.ben90@gmail.com"
password = "arifben12"




def read_template(filename):
    with open(filename, 'r', encoding='utf-8') as template_file:
        template_file_content = template_file.read()
    return Template(template_file_content)

    
@api_view(['POST'])
def reset_email(request):

    # global email_pass
    email_pass = request.POST.get("email", None)
    # print("------ printing input email ------------", email_pass)
    email_pass = str(email_pass)
    
    if not email_pass:
        context = {
            'error_msg':'* Please provide your email ID',
            "status": -1
        }
        # print("--------- not email_pass ------------")
        return Response(context)
        
        
    regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    if re.search(regex, email_pass) == None:
        context = {
            'error_msg':'* Please provide a valid email id',
            "status": "error"
        }
        # print("--------- not a regex match ------------")
        return Response(context)
        
    cnx=mysql.connector.connect(user=db_config['user'],
                               password=db_config['password'],
                               host=db_config['host'],
                               database=db_config['database'],use_pure=True)
    cursor=cnx.cursor()

    query = 'SELECT COUNT(1) FROM BK_AI.user_login WHERE email_id= %s'
    cursor.execute(query,(email_pass,))
    row=cursor.fetchone()
    cnx.commit()
    count = row[0]
    cnx.close()
    if count != 1:
        context = {
            'error_msg': '*Email does not exist! Please sign-up first.',
            "status": "error"
        }
        # print("--------- email not in DB ------------")
        return Response(context)
    
    
    # request.session['password_reset_details'][email_pass] = random.randint(000000,999999)
    # master_reset_list = master_reset(email_pass, random.randint(000000,999999))
    otp = random.randint(000000,999999)
    
    master_reset_add(email_pass, otp)
    
    print("---- OTP ----: ", master_reset_fetch(email_pass))
    print(sender_email, password)

    #---------------------------------------------------------------------------------
    ###### SEND EMAIL WITH OTP
    #---------------------------------------------------------------------------------
    
    # with open('/home/ubuntu/BKAI_backend/apis/pass_rec.txt') as template:
    #         message_template = template.readlines()
    
    
    message_template = read_template('/home/ubuntu/BKAI_backend/apis/pass_rec.txt')
    
    receiver_email = str(email_pass)
    print(receiver_email)
    msg = MIMEMultipart()
    
    otp_template = message_template.substitute(OTP=str(otp).title())

    # setup the parameters of the message
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject']="OTP for password reset"
    

    # add in the message body
    msg.attach(MIMEText(otp_template, 'plain'))
    
    # context = ssl.create_default_context()
    # with smtplib.SMTP("smtp.gmail.com", 465) as server:
    #     server.login(sender_email, password)
    #     server.sendmail(sender_email, receiver_email, msg.as_string())
    
    server = smtplib.SMTP_SSL('smtp.gmail.com',465)
    server.login(sender_email,password)
    server.sendmail(sender_email,receiver_email,msg.as_string())
        
    # except:
    #     print("Wrong")
    
    # print("/n --------------------------------- /n", otp_template)
    
    context = {
        "status": 1
    }
    
    return Response(context)
    
    


@api_view(['POST'])
def reset_otp(request, email_pass, format=None):
    
    # #-----------------------------------------------------------------------------------------------
    # if 'submit - OTP' in request.POST:
    # #-----------------------------------------------------------------------------------------------
    otp = master_reset_fetch(email_pass)
    
    user_otp = request.POST.get("otp", None)
    
    print("----- user_otp -----", user_otp)
    
    if not user_otp.isdigit():
        context = {
            'error_msg': '*Invalid OTP'
        }
        return Response(context)
        
    if otp == int(user_otp):
        context = {
            'error_msg': '* OTP matched',
            'status': 2
        }
        return Response(context)
        
    else:
        context = {
            'error_msg': "*OTP does not match"
        }
        return Response(context)
        



@api_view(['POST'])
def reset_password(request, email_pass, format=None):
    
    pwd = request.POST['password']
    pwd2 = request.POST['confirmed-password']
        
    if not pwd or not pwd2:
        context = {
            "error_msg": "* Please enter your new password"
        }
        return Response(context)
    
    if pwd == pwd2:
        print("----- Passwords Matched -----")
        
        salt = bcrypt.gensalt()
        hashed_password = hashlib.pbkdf2_hmac('sha256', pwd.encode('ascii'), salt, 100000,dklen=16)
        hashed_password = hashed_password.hex()
        
        cnx = mysql.connector.connect(user=db_config['user'],
                                  password=db_config['password'],
                                  host=db_config['host'],
                                  database=db_config['database'], use_pure=True)
        
        cursor = cnx.cursor()
        # email_id, pwd_hash, salt
        querry_pass = 'UPDATE user_login SET pwd_hash = %s, salt = %s where email_id = %s;'
        # UPDATE new_schema.new_table SET salt = %s, pwd_hash = %s WHERE uid = %s;" 
        cursor.execute(querry_pass,(hashed_password, salt, email_pass))
        cnx.commit()
        cnx.close()
        
        master_reset_delete(email_pass)

        context = {
            'status': 3
        }
        return Response(context)
    else:
        context = {
            "error_msg": "* Passwords do not match"
        }
        return Response(context)
    
