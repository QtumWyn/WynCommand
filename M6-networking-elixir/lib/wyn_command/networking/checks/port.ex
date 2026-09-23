defmodule WynCommand.Networking.Checks.Port do
  alias WynCommand.Networking.{Host, Result}

  @default_timeout_ms 1000

  def run(
        %Host{} = host,
        port,
        timeout_ms \\ @default_timeout_ms
      )
      when is_integer(port) and
             port in 1..65_535 and
             is_integer(timeout_ms) and
             timeout_ms > 0 do
    started_at = System.monotonic_time(:millisecond)

    connection_result =
      :gen_tcp.connect(
        String.to_charlist(host.address),
        port,
        [:binary, active: false],
        timeout_ms
      )

    finished_at = System.monotonic_time(:millisecond)

    duration_ms = finished_at - started_at

    build_result(
      host,
      port,
      connection_result,
      duration_ms
    )
  end

  defp build_result(
         host,
         port,
         {:ok, socket},
         duration_ms
       ) do
    :gen_tcp.close(socket)

    %Result{
      check: :tcp_port,
      target: host.address,
      status: :ok,
      message: "TCP port #{port} is open",
      duration_ms: duration_ms,
      metadata: %{
        port: port,
        protocol: :tcp
      }
    }
  end

  defp build_result(
         host,
         port,
         {:error, reason},
         duration_ms
       ) do
    %Result{
      check: :tcp_port,
      target: host.address,
      status: :error,
      message: "TCP port #{port} is not reachable",
      duration_ms: duration_ms,
      metadata: %{
        port: port,
        protocol: :tcp,
        reason: reason
      }
    }
  end
end
