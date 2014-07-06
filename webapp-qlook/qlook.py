# -*- coding: utf-8 -*-
"""
qlook.py

Created on Sun Jul  6 12:02:36 2014

@author: ras
"""
import os
import json
import glob
from datetime import datetime

from flask import Flask
from flask import request, render_template

home = os.path.abspath(os.path.dirname(__file__))

local_image_path = os.path.join(home, 'static/images')
url_image_path = '/static/images'

station_name = 'Smidsbjerg'
area_name = 'dkf'
composites = [("night_rgb", "Night RGB"),
              ("day_rgb", "Day RGB"),
              ("day_rgb_hist", "Day RGB histogram"),
              ("ir", "Infrared"),
              ("vis", "Visible")]

app = Flask(__name__)

class Images(object):
    def __init__(self, area_name, passid):
        self.area_name = area_name
        self.passid = passid
        self._list = []
        for id_, name in composites:
            fname = "%s-%s-%s.png" % (self.passid,
                                      id_, 
                                      self.area_name)
            if os.path.isfile(local_image_path + '/large/' + fname):
                self._list.append({'id': id_,
                                   'name': name,
                                   'thumb': url_image_path + '/thumb/' + fname,
                                   'small': url_image_path + '/small/' + fname,
                                   'large': url_image_path + '/large/' + fname})

    def __getitem__(self, i):
        return self._list[i]

    def __iter__(self):
        for i in self._list:
            yield i

@app.route('/hello')
@app.route('/hello/<name>')
def hello(name=None):
    return render_template('hello.html', name=name)

@app.route('/qlook')
@app.route('/qlook/')
def qlook_list():
    a_comp = composites[0][0]
    thumbs = glob.glob(local_image_path + '/thumb/*-%s-*.png' % a_comp)
    thumbs = sorted(thumbs, reverse=True)[:30]
    thumb_list = []
    for thumb in thumbs:
        fname = os.path.basename(thumb)
        passid = fname.split('-')[0]
        image = url_image_path + '/thumb/' + fname
        thumb_list.append({'id': passid, 
                           'image': image,
                           'item_url': '/qlook/' + passid})
    return render_template('qlook_list.html',
                           station=station_name,
                           thumbs=thumb_list)

@app.route('/qlook/<passid>')
def qlook_item(passid):
    images = Images(area_name, passid)
    return render_template('qlook_item.html',
                           station=station_name,
                           images=images)

if __name__ == '__main__':
    app.run(debug=True)
