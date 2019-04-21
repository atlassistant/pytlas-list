from pytlas import intent, training, translations, meta
import pytlas.settings as settings
import json
import os
import unicodedata
import re
import smtplib
import sys
# This entity will be shared among training data since it's not language specific


@training('en')
def en_data(): return """
%[enumerate_list]
  what are my lists
  enumerate my lists

%[delete_list]
  delete list @[list_name]
  delete @[list_name]
  delete my list @[list_name]
  erase @[list_name]
  destroy @[list_name]
  put @[list_name] in the can
  trash list @[list_name]

%[add_item]
  add @[item_name] in list @[list_name]
  add @[item_name] in my @[list_name]
  add @[item_name] in the @[list_name]
  I want add something in my @[list_name]
  could you  add something in the @[list_name]

%[remove_item]
  remove @[item_name] from @[list_name]

%[display_list]
  what is the @[list_name] content
  show me the @[list_name] content
  show me my @[list_name]
  display my @[list_name]
  what I have in my @[list_name]

%[send_list]
  send to @[to_email] the list @[list_name]
  send the list @[list_name] to @[to_email] 
  send @[list_name] to @[to_email]

%[help_list]
  give me help on list skill
  give me advises on list skill
  how does the list skill work

@[list_name]
  shoping list
  todo list
  wish list
  christmas list
  gift list

@[item_name]
  garlic
  salt
  walk the dog
  call mother
  bread
  eggs
  trip
  do homework

@[to_email]
  first.name@domain.com
  me

"""

#@training('fr')
#def fr_data(): return """
#"""

#@translations('fr')
#def fr_translations(): return {
#}


def slugify(value):
  """
  Normalizes string, converts to lowercase, removes non-alpha characters,
  and converts spaces to hyphens.
  """
  slug_value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
  slug_value = re.sub(r'[^\w\s-]', '', slug_value).strip().lower()
  slug_value = re.sub(r'[-\s]+', '_', slug_value)
  return slug_value

def default_pytlas_list_path():
  return os.path.join(os.path.expanduser('~'),'.pytlas-list')

def build_list_file_path(list_name, list_dir_path):
  list_filename = slugify(list_name)+'.json'  
  list_path = os.path.join(list_dir_path,list_filename)
  return list_path

def create_blank_file(list_name, list_path):
  list_content = { 'name' : list_name, 'items' : [] }
  with open(list_path,'w') as json_file:
    json.dump(list_content, json_file)

def append_in_file(item_name, list_path):
  list_content = {}
  with open(list_path,'r') as json_file:
    list_content = json.load(json_file)
    list_content['items'].append(item_name)
  with open(list_path,'w') as json_file:
    json.dump(list_content, json_file)

def remove_from_file(item_name, list_path):
  list_content = {}
  with open(list_path,'r') as json_file:
    list_content = json.load(json_file)
    list_content['items'] = [x for x in list_content['items'] if x != item_name]
  with open(list_path,'w') as json_file:
    json.dump(list_content, json_file)


@meta()
def help_meta(_): return {
  'name': _('list'),
  'description': _('The skill which helps you to manage your TODO lists.'),
  'author': 'Jean-Michel LEKSTON',
  'version': '1.0.0',
  'homepage': 'https://github.com/atlassistant/pytlas-list',
}

@intent('enumerate_list')
def on_enumerate_list(req):
  list_dir_path = settings.get('path',section='pytlas_list')  
  if not list_dir_path:
    list_dir_path = default_pytlas_list_path()
  list_names = []
  for f in os.listdir(list_dir_path): 
    file_path = os.path.join(list_dir_path, f)
    if os.path.isfile(file_path) and os.path.splitext(file_path)[1] == '.json':
      with open(file_path,'r') as json_file:
        list_content = json.load(json_file)
        list_names.append(list_content['name'])
  if len(list_names) == 0:
    result = req._("I found no list")
  elif len(list_names) == 1:
    result = req._("I found only one list : {0}").format(list_names[0])
  else:
    found_list = ', '.join(list_names)
    result = req._("I found the following lists : {0}").format(found_list)

  req.agent.answer(result)
  return req.agent.done()

@intent('delete_list')
def on_delete_list(req):
  list_name = req.intent.slot('list_name').first().value
  if not list_name:
    return req.agent.ask('list_name',req._('In which list?'))
  list_dir_path = settings.get('path',section='pytlas_list')  
  if not list_dir_path:
    list_dir_path = default_pytlas_list_path()
  
  list_path = build_list_file_path(list_name, list_dir_path)
  if not os.path.exists(list_path):
    req.agent.answer(req._('Hummm! The list "{0}" seems not exists').format(list_name))
    return req.agent.done()    

  delete_confirmed = req.intent.slot('delete_confirmed').first().value
  yes = req._('Yes')
  no = req._('No')
  if not delete_confirmed:
    return req.agent.ask('delete_confirmed', req._('Would you like delete "{0}"?').format(list_name), [yes, no])
  
  if delete_confirmed == no:
    return req.agent.done()    
  
  try:
    os.remove(list_path)
  except:
    req.agent.answer(req._('Oops! Something bad append. I can\'t delete file "{0}"').format(list_path))
  return req.agent.done()    

@intent('add_item')
def on_add_item(req):
  list_name = req.intent.slot('list_name').first().value
  if not list_name:
    return req.agent.ask('list_name',req._('In which list?'))

  list_dir_path = settings.get('path',section='pytlas_list')  
  if not list_dir_path:
    list_dir_path = default_pytlas_list_path()
  
  list_path = build_list_file_path(list_name, list_dir_path)
  
  if not os.path.exists(list_path):
    create_confirmed = req.intent.slot('create_confirmed').first().value
    yes = req._('Yes')
    no = req._('No')
    if not create_confirmed:
      return req.agent.ask('create_confirmed', req._('Hummm! The list "{0}" seems not exists. Would you like create it?').format(list_name), [yes, no])
    
    if create_confirmed == no:
      return req.agent.done()    

    try:
      create_blank_file(list_name, list_path)
    except:
      req.agent.answer(req._('Oops! Something bad append. I can\'t create file "{0}"').format(list_path))
      return req.agent.done()    

  item_name = req.intent.slot('item_name').first().value
  if not item_name:
    return req.agent.ask('item_name', req._('What do you want to add in your list?'))

  try:
    append_in_file(item_name, list_path)
  except:
    req.agent.answer(req._('Oops! Something bad append. I can\'t add "{0}" in file "{1}"').format(item_name, list_path))
    return req.agent.done()    

  req.agent.answer(req._('Ok, "{0}" has been added in your list "{1}"').format(item_name, list_name))
  return req.agent.done()

@intent('remove_item')
def on_remove_item(req):
  list_name = req.intent.slot('list_name').first().value
  if not list_name:
    return req.agent.ask('list_name',req._('From which list?'))

  list_dir_path = settings.get('path',section='pytlas_list')  
  if not list_dir_path:
    list_dir_path = default_pytlas_list_path()
  
  list_path = build_list_file_path(list_name, list_dir_path)
  if not os.path.exists(list_path):
    req.agent.answer(req._('Hummm! The list "{0}" seems not exists').format(list_name))
    return req.agent.done()    

  item_name = req.intent.slot('item_name').first().value
  if not item_name:
    return req.agent.ask('item_name', req._('What do you want remove from your list?'))

  try:
    remove_from_file(item_name, list_path)
  except:
    req.agent.answer(req._('Oops! Something bad append. I can\'t remove "{0}" from file "{1}"').format(item_name, list_path))
    return req.agent.done()    

  req.agent.answer(req._('Ok, "{0}" has been removed from your list "{1}"').format(item_name, list_name))
  return req.agent.done()


@intent('display_list')
def on_display_list(req):
  list_name = req.intent.slot('list_name').first().value
  if not list_name:
    return req.agent.ask('list_name',req._('Which list?'))
  
  list_dir_path = settings.get('path',section='pytlas_list')
  if not list_dir_path:
    list_dir_path = default_pytlas_list_path()
  
  list_path = build_list_file_path(list_name, list_dir_path)
  if not os.path.exists(list_path):
    req.agent.answer(req._('Hummm! The list "{0}" seems not exists.').format(list_name))
    return req.agent.done()
  
  list_content = {}
  try:
    with open(list_path,'r') as json_file:
      list_content = json.load(json_file)
  except:
    req.agent.answer(req._('Oops! Something bad append. I can\'t open the file "{0}"').format(list_path))
    return req.agent.done()    

  req.agent.answer(req._('Your list "{0}" contains : {1}').format(list_content['name'], ', '.join(list_content['items'])))
  return req.agent.done()    

@intent('send_list')
def on_send_list(req):
  list_name = req.intent.slot('list_name').first().value
  if not list_name:
    return req.agent.ask('list_name',req._('Which list?'))
  
  list_dir_path = settings.get('path',section='pytlas_list')  
  if not list_dir_path:
    list_dir_path = default_pytlas_list_path()
  
  list_path = build_list_file_path(list_name, list_dir_path)
  
  if not os.path.exists(list_path):
    req.agent.answer(req._('Hummm! The list "{0}" seems not exists.').format(list_name))
    return req.agent.done()
  
  
  from_email = req.intent.slot('from_email').first().value
  if not from_email:
    from_email = settings.get('from_email',section='pytlas_list')
  if not from_email:
    return req.agent.ask('from_email',req._('Please tell me from which email address'))

  to_email = req.intent.slot('to_email').first().value
  if not to_email:
    return req.agent.ask('to_email',req._('Please tell to which email address'))
  
  if to_email == "me":
    to_email = from_email  

  smtp_address = req.intent.slot('smtp_address').first().value
  if not smtp_address:
    smtp_address = settings.get('smtp_address',section='pytlas_list')
  if not smtp_address:
    return req.agent.ask('smtp_address',req._('Please give me the smtp server address'))

  smtp_login = req.intent.slot('smtp_login').first().value
  if not smtp_login:
    smtp_login = settings.get('smtp_login',section='pytlas_list')
  if not smtp_login:
    return req.agent.ask('smtp_login',req._('Please give me the smtp server login'))

  smtp_pwd = req.intent.slot('smtp_pwd').first().value
  if not smtp_pwd:
    smtp_pwd = settings.get('smtp_pwd',section='pytlas_list')
  if not smtp_pwd:
    return req.agent.ask('smtp_pwd',req._('Please give me the smtp server pwd'))

  list_content = {}
  try:
    with open(list_path,'r') as json_file:
      list_content = json.load(json_file)
  except:
    req.agent.answer(req._('Oops! Something bad append. I can\'t open the file "{0}"').format(list_path))
    return req.agent.done()    

  msg = "\n"
  msg = msg + list_content['name'] + "\n"
  msg = msg + "=" *  len(list_content['name']) + "\n"
  for item in list_content['items']:
    msg = msg + "-[ ]" + item + "\n"

  # print('sending to {0} from {1} on {2} using credential {3} {4} of \n{5}'.format(to_email, from_email, smtp_address, smtp_login, smtp_pwd, msg))
  
  try:
    server = smtplib.SMTP(smtp_address+":587")
    server.ehlo()
    server.starttls()
    #Next, log in to the server
    server.login(smtp_login, smtp_pwd)
    #Send the mail
    server.sendmail(from_email, to_email, msg)
    server.quit()
  except:
    req.agent.answer(req._('Hummm! Email sending failed. Cause : {0}.').format(sys.exc_info()[0]))
    return req.agent.done()

  req.agent.answer(req._('Email successfully sent.'))
  return req.agent.done()


