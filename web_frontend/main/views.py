# -*- coding: utf-8 -*-
# # Create your views here.

from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.base import View
from django.shortcuts import render_to_response, render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from django.contrib import auth
from django.core.urlresolvers import reverse_lazy
from django.conf import settings

#from forms import OwnerForm, HeaterForm
#from models import Contact, Heater
import os
import yaml
import shutil

def findfiles(dir_base, file_extensions):
    ret = []
    for root, dirs, files in os.walk(dir_base):
        for file in files:
            if not "." in file:
                continue
            ext = file.split(".")[-1]
            if ext in file_extensions:
                ret.append(os.path.join(root, file))
    return ret


class LogoutView(View):
    def get(self, request):
        auth.logout(request)
        return HttpResponseRedirect("/")


def settings_restore(request):
    shutil.copyfile(settings.PLAYER_SETTINGS_DEFAULT_YAML_FILE, settings.PLAYER_SETTINGS_YAML_FILE)
    return HttpResponseRedirect("/settings/")


def settings_view(request):
    if request.method == 'POST': # If the form has been submitted...
        with open(settings.PLAYER_SETTINGS_YAML_FILE, 'w') as outfile:
            outfile.write(request.POST.get("settings"))
            return HttpResponseRedirect("/settings/")

    player_settings = open(settings.PLAYER_SETTINGS_YAML_FILE).read()
    return render(request, 'main/settings.html', {"settings": player_settings})


def index_view(request):
    PLAYER_SETTINGS = yaml.load(open(settings.PLAYER_SETTINGS_YAML_FILE))
    PLAYLIST = yaml.load(open(settings.PLAYLIST_YAML_FILE))

    files = {
        "video": [],
        "audio": [],
        "image": [],
    }

    playlist_files = [
        #{ "fn": ..., "media": video/audio/image, "existing": True/False}
    ]

    for fn in PLAYLIST["playlist"]:
        ext = fn.split(".")[-1]
        media_type = None
        if ext in PLAYER_SETTINGS["media_extensions"]["video"]:
            media_type = "video"
        elif ext in PLAYER_SETTINGS["media_extensions"]["audio"]:
            media_type = "audio"
        elif ext in PLAYER_SETTINGS["media_extensions"]["image"]:
            media_type = "image"
        else:
            raise Exception("Not recognized file type for fn '%s'" % fn)

        playlist_files.append({ "fn": fn, "media": media_type, "existing": os.path.isfile(fn) })


    for dir in PLAYER_SETTINGS["media_search_directories"]:
        files["video"] += [f for f in findfiles(dir, PLAYER_SETTINGS["media_extensions"]["video"]) if f not in PLAYLIST["playlist"]]
        files["audio"] += [f for f in findfiles(dir, PLAYER_SETTINGS["media_extensions"]["audio"]) if f not in PLAYLIST["playlist"]]
        files["image"] += [f for f in findfiles(dir, PLAYER_SETTINGS["media_extensions"]["image"]) if f not in PLAYLIST["playlist"]]

    print playlist_files
    print files
    return render(request, 'index.html', {"media_files": files, "playlist_files": playlist_files })


def playlist_save(request):
    if request.method == 'POST': # If the form has been submitted...
        data = {
            "playlist": request.POST.getlist("fn[]"),
        }
        print data
        with open(settings.PLAYLIST_YAML_FILE, 'w') as outfile:
            outfile.write( yaml.dump(data, default_flow_style=True) )

        return HttpResponseRedirect("/")
    return HttpResponse("no post")
