defmodule WynCommand.Networking.Local.Listener do
  alias WynCommand.Networking.Local.SocketOwner

  @enforce_keys [
    :protocol,
    :address,
    :port,
    :state
  ]

  defstruct [
    :protocol,
    :address,
    :port,
    :state,
    owners: [],
    metadata: %{}
  ]

  @type t :: %__MODULE__{
          protocol: atom(),
          address: String.t(),
          port: non_neg_integer(),
          state: atom(),
          owners: [SocketOwner.t()],
          metadata: map()
        }
end
