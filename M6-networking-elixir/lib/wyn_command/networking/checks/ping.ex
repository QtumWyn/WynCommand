defmodule WynCommand.Networking.Checks.Ping do
  alias(WynCommand.Networking.{Host, Result})

  def run(%Host{} = host) do
    started_at = System.monotonic_time(:millisecond)

    {output, exit_code} =
      System.cmd(
        "ping",
        ping_arguments(host.address),
        stderr_to_stdout: true
      )

    finished_at = System.monotonic_time(:millisecond)

    duration_ms = finished_at - started_at

    build_result(host, output, exit_code, duration_ms)
  end

  defp ping_arguments(address) do
    case :os.type() do
      {:unix, :linux} ->
        ["-c", "1", "-W", "1", address]

      {:win32, :nt} ->
        ["-n", "1", "-w", "1000", address]
    end
  end

  defp build_result(host, output, 0, duration_ms) do
    %Result{
      check: :ping,
      target: host.address,
      status: :ok,
      message: "Host responded",
      duration_ms: duration_ms,
      metadata: %{
        output: output
      }
    }
  end

  defp build_result(host, output, exit_code, duration_ms) do
    %Result{
      check: :ping,
      target: host.address,
      status: :error,
      message: "Host did not respond",
      duration_ms: duration_ms,
      metadata: %{
        exit_code: exit_code,
        output: output
      }
    }
  end
end
