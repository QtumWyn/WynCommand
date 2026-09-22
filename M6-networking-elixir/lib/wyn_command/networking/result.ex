defmodule WynCommand.Networking.Result do
  @enforce_keys [:check, :target, :status]
  defstruct [
    :check,
    :target,
    :status,
    :message,
    :duration_ms,
    metadata: %{}
  ]
end
