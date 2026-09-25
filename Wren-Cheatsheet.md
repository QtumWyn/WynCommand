# Wren Quick Reference

## Thinking in Wren

Wren = policy/configuration/workflow scripting

## Comments

```wren
// Single line

/*
   Multi-line
*/
```

## Variables

```wren
var name = "Wyn"
var port = 8080
var enabled = true
var nothing = null
```

## Printing

```wren
System.print("Hello!")
System.print(port)
```

## String Interpolation

```wren
System.print("Port: %(port)")
System.print("Hello, %(name)")
```

## Basic Values

```wren
var integer = 42
var decimal = 3.14
var text = "hello"
var yes = true
var no = false
var empty = null
```

## Lists

```wren
var ports = [22, 80, 443]

System.print(ports[0])

ports.add(8080)

System.print(ports.count)

for (port in ports) {
  System.print(port)
}
```

## Negative Indexes

```wren
System.print(ports[-1])  // last element
```

## Maps

```wren
var services = {
  "ssh": 22,
  "http": 80,
  "https": 443
}

System.print(services["ssh"])

services["postgres"] = 5432
```

## If / Else

```wren
if (port == 443) {
  System.print("HTTPS")
} else if (port == 80) {
  System.print("HTTP")
} else {
  System.print("Other")
}
```

## While

```wren
var i = 0

while (i < 5) {
  System.print(i)
  i = i + 1
}
```

## For

```wren
for (port in ports) {
  System.print(port)
}
```

## Ranges

```wren
// inclusive
for (i in 1..5) {
  System.print(i)
}

// exclusive endpoint
for (i in 1...5) {
  System.print(i)
}
```

## Functions

```wren
var double = Fn.new {|number|
  return number * 2
}

System.print(double.call(5))


// Short single-expression function

var square = Fn.new {|number| number * number }
```

## Classes

```wren
class Host {
  construct new(address, ports) {
    _address = address
    _ports = ports
  }

  address {
    return _address
  }

  ports {
    return _ports
  }

  describe() {
    System.print("Host: %(_address)")
  }
}

var host = Host.new("1.1.1.1", [80, 443])

host.describe()

System.print(host.address)
```

## Static Method

```wren
class Profiles {
  static web() {
    return [80, 443]
  }
}

var webPorts = Profiles.web()
```

## Importing Modules

```wren
import "profiles" for Profiles

var ports = Profiles.web()
```

## Brain Map

```text
var                 declare variable

[1, 2, 3]           list

{"a": 1}            map

object.method()      method call

Fn.new {|x| ... }   anonymous function

function.call(x)    invoke Fn object

class Foo { }       class

construct new(...)  constructor

static method()     class/static method

_name               instance field

1..5                inclusive range

1...5               exclusive range

%(value)             string interpolation

null                 no value
```
