# Elixir Quick Reference

## Thinking in Elixir

1. = means match, not merely assignment.
2. Prefer pattern matching and function clauses over giant conditional trees.
3. Think of |> as data flowing through transformations.
4. Data is immutable, so you produce transformed values rather than modifying them in place.
5. BEAM processes are cheap enough that concurrency is often an architectural tool, not an exotic optimization.

## Comments

```elixir
# single-line comment
```

## Basic Values

```elixir
name = "Wyn"
port = 443
enabled = true
nothing = nil

atom = :tcp
status = :ok
```

## Strings

```elixir
"hello"

"Port #{port}"
```

## Charlist

```elixir
~c"hello"
```

## List

```elixir
ports = [22, 80, 443]

[head | tail] = ports
```

## Tuple

```elixir
{:ok, result}

{:error, :timeout}
```

## Map

```elixir
host = %{
  address: "1.1.1.1",
  port: 443
}

host.address
host[:address]
```

## Keyword List

```elixir
options = [
  timeout: 1000,
  ordered: true
]
```

## Struct

```elixir
defmodule Host do
  @enforce_keys [:address]

  defstruct [
    :address,
    :name,
    ports: []
  ]
end


host =
  %Host{
    address: "1.1.1.1",
    name: "Cloudflare"
  }
```

## Function

```elixir
def add(a, b) do
  a + b
end
```

## One-Line Function

```elixir
def add(a, b), do: a + b
```

## Private Function

```elixir
defp parse_result(result) do
  result
end
```

## Default Argument

```elixir
def scan(host, timeout \\ 1000) do
  ...
end


# run/2 means:
#
# function = run
# arity    = 2
```

## Anonymous Function

```elixir
double =
  fn number ->
    number * 2
  end

double.(5)
```

## Capture Syntax

```elixir
Enum.map(numbers, &double/1)

Enum.map(numbers, &(&1 * 2))
```

## Pattern Matching

```elixir
{:ok, result} = some_function()
```

## Multiple Function Clauses

```elixir
def handle({:ok, result}) do
  result
end

def handle({:error, reason}) do
  reason
end
```

## Struct Pattern

```elixir
def run(%Host{} = host) do
  ...
end
```

## Guards

```elixir
def scan(port)
    when is_integer(port) and
           port > 0 do
  ...
end
```

## Case

```elixir
case result do
  {:ok, value} ->
    value

  {:error, reason} ->
    reason
end
```

## Cond

```elixir
cond do
  port == 80 ->
    :http

  port == 443 ->
    :https

  true ->
    :unknown
end
```

## If

```elixir
if port == 443 do
  :https
else
  :other
end
```

## Pipeline

```elixir
output
|> String.split("\n")
|> Enum.map(&parse_line/1)
|> Enum.reject(&is_nil/1)


# Equivalent idea:

Enum.reject(
  Enum.map(
    String.split(output, "\n"),
    &parse_line/1
  ),
  &is_nil/1
)
```

## Enum

```elixir
Enum.map([1, 2, 3], fn x ->
  x * 2
end)

Enum.filter(ports, fn port ->
  port > 100
end)

Enum.reject(values, &is_nil/1)

Enum.each(ports, &IO.inspect/1)

Enum.count(ports)

Enum.member?(ports, 443)

Enum.reduce([1, 2, 3], 0, fn number, acc ->
  acc + number
end)
```

## Modules

```elixir
defmodule WynCommand.Networking do
  ...
end
```

## Alias

```elixir
alias WynCommand.Networking.Host

alias WynCommand.Networking.Checks.{
  Ping,
  Port
}
```

## Type

```elixir
@type t :: %__MODULE__{
        port: integer(),
        status: atom()
      }
```

## Spec

```elixir
@spec listeners() ::
        {:ok, [Listener.t()]}
        | {:error, term()}
```

## Callback

```elixir
@callback listeners() ::
            {:ok, [Listener.t()]}
```

## Behaviour

```elixir
@behaviour WynCommand.Networking.Platform
```

## Callback Implementation

```elixir
@impl true
def listeners do
  ...
end
```

## System Command

```elixir
{output, exit_code} =
  System.cmd(
    "ping",
    ["-c", "1", "1.1.1.1"],
    stderr_to_stdout: true
  )
```

## Erlang Function

```elixir
:os.type()

:gen_tcp.connect(
  ~c"1.1.1.1",
  443,
  [:binary, active: false],
  1000
)
```

## Task

```elixir
task =
  Task.async(fn ->
    expensive_work()
  end)

result =
  Task.await(task)
```

## Concurrent Map

```elixir
results =
  ports
  |> Task.async_stream(
    fn port ->
      Port.run(host, port)
    end,
    ordered: true,
    timeout: 2000
  )
  |> Enum.to_list()
```

## Raw Beam Process

```elixir
pid =
  spawn(fn ->
    receive do
      message ->
        IO.inspect(message)
    end
  end)

send(pid, :hello)
```

## Brain Map

```text
=                       pattern match

==                      equality

===                     strict equality

:thing                  atom

{:ok, value}            tuple

[head | tail]           linked-list decomposition

%{key: value}           map

%Host{}                 struct

def                     public function

defp                    private function

fn -> ... end           anonymous function

fun.()                  call anonymous function

&foo/1                  capture function

|>                      pipe

case                    pattern-based branching

when                    guard

Enum                    eager collection processing

Stream                  lazy collection processing

Task                    concurrent work

spawn                    raw BEAM process

send / receive          process messaging

@type                   type definition

@spec                   function type specification

@callback               behaviour requirement

@behaviour              implement behaviour
```
