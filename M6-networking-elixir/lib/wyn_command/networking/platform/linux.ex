defmodule WynCommand.Networking.Platform.Linux do
  @behaviour WynCommand.Networking.Platform

  alias WynCommand.Networking.Local.{Listener, SocketOwner}

  @impl true
  def listeners do
    case System.cmd(
           "ss",
           ["-H", "-ltnp"],
           stderr_to_stdout: true
         ) do
      {output, 0} ->
        {:ok, parse_listeners(output)}

      {output, exit_code} ->
        {:error,
         %{
           exit_code: exit_code,
           output: output
         }}
    end
  end

  defp parse_listeners(output) do
    output
    |> String.split("\n", trim: true)
    |> Enum.map(&parse_listener/1)
    |> Enum.reject(&is_nil/1)
  end

  defp parse_listener(line) do
    columns =
      String.split(
        line,
        ~r/\s+/,
        parts: 6
      )

    case columns do
      [
        "LISTEN",
        _recv_q,
        _send_q,
        local_address,
        _peer_address,
        process_info
      ] ->
        parse_local_address(
          local_address,
          process_info
        )

      [
        "LISTEN",
        _recv_q,
        _send_q,
        local_address,
        _peer_address
      ] ->
        parse_local_address(
          local_address,
          nil
        )

      _ ->
        nil
    end
  end

  defp parse_local_address(local_address, process_info) do
    case Regex.run(~r/^(.*):(\d+)$/, local_address) do
      [_, address, port_text] ->
        %Listener{
          protocol: :tcp,
          address: normalize_address(address),
          port: String.to_integer(port_text),
          state: :listen,
          owners: parse_owners(process_info)
        }

      nil ->
        nil
    end
  end

  defp normalize_address(address) do
    address
    |> String.trim_leading("[")
    |> String.trim_trailing("]")
  end

  defp parse_owners(nil) do
    []
  end

  defp parse_owners(process_info) do
    Regex.scan(
      ~r/"([^"]+)",pid=(\d+),fd=(\d+)/,
      process_info
    )
    |> Enum.map(fn [_, process, pid_text, fd_text] ->
      %SocketOwner{
        process: process,
        pid: String.to_integer(pid_text),
        fd: String.to_integer(fd_text)
      }
    end)
  end
end
