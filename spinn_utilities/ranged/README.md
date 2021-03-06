These classes present a RangeMapping Matrix implementation

The main dimension is ids which must be zero based continuous int values.
This dimension supports the main list functions.

The second dimension is keys which must be Strings.
This dimension supports the main dict methods.

**USAGE**
1. Create a RangeDict
    data = RangeDictionary(size=x)

2. Add Lists to the range by.

a. Setting all the values the same so
    data["foo"] = foo_value

b. Setting using a list of size x

    foo_list = range(x)

    data["foo"] = foo_list          

c. Setting using something that implements next(n) to return n objects

    data["foo"] = foo_creator

    \# Same result as

    foo_list = foo_creator.next(n)

    data["foo"] = foo_list          

d. create a new list by operating over two lists

    data["foo"] = foo...

    data["bar"] = bar...

    data["add"] = data["foo"] + data["bar"]
    

e. create a new list by applying operation to a list

    data["foo"] = foo...

    data["2_foo"] = data["foo"].apply_operation(lambda x: x * 2)        

3.  Changing the value of an existing list is saver via

    data.set_value(key="foo", value=foo...)      

    \# There are also set_value by id, by slice and by ids methods    

    \# You can not set the values of a derived list
    
    \# Changing the values for a list also effects the lists derived from it.
    
4. Get the values as a list like Object
   
   data["foo"]          
    
    
**NOTE**: As Dictionary value and item methods expect to return a single value,
where the result would result in multiple values an Exception is raised.

**WARNING**:
len and \_\_len\_\_ are id based. Use len_keys for dict len.
iter and \_\_iter\_\_ will also iterate over the id dimension,
Use iterkeys(), itervalues(), iteritems() for the dict dimension

get, \_\_getitem\_\_, set, \_\_setitem\_\_ and \_\_contains\_\_() 
 will use the type of the key to determine the dimensions. 
int, \[int\] and slice will be ids
str will be dict based all others will cause an error

Methods that reduce the size of a dimension are not supported
including \_\_delitem\_\_, \_\_delslice\_\_, clear(), pop(), popitem(), remove()

Methods that increase the size of a dimension are not supported
including extend, append, and \_\_set\_\_ with a new key
One exception is that Dict[str] = xyz is supported as only as Dict is an 
original and not a view

Methods that change the order of a list are not supported
including reverse and sort

dict's view methods viewvalues() and viewitems() are not supported
viewkeys is supported but as keys may not changes makes little sense.
However a slice by id is a view so items() and values() methods  
will return the latest results even if changes after the slice was created.

See AbstractDict.py for extra methods that the whole dictionary and view support
These include:

The Only numerical operation that are supported are +. -, *, / and //
Where two dict[str] objects (lists) are combined to form a new list  
