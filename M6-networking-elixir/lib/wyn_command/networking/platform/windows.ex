defmodule WynCommand.Networking.Platform.Windows do
  @behaviour WynCommand.Networking.Platform

  @impl true
  def listeners do
    {:error, :not_implemented}
  end
end
