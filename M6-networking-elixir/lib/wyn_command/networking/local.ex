defmodule WynCommand.Networking.Local do
  alias WynCommand.Networking.Platform

  def listeners do
    platform = Platform.current()
    platform.listeners()
  end
end
