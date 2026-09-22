defmodule WynCommand.Networking.Host do
  @enforce_keys [:address]
  defstruct [
    :address,
    :name
  ]
end
