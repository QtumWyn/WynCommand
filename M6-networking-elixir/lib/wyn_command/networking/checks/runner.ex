defmodule WynCommand.Networking.Checks.Runner do
  alias WynCommand.Networking.Host
  alias WynCommand.Networking.Checks.{Ping, Port}

  def run(
        %Host{} = host,
        ports \\ [22, 80, 443]
      )
      when is_list(ports) do
    checks =
      [
        fn ->
          Ping.run(host)
        end
        | Enum.map(ports, fn port ->
            fn ->
              Port.run(host, port)
            end
          end)
      ]

    checks
    |> Task.async_stream(
      fn check ->
        check.()
      end,
      ordered: true,
      timeout: 2_000
    )
    |> Enum.map(fn
      {:ok, result} ->
        result

      {:exit, reason} ->
        {:task_failed, reason}
    end)
  end
end
