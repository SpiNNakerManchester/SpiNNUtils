These classes present a RangeMapping Matrix implementaion

The main dimension is ids which must be zero based continious int values.
This dimension supports the main list funtions.

The second dimension is keys which must be Strings.
This dimension supports the main dict methods.

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
One exception is that Dict[str] = xyz is supported as only as Dict is an orginal and not a view

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
