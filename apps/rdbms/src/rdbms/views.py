#!/usr/bin/env python
# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import json

from functools import wraps

from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

from desktop.context_processors import get_app_name
from desktop.models import Document
from desktop.lib.django_util import render

from librdbms import conf
from librdbms.design import SQLdesign

from beeswax import models as beeswax_models
from beeswax.views import safe_get_design

import csv
from django.http import HttpResponse
from rdbms.forms import UploadFileFormHDFS 
from desktop.lib.exceptions_renderable import PopupException

LOG = logging.getLogger(__name__)


def index(request):
  return execute_query(request)


def configuration_error(request, *args, **kwargs):
  return render('error.mako', request, {})


"""
Decorators
"""
def ensure_configuration(view_func):
  def _decorator(*args, **kwargs):
    if conf.DATABASES.get():
      return view_func(*args, **kwargs)
    else:
      return configuration_error(*args, **kwargs)
  return wraps(view_func)(_decorator)


"""
Queries Views
"""
@ensure_configuration
def execute_query(request, design_id=None, query_history_id=None):
  """
  View function for executing an arbitrary synchronously query.
  """
  action = request.path
  app_name = get_app_name(request)
  query_type = beeswax_models.SavedQuery.TYPES_MAPPING[app_name]
  design = safe_get_design(request, query_type, design_id)  

  if request.method == 'POST':
    form = UploadFileFormHDFS(request.POST, request.FILES)
  else:   
    form = UploadFileFormHDFS()

  return render('execute.mako', request, {
    'action': action,
    'doc_id': json.dumps(design.id and design.doc.get().id),
    'design': design,
    'autocomplete_base_url': reverse('rdbms:api_autocomplete_databases', kwargs={}),
    'can_edit_name': design.id and not design.is_auto,
    'frmHDFS': form
  })


@ensure_configuration
def save_design(request, save_form, query_form, type_, design, explicit_save=False):
  """
  save_design(request, save_form, query_form, type_, design, explicit_save) -> SavedQuery

  A helper method to save the design:
    * If ``explicit_save``, then we save the data in the current design.
    * If the user clicked the submit button, we do NOT overwrite the current
      design. Instead, we create a new "auto" design (iff the user modified
      the data). This new design is named after the current design, with the
      AUTO_DESIGN_SUFFIX to signify that it's different.

  Need to return a SavedQuery because we may end up with a different one.
  Assumes that form.saveform is the SaveForm, and that it is valid.
  """

  if type_ == beeswax_models.RDBMS:
    design_cls = SQLdesign
  else:
    raise ValueError(_('Invalid design type %(type)s') % {'type': type_})

  old_design = design
  design_obj = design_cls(query_form)
  new_data = design_obj.dumps()

  # Auto save if (1) the user didn't click "save", and (2) the data is different.
  # Don't generate an auto-saved design if the user didn't change anything
  if explicit_save:
    design.name = save_form.cleaned_data['name']
    design.desc = save_form.cleaned_data['desc']
    design.is_auto = False
  elif new_data != old_design.data:
    # Auto save iff the data is different
    if old_design.id is not None:
      # Clone iff the parent design isn't a new unsaved model
      design = old_design.clone()
      if not old_design.is_auto:
        design.name = old_design.name + beeswax_models.SavedQuery.AUTO_DESIGN_SUFFIX
    else:
      design.name = beeswax_models.SavedQuery.DEFAULT_NEW_DESIGN_NAME
    design.is_auto = True

  design.name = design.name[:64]
  design.type = type_
  design.data = new_data

  design.save()

  LOG.info('Saved %s design "%s" (id %s) for %s' % (design.name and '' or 'auto ', design.name, design.id, design.owner))

  if design.doc.exists():
    design.doc.update(name=design.name, description=design.desc)
  else:
    Document.objects.link(design, owner=design.owner, extra=design.type, name=design.name, description=design.desc)

  if design.is_auto:
    design.doc.get().add_to_history()

  return design

def download(request):  
  response = HttpResponse('')
  aHeaders = []
  aData = []
  aLine = []
  response = HttpResponse('')

  if request.method == 'POST':
    aHeaders = request.POST['pHeaders']
    aData = request.POST['pData']    
    file_format = 'csv' if 'csv' in request.POST else 'xls' if 'xls' in request.POST else 'json'

    #Output File Format.
    if file_format in ('csv','xls'):      
      if file_format == 'csv':
        contenttype = 'text/csv'
      else:
        contenttype = 'application/ms-excel'

      response = HttpResponse(content_type=contenttype)
      response['Content-Disposition'] = 'attachment; filename=%s_%s.%s' % ('file', file_format, file_format)        
      writer = csv.writer(response)
      writer.writerow(json.loads(aHeaders))
      for element in json.loads(aData):        
        aLine = []
        for line in element:
          if type(line) is unicode:
            line = line.encode('utf8')
          aLine.append(line)
        writer.writerow(aLine)

    if file_format == 'json':            
      contenttype = 'application/json'
      response = HttpResponse(aData, content_type=contenttype)
      response['Content-Disposition'] = 'attachment; filename=%s_%s.%s' % ('file', file_format, file_format)

  return response

def save_file(request):
  print "111"
  form = UploadFileFormHDFS(request.POST, request.FILES)
  print "222"
  sURL = request.POST['psURL']
  print "333"

  if request.META.get('upload_failed'):
    print "444"
    raise PopupException(request.META.get('upload_failed'))

  if form.is_valid():
    print "555"
    uploaded_file = request.FILES['hdfs_file']        

    username = request.user.username
    sFileNameHDFS = sFileHDFS.name
    sPathHDFS = "/user/" + username                 
    sPathHDFS = request.fs.join(sPathHDFS, sFileNameHDFS)  
    print "PATH: ",sPathHDFS
    tmp_file = uploaded_file.get_temp_path()
    print "TEMP: ",tmp_file

    try:
        # Remove tmp suffix of the file
        request.fs.do_as_user(username, request.fs.rename, tmp_file, sPathHDFS)
        print "GRABAR: ",tmp_file
        return HttpResponseRedirect(sURL)
    except IOError, ex:
        already_exists = False
        try:
            already_exists = request.fs.exists(sPathHDFS)
        except Exception:
          pass
        if already_exists:
            msg = _('Destination %(name)s already exists.')  % {'name': sPathHDFS}
        else:
            msg = _('Copy to %(name)s failed: %(error)s') % {'name': sPathHDFS, 'error': ex}
        raise PopupException(msg)
    
  else:
    print "aaa"
    raise PopupException(_("Error in upload form: %s") % (form.errors,))
