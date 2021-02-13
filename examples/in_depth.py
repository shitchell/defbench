import requests
import defbench
from pprint import pprint

my_set = set()
my_list = list()
filled_list = [None]*10000

def populate_set(count: int = 20):
  global my_set
  for i in range(count):
    my_set.add(str(i))

def populate_list(count: int = 20):
  global my_list
  for i in range(count):
    my_list.append(str(i))

def refill_list(count: int = 20):
  global filled_list
  max = len(filled_list)
  index = 0
  for i in range(count):
    if i >= max:
      index = 0
    filled_list[index] = index
    index += 1

def refill_list_nocheck(count: int = 20):
  global filled_list
  for i in range(count):
    filled_list[i] = i

def search_set():
  global my_set
  return "hello" in my_set

def search_list():
  global my_list
  return "hello" in my_list

def print_stuff():
  print('hello world')

def fetch_resource():
  # The following resource is a 4.8MB text file
  url = 'https://raw.githubusercontent.com/dwyl/english-words/master/words.txt'
  words = requests.get(url).text

fr = defbench.run(fetch_resource)
print(fr)
print()

# first argument is the function to test,
# second argument (optional) is number of times
# to run the method
ps = defbench.run(populate_set, repeat=10000)
print(ps)
print()

# if you want, you can name the test
pl = defbench.run(populate_list, repeat=10000, name="create list[20] x10000 ")
print(pl)
print()

# if you want to run a function with arguments,
# create a lambda function like so:
pl_args = defbench.run(lambda: populate_list(1000), repeat=100)
print(pl_args)
print()

# notice that using lambda causes the function to be
# named "<lambda>" in the output. you can use the name
# parameter to fix that
pl_named = defbench.run(lambda: populate_list(10000), repeat=100, name="populate list[10000]")
print(pl_named)
print()

ps_named = defbench.run(lambda: populate_set(10000), repeat=100, name="populate set[10000]")
print(ps_named)
print()

rl_named = defbench.run(lambda: refill_list(10000), repeat=100, name="refill list[10000]")
print(rl_named)
print()

rln_named = defbench.run(lambda: refill_list_nocheck(10000), repeat=100, name="refill nocheck[10000]")
print(rln_named)
print()

ss = defbench.run(search_set, repeat=100)
print(ss)
print()

sl = defbench.run(search_list, repeat=100)
print(sl)
print()

# if your function prints output, defbench will
# suppress it while running the test. access it
# with the `.stdout` attribute
pstuff = defbench.run(print_stuff, repeat=5)
print(pstuff)
if pstuff.stdout:
  print('---stdout---')
  print(pstuff.stdout)
  print('------------')
print()

# get the average time of all tests
avg = defbench.history.average_time()
print(f"total avg: {avg:.5}s")

# print all the tests
pprint(defbench.history.get())
