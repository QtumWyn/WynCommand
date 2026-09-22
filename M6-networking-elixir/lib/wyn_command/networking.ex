defmodule WynCommand.Networking do
  alias WynCommand.Networking.Host
  alias WynCommand.Networking.Checks.Runner

  def check(
        address,
        ports \\ [22, 80, 443]
      )
      when is_binary(address) and is_list(ports) do
    host = %Host{
      address: address
    }

    Runner.run(host, ports)
  end
end
