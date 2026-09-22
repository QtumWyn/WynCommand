defmodule WynCommand.Networking.Checks.Runner do
  alias WynCommand.Networking.Host
  alias WynCommand.Networking.Checks.{Ping, Port}

  def run(
        %Host{} = host,
        ports \\ [22, 80, 443]
      ) when is_list(ports) do
    ping_result = Ping.run(host)
    # Conceptually:
    # [
    #   Port.run(host, 22),
    #   Port.run(host, 80),
    #   Port.run(host, 443)
    # ]
    port_results =
      Enum.map(ports, fn port ->
        Port.run(host, port)
      end)

    [ping_result | port_results]
  end
end
