defmodule WynCommand.Networking.Diagnostics.Prolog do
  def query(goal) when is_binary(goal) do
    wrapped_goal =
      """
      (
        #{goal} ->
      writeln(true)
            ;
      writeln(false)
            )
      """

    {output, exit_code} =
      System.cmd(
        "swipl",
        [
          "-q",
          "-s",
          diagnostics_path(),
          "-g",
          wrapped_goal,
          "-t",
          "halt"
        ],
        stderr_to_stdout: true
      )

    {
      String.trim(output),
      exit_code
    }
  end

  defp diagnostics_path do
    Path.expand(
      "../../../../../shared/prolog/diagnostics.prolog",
      __DIR__
    )
  end

  def boolean_query(goal) when is_binary(goal) do
    case query(goal) do
      {"true", 0} ->
        {:ok, true}

      {"false", 0} ->
        {:ok, false}

      {output, exit_code} ->
        {:error,
         %{
           exit_code: exit_code,
           output: output
         }}
    end
  end

  def boolean_query_with_facts(goal, facts)
      when is_binary(goal) and is_binary(facts) do
    facts_path = temporary_facts_path()

    try do
      File.write!(facts_path, facts)

      query_with_facts(goal, facts_path)
    after
      File.rm(facts_path)
    end
  end

  defp query_with_facts(goal, facts_path) do
    wrapped_goal = "(#{goal} -> writeln(true) ; writeln(false))"

    {output, exit_code} =
      System.cmd(
        "swipl",
        [
          "-q",
          "-s",
          diagnostics_path(),
          "-s",
          facts_path,
          "-g",
          wrapped_goal,
          "-t",
          "halt"
        ],
        stderr_to_stdout: true
      )

    case {
      String.trim(output),
      exit_code
    } do
      {"true", 0} ->
        {:ok, true}

      {"false", 0} ->
        {:ok, false}

      {output, exit_code} ->
        {:error,
         %{
           output: output,
           exit_code: exit_code
         }}
    end
  end

  def ports_owned_by(process, facts) when is_binary(process) and is_binary(facts) do
    facts_path = temporary_facts_path()

    try do
      File.write!(facts_path, facts)

      query_ports_owned_by(process, facts_path)

    after
      File.rm(facts_path)
    end
  end

  defp query_ports_owned_by(process, facts_path) do
    goal = "ports_owned_by(#{process}, Ports), write_canonical(Ports)"

    {output, exit_code} = System.cmd(
      "swipl",
[
"-q",
"-s",
diagnostics_path(),
"-s",
facts_path,
"-g",
goal,
"-t",
"halt"
],
stderr_to_stdout: true
    )

    case exit_code do
      0 -> parse_port_list(output)

      _ -> {:error, %{
      output: String.trim(output),
exit_code: exit_code
      }}

    end
  end

  defp temporary_facts_path do
    unique_id =
      System.unique_integer([
        :positive,
        :monotonic
      ])

    Path.join(
      System.tmp_dir!(),
      "wyncommand_facts_#{unique_id}.prolog"
    )
  end

  defp parse_port_list(output) do
    output = String.trim(output)

    case output do
      "[]" -> {:ok, []}

      _ -> ports = output
      |> String.trim_leading("[")
      |> String.trim_trailing("]")
      |> String.split(",")
      |> Enum.map(&String.to_integer/1)
           {:ok, ports}
    end
  end
end
