defmodule WynCommand.Networking.Local.SocketOwner do
  @enforce_keys [
    :pid,
    :process,
    :fd
  ]

  defstruct [
    :pid,
    :process,
    :fd
  ]

  @type t :: %__MODULE__{
          pid: non_neg_integer(),
          process: String.t(),
          fd: non_neg_integer()
        }
end
