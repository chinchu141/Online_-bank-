from django.shortcuts import render
from django.http import HttpResponseRedirect,HttpResponse,request
import pymysql,hashlib,os, binascii,re
import json,smtplib
from datetime import datetime,date
from django.core.mail import send_mail
from internet_bank.settings import EMAIL_HOST_USER
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import pandas as pd
import decimal



# db Connetion.
db=pymysql.connect("localhost","root","","db_internet_bank")
c=db.cursor()

# Create your views here.
context={}
dict={}
def login(request):
    """
         the fun to load login page
         --------------------------
    """
    #now = datetime.now()
    #formatted= now.strftime('%d-%m-%Y %H:%M')  
    # returns current date and time
     
    now = datetime.now() 
    e=now.strftime("%Y-%m-%d %H:%M")
    msg=""
    if(request.POST):
        uname=request.POST.get("textuser")
        newpwd=request.POST.get("textpass")
        if(uname=="Admin" and newpwd=="Admin@123"):
            return render(request,'admin.html')
        else:
            s="select count(*) from login_tb where Username='"+uname+"'"
            c.execute(s)
            account=c.fetchone()
            if(account[0]>0):
                s="select * from login_tb where Username='"+uname+"'"
                c.execute(s)
                account=c.fetchone()
                if verify_password(account[1],newpwd):
                    context['email']=uname
                    context['date']=account[2]
                    t="select Acc_No from bankdb where Email='"+uname+"'"
                    c.execute(t)
                    acc_no=c.fetchone()
                    accno=str(acc_no[0])
                    bad_chars = ['(', ')', ',']
                    for i in bad_chars :
                        accno = accno.replace(i, '')
                        context['accno']=accno
                        msg="success"
                #s="update login_tb set login_time={}.format(e) where  Username='"+uname+"'" 
                    s="update login_tb set login_time=%s  where Username='"+uname+"'"
                    c.execute(s,e)
                    
                    return render(request,'dashboard.html',context)
                    
                else:
                    msg=("incorrect password") 
            else:
                msg=("user doesnt exist")
        return render(request, 'login.html',context)
    context['msg']=msg  
    return render(request, 'login.html',context)

#-----------password hashing-------------


def hash_password(password):
    """
        Hash a password for storing.
    """
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), 
                                salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')


#=======================paasword verification================
def verify_password(pwd1, newpwd):
    """
    Verify a stored password against one provided by user
    """
    salt = pwd1[:64]
    pwd1 = pwd1[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha256', 
                                  newpwd.encode('utf-8'), 
                                  salt.encode('ascii'), 
                                  100000)
    pwdhash1 = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash1 == pwd1

#--------------------password validation-----------------
def password_check(passwd): 
      
    reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$"
      
    # compiling regex 
    pat = re.compile(reg) 
      
    # searching regex                  
    mat = re.search(pat, passwd) 
      
    # validating conditions 
    if mat: 
        print("Password is valid.") 
    else: 
        print("Password invalid !!")

#.................registration..........

def registration(request):
    msg=""
    
    if 'ok' in request.POST:
        name=request.POST.get("txtname")
        acc=request.POST.get("txtAcc")
        phno=request.POST.get("txtphno")
        email=request.POST.get("txtemail")
        atm_nbr=request.POST.get("txtatm")
        pwd1=request.POST.get("txtpass1")
        pwd2=request.POST.get("txtpass2")
        if pwd1!=pwd2:
            msg="password is missmatching"
            return render(request, 'registration.html',{"msg":msg})
        else:
            s="select Username,Phno,Email,ATM_No,Status from bankdb where Acc_No = '"+str(acc)+"'"
            c.execute(s)
            result = c.fetchone()
            print(result)
            #print(type(result[1]))
            print(type(phno))
            if result== None:
                msg="incorrect Account number !"
                return render(request, 'home.html',{"msg":msg}) 
            elif result[4] == 1:
                msg="You are already registered Please login !"
                return render(request, 'home.html',{"msg":msg}) 
            elif  name != result[0]:
                msg="unknown Entry please verify Either your name or Account number"
            elif str(result[1]) != phno:
                msg=" please Enter your registered phone number"
            elif result[2] != email:
                msg=" please Enter your registered Email id"
            elif str(result[3]) != atm_nbr:
                msg=" please Enter valid Atm card number"
            else:
                pwd=hash_password(pwd1)
                msg="Welcome",name
                t="insert into login_tb(Username,Password) values('"+str(email)+"','"+str(pwd)+"');"
                s="update bankdb set Status=1 where Acc_No = '"+str(acc)+"'"
                c.execute(t)
                c.execute(s)
                db.commit()
                return render(request, 'home.html',{"msg":msg}) 
            #return render(request, 'registration.html',{"msg":msg})
        return render(request, 'registration.html',{"msg":msg})
    return render(request, 'registration.html',{"msg":msg})
#----------------------

def home(request):
    return render(request, 'home.html',context)

#-----------------------------
def t(request):
    return render(request, 't_1.html')



#------------------------------
def history_tran(request):
    v = list(context.values())[3]
    r='select date for getting  history'
    result=""
    if 'download' in request.POST:
        r=sent_mail(result)
        print(r)
    if 'submit' in request.POST:
        fdate=request.POST.get("fdate")
        todate=request.POST.get("todate")
        type=request.POST.get("type")
        if fdate > todate:
            r='select valid date'
            return render(request,'history_tran.html',{'result':r})
        else:
            if type=='Fund Transfer':
                s="select Date,tran_Amount,t_id from transaction_tb where sender_accno='"+str(v)+"' and Date between '"+fdate+"' and '"+todate+"' "  
                c.execute(s)
            if type=='Deposit':
                s="select Date,Amount,Dep_id from Deposite_tb where User_acc='"+str(v)+"' and Date between '"+fdate+"' and '"+todate+"' "  
                c.execute(s)
            if type=='All':
                s="select Date,tran_Amount,t_id from transaction_tb where sender_accno='"+str(v)+"' and Date between '"+fdate+"' and '"+todate+"' "  
                c.execute(s)
                res = c.fetchall()
                
                t="select Date,Amount,Dep_id from Deposite_tb where User_acc='"+str(v)+"' and Date between '"+fdate+"' and '"+todate+"' "  
                c.execute(t)
                res2 = c.fetchall()
                if((len(res)<1) and (len(res2)<1)):
                    r='There are no transactions that match your selection'
                    return render(request,'history_tran.html',{'result':r})
                else:
                    t=type
                    return render(request,'history_tran.html',{'all':res,'type':t,'a':res2})
            result = c.fetchall()
            if(len(result)<1):
                r='There are no transactions that match your selection'
                return render(request,'history_tran.html',{'result':r})
            else:
                t=type
                return render(request,'history_tran.html',{'dict':result,'type':t})
            
        return render(request,'history_tran.html',{'result':r})
   
    return render(request,'history_tran.html',{'result':r})
   

#--------------------------
def dashboard(request):
    return render(request, 'dashboard.html',context)


def user_view(request):
    v = list(context.values())[1]
    msg=""
    #for selecting query from db using email

    s="select Username,HouseName,Phno,Acc_No,Balance from bankdb where Email='"+str(v)+"'"
    c.execute(s)
    result = c.fetchone()
    r=str(result[3])
    set=len(r)-4
    re=r[0:set]
    for i in range(0,set):
        j=re[i]
        re = re.replace(j, '*')
    re=re+r[-4:]
    context['name']=result[0]
    context['hname']=result[1]
    context['phno']=result[2]
    context['a_no']=re
    context['bal']=result[4]
    return render(request, 'user_view.html',context)


 #---------------------------transation  -------------------- 
def transaction(request):
    msg=""
    email = list(context.values())[1]
    
    #for selecting query from db using email

    s="select Acc_No,Balance from bankdb where Email='"+str(email)+"'"
    c.execute(s)
    result = c.fetchone()
    accno=str(result[0])
    bal=float(result[1])
    today = date.today()
    #print("Today's date:", today)
    
    #context['bal']=bal
    if 'submit' in request.POST:
        bank_name=request.POST.get("txtbname")
        rece_name=request.POST.get("txtrname")
        rece_accno=request.POST.get("txtrano")
        t_amount=request.POST.get("txtamt")
        sender_accno=request.POST.get("txtsnano")
        amount=float(t_amount)
        print(amount,bal)
        if (bal-100 <= amount):
            msg="No Sufficient balance"
            context['msg']=msg
            return render(request, 'transaction.html',context)
        else:
            amount=bal-amount
            print(amount)
            t="update bankdb set Balance=%s where Email='"+str(email)+"'"
            val=float(amount)
            print(val)
            s="insert into transaction_tb(Receiver_bank,Receiver_name,Receiver_accno,tran_Amount,sender_accno,Date) values('"+str(bank_name)+"','"+str(rece_name)+"','"+str(rece_accno)+"','"+str(t_amount)+"','"+str(sender_accno)+"','"+str(today)+"');"
            c.execute(t,val)
            c.execute(s)
            db.commit() 
            msg="success transaction"   
            subject = 'Debit Alert From MICRO BANK'
            message = ''' Dear Customer,This is to inform you that %s INR was debited from your MICRO BANK
            Thank you'''
            send_mail(subject, message, EMAIL_HOST_USER, [email], fail_silently = False)

            context['msg']=msg
        #else:
            #msg="amount should be less than 25000"
    return render(request, 'transaction.html',context)


    #-------------------------regverify---------------------

def dashboard1(request):
    return render(request, 'dashboard1.html',context)
   
def sent_mail(s):
    result=s
    print(s)
    f=open("statement.txt","w+")
            #s="select Date,tran_Amount,t_id from transaction_tb where sender_accno='"+str(v)+"' and Date between '"+fdate+"' and '"+todate+"' "  
            #c.execute(s)
            #result = c.fetchall()
    f.write(result)
    f.close()
    mail_content = "hi" 
    sender_address ='chinchujayan1997@gmail.com'
    sender_pass = 'Jesus@me'
    receiver_address = 'chinchumolj97@gmail.com'
    #setup mime
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address
    message['subject'] = 'Micro Bank Statement'
    message.attach(MIMEText( mail_content, 'plain/text'))
    attach_file_name = 'statement.txt'
    attach_file = open(attach_file_name, 'rb')
    payload = MIMEBase('application', 'octate-stream')
    payload.set_payload((attach_file).read())
    encoders.encode_base64(payload) #encode the attachment
        #add payload header with filename
    payload.add_header('Content-Decomposition', 'attachment', filename=attach_file_name)
    message.attach(payload)
        #Create SMTP session for sending the mail
    session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
    session.starttls() #enable security
    session.login(sender_address, sender_pass) #login with mail_id and password
    text = message.as_string()
    session.sendmail(sender_address,receiver_address, text)
    session.quit()
    print('Mail Sent')
    return "Mail send"
    
 

#-----------------------------------
def admin(request):
    return render(request, 'admin.html')

#-------------------------------------
def admin_user(request):
    account="hi"
    if 'all' in request.POST:
        s="select Username,Email,Phno,Acc_No,Balance,Status from bankdb "
        c.execute(s)
        account=c.fetchall()
        acc=list(account)
        i=0
        for  a in  acc:
            b=list(a)
            if (b[5]==1):
                v="registered"
                b[5]=v
            else:
                v="not registered"
                b[5]=v
            acc[i]=b
            i=i+1
        return render(request,'admin_user.html',{'dict':acc})
    if 'reg' in request.POST:
        s="select Username,Email,Phno,Acc_No,Balance,Status from bankdb where status=1"
        c.execute(s)
        account=c.fetchall()
        acc=list(account)
        i=0
        for  a in  acc:
            b=list(a)
            if (b[5]==1):
                v="registered"
                b[5]=v
            else:
                v="not registered"
                b[5]=v
            acc[i]=b
            i=i+1
        return render(request,'admin_user.html',{'dict':acc})
    if 'notreg' in request.POST:
        s="select Username,Email,Phno,Acc_No,Balance,Status from bankdb where status=0"
        c.execute(s)
        account=c.fetchall()
        acc=list(account)
        i=0
        for  a in  acc:
            b=list(a)
            if (b[5]==1):
                v="registered"
                b[5]=v
            else:
                v="not registered"
                b[5]=v
            acc[i]=b
            i=i+1
        return render(request,'admin_user.html',{'dict':acc})
    

    return render(request, 'admin_user.html')
#------------------------------------------

def more_info(request):
    sku = request.GET.get('sku')
    s="select * from bankdb where Email='"+sku+"'"
    c.execute(s)
    account=c.fetchone()
    return render(request, 'more_info.html',{'dict':account})
    #---------------------------------------
def update(request):
    sku = request.GET.get('sku')
    print(type(sku))
    print(str(sku))
    a=''
    s="select Username,Acc_No,Balance from bankdb where Email='"+str(sku)+"'"
    c.execute(s)
    acc=c.fetchone()
   
    amt=acc[2]
    acc_no=acc[1]

    
    if 'update' in request.POST:
        bal = request.POST.get('txtblns')
        d = decimal.Decimal(bal)
        now = datetime.now() 
        e=now.strftime("%Y-%m-%d %H:%M")
        
        amount = d + amt
        t="update bankdb set Balance=%s where Email='"+str(sku)+"'"
        v= str(amount)
        print("hi",e)
        s="insert into deposite_tb(User_acc,Amount,Date) values('"+str(acc_no)+"','"+str(d)+"','"+str(e)+"');"
        c.execute(t,v)
        c.execute(s)
        db.commit()
        return render(request, 'admin.html',{'dict':acc})
    return render(request, 'update.html',{'dict':acc})


#----------------------------------

def contact(request):

    return render(request,'contact.html')

#-------------------------------

def book_gas(request):
    s="select distinct(District) from gas_agency "
    c.execute(s)
    dis=c.fetchall()    
    if 'submit' in request.POST:
        v=request.POST.get("dis")
        print(v)
        s="select distinct(District) from gas_agency "
        c.execute(s)
        gas=c.fetchall()
        print(gas)
        return render(request,'book_gas.html',{'gas':gas})
    return render(request,'book_gas.html',{'dis':dis})

    