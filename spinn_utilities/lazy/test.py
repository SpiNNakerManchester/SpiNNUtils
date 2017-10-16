from spinn_utilities.lazy.range_dictionary import RangeDictionary

defaults = {"alpha": "a", "beta": 2}

rd = RangeDictionary(5, defaults)

print rd

print rd[2]
print rd[2: 4]
print rd[1: 3: 2]
print rd[1, 3]
print rd[1, "a"]
