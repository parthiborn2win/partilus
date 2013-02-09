#imports
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.http import HttpResponse,HttpResponseRedirect 
from django.db.models import Count, Avg, Q
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail, BadHeaderError,send_mass_mail, mail_managers, mail_admins, EmailMessage
from django.contrib.sites.models import Site
from django.template.loader import render_to_string

import datetime
from datetime import timedelta
import smtplib
import os
import sys
import stat
import time
#import git
#import sh
    
def sizeof_fmt(num):
    for x in ['B','KB','MB','GB','TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0

def _searchfile(lookfor):
    # searchfile(files[0]['filename'])
    fileslist = []
    for root, dirs, files in os.walk('/opt/'):
        #print "searching", root
        if lookfor in files:
            try:
                print "found: %s" % os.path.join(root, lookfor)
                fileslist.append("%s" % os.path.join(root, lookfor))
            except:
                pass
    for root, dirs, files in os.walk('/home/'):
        if lookfor in files:
            try:
                print "found: %s" % os.path.join(root, lookfor)
                fileslist.append("%s" % os.path.join(root, lookfor))
            except:
                pass
    try:
        for root, dirs, files in os.walk('/var/www/'):
            if lookfor in files:
                try:
                    print "found: %s" % os.path.join(root, lookfor)
                    fileslist.append("%s" % os.path.join(root, lookfor))
                except:
                    pass
    except:
        pass
    return fileslist

def home(request,path='/'):
    
    try:
        path = request.GET['path'].lstrip('/')
    except:
        pass
    path = '/%s/' %(path)
    path = path.replace("//","/").replace("//","/")
    
    allfiles = os.listdir(path)    
    directories = [ {"name":name,
                     "size":str(sizeof_fmt(os.path.getsize("%s/%s" %(path,name)))),
                     "type":"Directory",
                     "permission":oct(stat.S_IMODE(os.lstat("%s/%s" %(path,name)).st_mode)),
                     "last_modified_on":time.ctime(os.path.getmtime("%s/%s" %(path,name))),
                     "created_on":time.ctime(os.path.getmtime("%s/%s" %(path,name)))                     
                     } for name in os.listdir(path) if os.path.isdir(os.path.join(path, name)) ]    
    files = [ {"filename":name,
               "size":str(sizeof_fmt(os.path.getsize("%s/%s" %(path,name)))),
               "type":name.split('.')[-1:][0],
               "permission":oct(stat.S_IMODE(os.lstat("%s/%s" %(path,name)).st_mode)),
               "last_modified_on":time.ctime(os.path.getmtime("%s/%s" %(path,name))),
               "created_on":time.ctime(os.path.getmtime("%s/%s" %(path,name)))
               } for name in os.listdir(path) if not os.path.isdir(os.path.join(path, name)) ]
              
    paths = path.split("/")
    try: del paths[0]
    except: pass
    try: del paths[len(paths)-1]
    except: pass
    pathlist = []
    print paths
    for apath in paths:
        pathdict={}
        pathdict['name']=apath
        url = '/'
        for bpath in paths:
            url += bpath+'/'
            if apath == bpath:
                break
        pathdict['url']=url
        pathlist.append(pathdict)
    
    
    return render_to_response('home.html',locals(),context_instance = RequestContext(request))

def searchfile(request):
    
    if request.method == "POST":
        search = True
        pDict = request.POST.copy()
        searchtxt = pDict['searchtxt']
        foundfiles = _searchfile(pDict['searchtxt'])
        files = []
        for file in foundfiles:
            files.append({ "filename":"%s (%s)" %(file.split('/')[-1:][0],file),
                                   "size":str(sizeof_fmt(os.path.getsize(file))),
                                   "type":file.split('.')[-1:][0],
                                   "permission":oct(stat.S_IMODE(os.lstat(file).st_mode)),
                                   "last_modified_on":time.ctime(os.path.getmtime(file)),
                                   "created_on":time.ctime(os.path.getmtime(file))
                                   })
    return render_to_response('home.html',locals(),context_instance = RequestContext(request))
    
def _cmd_git(request,cmd,extra_arg=None):
    '''
    git = sh.git.bake(_cwd='/home/me/repodir')
    print git.status()
    
    # checkout and track a remote branch
    print git.checkout('-b', 'somebranch')
    
    # add a file
    print git.add('somefile')
    
    # commit
    print git.commit(m='my commit message')
    
    # now we are one commit ahead
    print git.status()
    
    # 2
    # repo = git.Repo(path)
    # print repo.git.status()
    '''    
    
    try:
        git = sh.git.bake(_cwd=path)
        print git.status()
    except Exception,e:
        print sys.exc_traceback.tb_lineno,e
    
    return response

