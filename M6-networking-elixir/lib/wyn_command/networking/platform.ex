defmodule WynCommand.Networking.Platform do
  alias WynCommand.Networking.Local.Listener

  @callback listeners() ::
              {:ok, [Listener.t()]}
              | {:error, term()}

  def current do
    case :os.type() do
      {:unix, :linux} ->
        WynCommand.Networking.Platform.Linux

      {:win32, :nt} ->
        WynCommand.Networking.Platform.Windows
    end
  end
end
