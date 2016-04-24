#!/usr/bin/python3
#    DigSig: Digital Signage
#    Copyright (C) 2015-2016 Gianluca Costa <g.costa@xplico.org>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


# in the file /etc/mplayer/mplayer.conf insert: lirc=no

import errno
import threading
import time
import os
import json
import urllib.request
import shutil
import operator
import copy
import requests
import xml.etree.ElementTree as ET
from subprocess import Popen, PIPE

version = '0.3.0'

tmp_dir = '/tmp/'
#config_dir = '/data/digsig/'
config_dir = './'
data_dir = '/tmp'
cfg_path = config_dir+'/digsig_cfg.json'
report_xml = tmp_dir+'/media_report.xml'

os.system('mkdir -p '+config_dir)
os.system('chown -R www-data:www-data '+config_dir)

threadLock = threading.Lock()
threads_dnld = {}
threads_play = {}
downloads = {}
play_list = {}
media_started = {}
reports = {}
list_id = 0
media_id = 0
err_none = '0000'
err_past = '1000'
err_not_found = '2000'

    
class VisualThr (threading.Thread):
    def __init__(self, id, wid):
        threading.Thread.__init__(self)
        self.id = id
        self.wid = wid
        
    def run(self):
        global list_id
        global media_id
        global media_started
        
        dnull = open(os.devnull, 'r')
        print('Play Manager')
        while True:
            threadLock.acquire()
            while len(play_list) == 0:
                threadLock.release()
                time.sleep(0.5)
                threadLock.acquire()
            print('New visualization: '+str(len(play_list)))
            nxt_list = False
            
            lid = list_id
            mid = media_id
            media_id += 1
            if list_id == 0:
                nxt_list = True
            elif mid not in play_list[lid]:
                # play completed
                nxt_list = True
                del play_list[lid]
                print("End visualization list: "+str(len(play_list)));
                if len(play_list) == 0:
                    list_id = 0
                    threadLock.release()
                    continue
            elif media_id in play_list[lid]:
                if time.time() >= float(play_list[lid][media_id]['start']):
                    reports[lid][play_list[lid][mid]['id']] = {'status': err_past}
                    threadLock.release()
                    continue
            
            if nxt_list:
                # research the playlist to execute
                tm = 0
                for p_id in play_list:
                    if tm == 0:
                        tm = play_list[p_id][0]['start']
                        lid = p_id
                    elif tm > play_list[p_id][0]['start']:
                        tm = play_list[p_id][0]['start']
                        lid = p_id
                list_id = lid
                reports[lid] = {}
                mid = 0
                media_id = 1
            
            media_started[self.id] = False
            extension = os.path.splitext(play_list[lid][mid]['url'])[1]
            extension = extension.lower()
            file_path = data_dir+'/'+str(play_list[lid][mid]['id'])+extension
            tstart = float(play_list[lid][mid]['start'])
            if play_list[lid][mid]['id'] not in reports[lid]:
                reports[lid][play_list[lid][mid]['id']] = {}
            threadLock.release()
            print('List '+str(lid)+' (mid '+str(mid)+')')
            print('\turl: '+play_list[lid][mid]['url'])
            print('\tFile: '+file_path)
            
            while time.time() < tstart-2:
                time.sleep(0.250)
            # image or video
            if not os.path.isfile(file_path):
                threadLock.acquire()
                reports[lid][play_list[lid][mid]['id']] = {'status': err_not_found}
                threadLock.release()
                print('Media not found : '+str(play_list[lid][mid]['id'])+' '+file_path)
                continue
            if play_list[lid][mid]['type'].lower() == 'video': # video
                print('Start play: media'+str(mid))
                # play in pause
                p = Popen(['mplayer', '-slave', '-noborder', '-nosound', '-framedrop', '-geometry', '+4200+4200', '-vo', 'x11', '-title', 'media'+str(mid),'-idle', '-fixed-vo', file_path], stdin=PIPE, universal_newlines=True, stdout=dnull)
                p.stdin.write('pause\n')
                time.sleep(0.150)
                #os.system('xdotool windowunmap `xdotool search --name media'+str(mid)+'`')
                while time.time() < tstart:
                    time.sleep(0.250)
                threadLock.acquire()
                reports[lid][play_list[lid][mid]['id']] = {'status': err_none, 'started': time.time()}
                threadLock.release()
                os.system('xdotool windowmove `xdotool search --name media'+str(mid)+'` 0 0')
                #os.system('xdotool windowmap `xdotool search --name media'+str(mid)+'`')
                os.system('xdotool windowraise `xdotool search --name media'+str(mid)+'`')
                media_started[self.wid] = False
                media_started[self.id] = True
                p.stdin.write('pause\n')

                while not media_started[self.wid]:
                    time.sleep(0.250)
                
                os.system('xdotool windowunmap `xdotool search --name media'+str(mid)+'`')
                p.terminate()
                p.kill()
            elif play_list[lid][mid]['type'].lower() == 'img': # images
                print('Play img: media'+str(mid))
                # play in pause
                p = Popen(['feh', '-B', 'white', '-Y', '-x', '-g', '+4200+4200', '--title', 'mediaimg'+str(mid), file_path], stdin=PIPE, universal_newlines=True, stdout=dnull)
                p.stdin.write('pause\n')
                time.sleep(0.150)
                #os.system('xdotool windowunmap `xdotool search --name mediaimg'+str(mid)+'`')
                while time.time() < tstart:
                    time.sleep(0.250)
                threadLock.acquire()
                reports[lid][play_list[lid][mid]['id']] = {'status': err_none, 'started': time.time()}
                threadLock.release()
                os.system('xdotool windowmove `xdotool search --name mediaimg'+str(mid)+'` 0 0')
                #os.system('xdotool windowmap `xdotool search --name mediaimg'+str(mid)+'`')
                os.system('xdotool windowraise `xdotool search --name mediaimg'+str(mid)+'`')
                media_started[self.wid] = False
                media_started[self.id] = True
                p.stdin.write('pause\n')

                while not media_started[self.wid]:
                    time.sleep(0.250)
                
                os.system('xdotool windowunmap `xdotool search --name mediaimg'+str(mid)+'`')
                p.terminate()
                p.kill()
            else:
                print('Media unknow')
            
            
            
class DownloadThr (threading.Thread):
    def __init__(self, mng, id=None, url=None, path=None):
        threading.Thread.__init__(self)
        self.mng = mng
        self.id = id
        self.url = url
        self.path = path
        
    def run(self):
        if self.mng == False: # slave
            print('Download Media:')
            res = True
            print('\t'+self.url)
            print('\t'+self.path)
            try:
                with urllib.request.urlopen(self.url) as response, open(self.path, 'wb') as out_file:
                    shutil.copyfileobj(response, out_file)
                res = True
            except Exception as e:
                print(Exception('Download connection error: %s' % e))
                res = False
            threads_dnld[self.id] = res
        else: # manager
            print('Download Manager')
            while True:
                while len(downloads) == 0: # lists in the queue
                    time.sleep(1)
                threadLock.acquire()
                dwnds = downloads.copy()
                downloads.clear()
                threadLock.release()
                for keyd in dwnds:
                    download = dwnds[keyd]
                    for key in download:
                        elem = download[key]
                        extension = os.path.splitext(elem['url'])[1]
                        extension = extension.lower()
                        file_path = data_dir+'/'+str(elem['id'])+extension
                        if not os.path.isfile(file_path):
                            # libero spazio
                            s = os.statvfs(data_dir)
                            if ((s.f_bavail * s.f_frsize) / 1024 /1024) < 100: # in Mbyte
                                RmMedia(data_dir)
                            #download
                            tmp_file = tmp_dir+'/'+str(elem['id'])+extension
                            thread = DownloadThr(False, 1, elem['url'], tmp_file)
                            thread.daemon = True
                            thread.start()
                            thread.join()
                            if threads_dnld[1]:
                                print('\t'+'Download completed')
                                os.rename(tmp_file, file_path)
                            else:
                                print('\t'+'Download fails')
                        else:
                            os.utime(file_path, None)
                time.sleep(1)
            print('Download Manager: end')
            
        
def RmMedia(data_dir):
    file_dir = [ data_dir+'/'+f for f in os.listdir(data_dir) if os.path.isfile(os.path.join(data_dir, f)) ]
    file_data = {}
    for fname in file_dir:
        file_data[fname] = os.stat(fname).st_atime
    sortedFiles = sorted(file_data.items(), key=operator.itemgetter(1))
    delete = len(sortedFiles)
    for x in range(0, delete):
        os.remove(sortedFiles[x][0])
        s = os.statvfs(data_dir)
        if ((s.f_bavail * s.f_frsize) / 1024 /1024) > 150: # in Mbyte
            break


# convert the xml data in a dictrionary (xml e' fatto solo da tag)
def XmlDic(xml_file_path):
    ret = {}
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    i = 0
    for child in root:
        if child.tag == 'elem':
            if i == 0:
                ret['elem'] = {}
            ret['elem'][i] = {}
            for dadv in child:
                if dadv.text.isdigit():
                    ret['elem'][i][dadv.tag] = int(dadv.text)
                else:
                    ret['elem'][i][dadv.tag] = dadv.text
            if 'type' not in ret['elem'][i]:
                ret['elem'][i]['type'] = ''
                print('Type non definito')
            i += 1
        elif child.tag == 'action':
            ret['action'] = {}
            for dadv in child:
                if dadv.text.isdigit():
                    ret['action'][dadv.tag] = int(dadv.text)
                else:
                    ret['action'][dadv.tag] = dadv.text
        else:
            if child.text.isdigit():
                ret[child.tag] = int(child.text)
            else:
                ret[child.tag] = child.text
    return ret
    
        
def ServerCom(cfg):
    ret = {}
    res = True
    try:
        with urllib.request.urlopen(cfg['servel_url']+'?id='+cfg['id']+'&v='+cfg['version']) as response, open(tmp_dir+'/ncmd.xml', 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
    except Exception as e:
        print(Exception('Server connection error: %s' % e))
        res = False
        
    if res == True: # manage server responce
        ret = XmlDic(tmp_dir+'/ncmd.xml')
    
    return ret
    
    
def Report2Xml(rep, file_name):
    try:
        f = open(file_name, 'w')
        f.write('<?xml version="1.0" encoding="UTF-8"?>')
        f.write('<log>')
        for lid in rep:
            f.write('<id>'+str(lid)+'</id>')
            for mid in rep[lid]:
                f.write('<elem><id>'+str(mid)+'</id>')
                for key in rep[lid][mid]:
                    f.write('<'+key+'>'+str(rep[lid][mid][key])+'</'+key+'>')
                f.write('</elem>')
        f.write('</log>')
        f.close()
        return True
        
    except Exception as e:
        print(Exception('XML error: %s' % e))
        pass
        
    return False
    
    
def ServerSendLog(cfg, lid):
    # generazione xml
    rep = {}
    rep[lid] = {}
    threadLock.acquire()
    if lid in reports:
        rep[lid] = copy.deepcopy(reports[lid])
    else:
        print('Report empty')
    threadLock.release()
    if Report2Xml(rep, report_xml) == False:
        return False
    
    # invio
    res = True
    try:
        url = cfg['servel_url']+'?id='+cfg['id']+'&v='+cfg['version']
        files = {'file':open(report_xml)}
        r = requests.post(url, files=files)
        print('Server responce: '+r.status_code)
    except Exception as e:
        print(Exception('Server connection error: %s' % e))
        res = False
        
    if res == True:
        threadLock.acquire()
        if lid not in play_list:
            del reports[lid]
        threadLock.release()
    
    return res
    
    
def main():
    unix_timestamp = time.time()
    
    # configuration
    json_data = open(cfg_path)
    cfg = json.load(json_data)
    json_data.close()
    cfg['version'] = version
    
    # thread: download manager
    download_mng = DownloadThr(True)
    download_mng.daemon = True
    download_mng.start()
    
    # thread: visualization manager
    visual_even = VisualThr(0, 1)
    visual_odd = VisualThr(1, 0)
    visual_even.daemon = True
    visual_odd.daemon = True
    visual_even.start()
    visual_odd.start()
    
    # main cicle
    server_to = unix_timestamp
    while True:
        unix_timestamp = time.time()
        # server comunication
        if server_to < unix_timestamp:
            print('Richiesta al server')
            data = ServerCom(cfg)
            if 'next_req' in data: # next request
                server_to = float(unix_timestamp) + float(data['next_req'])
            
            if 'elem' in data: # new list, new contents
                #print(data['elem'])
                if 'id' in data:
                    if data['id'] not in play_list: # queue  for play
                        print('added play ID: '+data['id'])
                        print('added download ID: '+data['id'])
                        threadLock.acquire()
                        downloads[data['id']] = data['elem']
                        play_list[data['id']] = data['elem']
                        threadLock.release()
            
            if 'action' in data: # action/command manager
                if 'cmd' in data['action']:
                    if data['action']['cmd'].lower() == 'log':
                        if 'param' in data['action']:
                            if ServerSendLog(cfg, data['action']['param']) == False:
                                print("Error sending the data to the server")
                        else:
                            print('Parameter error definition')
                    else:
                        print('Command unknow')
        time.sleep(1)
        
    
if __name__ == '__main__':
    main()
