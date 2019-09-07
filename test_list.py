from sure import expect
from pytlas.settings import CONFIG
from pytlas.testing import create_skill_agent
from nose import with_setup
import os
import shutil

agent = None

def get_test_tmp_folder_path():
  base_path = os.path.dirname(__file__)
  test_tmp_folder_path = os.path.join(base_path,'.test_tmp_folder')
  return test_tmp_folder_path

def remove_test_tmp_folder():
  test_tmp_folder_path = get_test_tmp_folder_path()
  if os.path.exists(test_tmp_folder_path):
    shutil.rmtree(test_tmp_folder_path)

def create_test_tmp_folder():
  test_tmp_folder_path = get_test_tmp_folder_path()
  if not os.path.exists(test_tmp_folder_path):
    os.makedirs(test_tmp_folder_path)

def read_text_file(text_file_path):
  text = ""
  with open(text_file_path,'r') as text_file:
    for line in text_file: text += line
  return line

def setup_module(module):
  global agent
  remove_test_tmp_folder()
  test_tmp_folder_path = get_test_tmp_folder_path()
  CONFIG.set('path',test_tmp_folder_path,section='pytlas_list')
  agent = create_skill_agent(os.path.dirname(__file__), lang='en')
 
def teardown_module(module):
  remove_test_tmp_folder()

def my_setup_function():
  create_test_tmp_folder()
  agent.model.reset()

def my_teardown_function():
  remove_test_tmp_folder()
 
@with_setup(my_setup_function, my_teardown_function)
def test_add_items_in_new_shopping_list():
  agent.parse('add pizza in my shopping list')
  call = agent.model.on_ask.get_call()
  expect(call.text).to.equal('Hummm! The list "{0}" seems not exists. Would you like create it?'.format('shopping list'))
  agent.parse('Yes')
  list_path = os.path.join(get_test_tmp_folder_path(),'shopping_list.json')
  expect(os.path.exists(list_path)).to.equal(True)
  expected_list_text = '{"name": "shopping list", "items": ["pizza"]}'
  list_text = read_text_file(list_path)
  expect(list_text).to.equal(expected_list_text)
  call = agent.model.on_answer.get_call()
  expect(call.text).to.equal('Ok, "{0}" has been added in your list "{1}"'.format('pizza', 'shopping list'))

@with_setup(my_setup_function, my_teardown_function)
def test_injection_attack_prevention():
  agent.parse('add "3l33t" in ../../etc/pwd')
  call = agent.model.on_ask.get_call()
  expect(call.text).to.equal('Hummm! The list "{0}" seems not exists. Would you like create it?'.format('pwd'))
  agent.parse('Yes')
  list_path = os.path.join(get_test_tmp_folder_path(),'pwd.json')
  expect(os.path.exists(list_path)).to.equal(True)

@with_setup(my_setup_function, my_teardown_function)
def test_add_item_in_new_shopping_list_in_invalid_folder():
  remove_test_tmp_folder()
  agent.parse('add pizza in my shopping list')
  agent.parse('Yes')
  call = agent.model.on_answer.get_call()
  expect(call.text.startswith('Oops! Something bad append. I can\'t create file')).to.equal(True)

@with_setup(my_setup_function, my_teardown_function)
def test_add_items_in_existing_todo_list():
  list_path = os.path.join(get_test_tmp_folder_path(),'todo_list.json')
  agent.parse('add clean bedroom in my todo list')
  agent.parse('Yes')
  agent.model.reset()
  agent.parse('add do homework in my todo list')
  expected_list_text = '{"name": "todo list", "items": ["clean bedroom", "do homework"]}'
  list_text = read_text_file(list_path)
  expect(list_text).to.equal(expected_list_text)
  call = agent.model.on_answer.get_call()
  expect(call.text).to.equal('Ok, "{0}" has been added in your list "{1}"'.format('do homework', 'todo list'))
  agent.model.reset()
  agent.parse('add play doom in my todo list')
  expected_list_text = '{"name": "todo list", "items": ["clean bedroom", "do homework", "play doom"]}'
  list_text = read_text_file(list_path)
  expect(list_text).to.equal(expected_list_text)
  call = agent.model.on_answer.get_call()
  expect(call.text).to.equal('Ok, "{0}" has been added in your list "{1}"'.format('play doom', 'todo list'))
  agent.parse('add play doom in my todo list')
  expected_list_text = '{"name": "todo list", "items": ["clean bedroom", "do homework", "play doom", "play doom"]}'
  list_text = read_text_file(list_path)
  expect(list_text).to.equal(expected_list_text)
  call = agent.model.on_answer.get_call()
  expect(call.text).to.equal('Ok, "{0}" has been added in your list "{1}"'.format('play doom', 'todo list'))

@with_setup(my_setup_function, my_teardown_function)
def test_remove_items_from_friend_list():
  agent.parse('add bill in my friends list')
  agent.parse('Yes')
  agent.parse('add tricia in my friends list')
  agent.parse('add donald in my friends list')
  agent.parse('add donald in my friends list')
  agent.parse('add julien in my friends list')
  agent.model.reset()
  agent.parse('remove donald from my friends list')
  list_path = os.path.join(get_test_tmp_folder_path(),'friends_list.json')
  list_text = read_text_file(list_path)
  expected_list_text = '{"name": "friends list", "items": ["bill", "tricia", "julien"]}'
  expect(list_text).to.equal(expected_list_text)  
  call = agent.model.on_answer.get_call()
  expect(call.text).to.equal('Ok, "{0}" has been removed from your list "{1}"'.format('donald', 'friends list'))
  agent.model.reset()
  agent.parse('remove steven from my friends list')
  call = agent.model.on_answer.get_call()
  expect(call.text).to.equal('Ok, "{0}" has been removed from your list "{1}"'.format('steven', 'friends list'))
  agent.model.reset()
  agent.parse('remove bill from my colleagues list')
  call = agent.model.on_answer.get_call()
  expect(call.text).to.equal('Hummm! The list "{0}" seems not exists'.format('colleagues list'))


@with_setup(my_setup_function, my_teardown_function)
def test_delete_toto_list():
  agent.parse('delete todo list')
  call = agent.model.on_answer.get_call()
  expect(call.text).to.equal('Hummm! The list "{0}" seems not exists'.format('todo list'))
  agent.model.reset()
  agent.parse('add do homeworks in todo list')
  agent.parse('yes')
  list_path = os.path.join(get_test_tmp_folder_path(),'todo_list.json')
  expect(os.path.exists(list_path)).to.equal(True)
  agent.model.reset()  
  agent.parse('delete todo list')
  call = agent.model.on_ask.get_call()
  expect(call.text).to.equal('Would you like delete "{0}"?'.format('todo list'))
  agent.parse('no')
  expect(os.path.exists(list_path)).to.equal(True)  
  agent.parse('delete todo list')
  agent.parse('yes')
  expect(os.path.exists(list_path)).to.equal(False)  


@with_setup(my_setup_function, my_teardown_function)
def test_enumerate_list():
  agent.parse('enumerate lists')
  call = agent.model.on_answer.get_call()
  expect(call.text).to.equal('I found no list')
  agent.parse('add do homeworks in todo list')
  agent.parse('yes')
  agent.model.reset()
  agent.parse('enumerate lists')
  call = agent.model.on_answer.get_call()
  expect(call.text).to.equal("I found only one list : {0}".format('todo list'))
  agent.parse('add eggs in shopping list')
  agent.parse('yes')
  agent.model.reset()
  agent.parse('enumerate lists')
  call = agent.model.on_answer.get_call()
  expect(call.text).to.match("I found the following lists : (shopping|todo) list, (shopping|todo) list")

@with_setup(my_setup_function, my_teardown_function)
def test_display_list():
  agent.parse('show me the shopping list content')
  call = agent.model.on_answer.get_call()
  expect(call.text).to.equal('Hummm! The list "{0}" seems not exists.'.format('shopping list'))
  agent.parse('add do homework in my todo list')
  agent.parse('yes')
  agent.parse('add clean bedroom in my todo list')
  agent.model.reset()
  agent.parse('show me the todo list content')
  call = agent.model.on_answer.get_call()
  expected_list_text = 'Your list "{0}" contains : {1}'.format('todo list', 'do homework, clean bedroom')
  expect(call.text).to.equal(expected_list_text)