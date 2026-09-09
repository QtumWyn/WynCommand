defmodule WynCommand.NetworkingTest do
  use ExUnit.Case
  doctest WynCommand.Networking

  test "greets the world" do
    assert WynCommand.Networking.hello() == :world
  end
end
