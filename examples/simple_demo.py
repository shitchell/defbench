import benchfunc

my_set = set()
my_list = list()

# fill both with data
for i in range(10000):
  my_set.add(i)
  my_list.append(i)

def search_set():
  global my_set
  return "hello" in my_set

def search_list():
  global my_list
  return "hello" in my_list

# run benchfunc tests
ss = benchfunc.run(search_set, repeat=1000)
print(ss)
print()

sl = benchfunc.run(search_list, repeat=1000)
print(sl)
