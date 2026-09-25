defmodule WynCommand.Networking.Diagnostics.Facts do
  alias WynCommand.Networking.Local.{Listener, SocketOwner}

  def from_listeners(listeners)
      when is_list(listeners) do
    listener_facts =
      listeners
      |> Enum.map(fn
        %Listener{port: port} ->
          "listener(#{port})."
      end)
      |> Enum.uniq()

    owner_facts =
      listeners
      |> Enum.flat_map(fn
        %Listener{
          port: port,
          owners: owners
        } ->
          Enum.map(
            owners,
            fn owner ->
              owner_fact(port, owner)
            end
          )
      end)
      |> Enum.uniq()

    (listener_facts ++ owner_facts)
    |> Enum.join("\n")
  end

  defp owner_fact(port, %SocketOwner{process: process}) do
    process = normalize_process_name(process)

    "owned_by(#{port}, #{process})."
  end

  defp normalize_process_name(name) do
    normalized =
      name
      |> String.downcase()
      |> String.replace(~r/[^a-z0-9_]+/, "_")
      |> String.trim("_")

    cond do
      normalized == "" -> "unknown process"
      Regex.match?(~r/^\d/, normalized) -> "process_#{normalized}"
      true -> normalized
    end
  end
end
