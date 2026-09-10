// Wren syntax-highlighting test

class Host {
  construct new(name, address) {
    _name = name
    _address = address
  }

  describe() {
    System.print("%(_name) [%(_address)]")
  }
}

var host = Host.new("itpc", "100.85.29.94")

host.describe()

class Test {
    }