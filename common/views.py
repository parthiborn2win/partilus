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
import shutil, errno
#import git
#import sh

def copyanything(src, dst):
    try:
        try:
            shutil.copytree(src, dst)
        except OSError as exc:
            if exc.errno == errno.ENOTDIR:
                shutil.copy(src, dst)
            else: 
                print 'some error machi'
                pass
    except Exception,e:
        return e
    
    return "Pasted Successfully"
        
def sizeof_fmt(num):
    for x in ['B','KB','MB','GB','TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0

def mode_matches(mode, file):
    """Return True if 'file' matches 'mode'.

    'mode' should be an integer representing an octal mode (eg
    int("755", 8) -> 493).
    """
    # Extract the permissions bits from the file's (or
    # directory's) stat info.
    filemode = stat.S_IMODE(os.stat(file).st_mode)

    return filemode == mode

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
    
    permission_modes = [1,2,3,4,5,6,7]
    
    try:
        paste_msg = request.session["paste_msg"]
        del request.session["paste_msg"]
    except:
        pass
    
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
    
def addfolder(request,fmode="folder"):
    # POST method only
    pDict = request.POST.copy()
    
    location = pDict['location_%s' %(fmode)]
    newfolder_name = pDict['newname_%s' %(fmode)]
    permission = int("%s%s%s" %(pDict['permission1_%s' %(fmode)],pDict['permission2_%s' %(fmode)],pDict['permission3_%s' %(fmode)]),8)
    
    location_path = "%s/%s" %(location,newfolder_name)
    if not os.path.exists(location_path):
        if fmode == "file":
            print location_path
            open(location_path, 'w').close()
        else: 
            os.mkdir(location_path)
        os.chmod(location_path,permission)
    else:
        print "Already Exists"
        
    return HttpResponseRedirect("%s?path=%s" %(reverse('home'),location))    

def copy(request,type):
    gDict = request.GET.copy()
    
    request.session['cp_type'] = type
    request.session['cp_path'] = gDict['path']
        
    print type,gDict['path']
    
    return HttpResponse("success")

def paste(request):
    gDict = request.GET.copy()
    copy_to_path = gDict['path']
    response = HttpResponseRedirect("%s?path=%s" %(reverse('home'),copy_to_path))

    type = request.session['cp_type']
    copy_file = request.session['cp_path']
    
    print type,copy_to_path,copy_file
    request.session["paste_msg"] = copyanything(copy_file, copy_to_path)
    
    del request.session['cp_type']
    del request.session['cp_path']
    
    return response

def delete(request):
    gDict = request.GET.copy()
    del_path = gDict['name']
    
    try:
        try:
            shutil.rmtree(del_path)
        except:
            os.remove(del_path)
        return_path = del_path.rstrip(del_path.split('/')[-1:][0])
    except:
        return_path = '/'    
    
    return HttpResponseRedirect("%s?path=%s" %(reverse('home'),return_path))

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

