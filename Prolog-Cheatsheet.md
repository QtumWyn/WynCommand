# Prolog Quick Reference

## Thinking in Prolog

Imperative thinking:
"Check whether port 5432 belongs to postgres."

Prolog thinking:
"These relationships are true.
What else follows from them?"

## Comments

```prolog
% Single line

/*
   Multi-line
*/
```

## Facts

```prolog
listener(tcp, 22).
listener(tcp, 80).
listener(tcp, 443).

owned_by(22, sshd).
owned_by(5432, postgres).
```

## Queries

```prolog
?- listener(tcp, 22).

true.
```

## Variables Start With Capital Letters

```prolog
?- listener(tcp, Port).

Port = 22 ;
Port = 80 ;
Port = 443.
```

## `_` Means "I Don't Care"

```prolog
?- listener(_, 443).

true.
```

## Rules

```prolog
web_port(Port) :-
    listener(tcp, Port),
    Port = 80.


% Multiple possible rules

web_port(80).
web_port(443).
web_port(8080).
web_port(8443).
```

## Rule With Variables

```prolog
service_running(Service) :-
    owned_by(_, Service).


// WRONG: // isn't a Prolog comment
% use % instead
```

## And / Conjunction

```prolog
reachable_service(Port) :-
    listener(tcp, Port),
    Port > 0.
```

## Or / Disjunction

```prolog
web_port(Port) :-
    Port = 80 ;
    Port = 443.
```

## Negation

```prolog
unexpected_port(Port) :-
    listener(tcp, Port),
    \+ expected_port(Port).
```

## Unification

```prolog
X = hello.

Host = host('1.1.1.1', 443).
```

## Structured Terms

```prolog
host('1.1.1.1', 443).

process(1234, postgres, user(postgres)).


// VARIABLES
//
// Uppercase = variable
// lowercase = atom

Port       % variable
Process    % variable

postgres   % atom
tcp        % atom
```

## Lists

```prolog
Ports = [22, 80, 443].
```

## Head / Tail

```prolog
[Head | Tail] = [22, 80, 443].

% Head = 22
% Tail = [80, 443]
```

## Member

```prolog
member(443, [22, 80, 443]).
```

## Recursion

```prolog
contains_port(Port, [Port | _]).

contains_port(Port, [_ | Rest]) :-
    contains_port(Port, Rest).
```

## Arithmetic

```prolog
X is 5 + 3.
```

## X = 8


## Important:

```prolog
% = does NOT perform arithmetic evaluation

X = 5 + 3.

% X becomes the term 5 + 3
```

## Arithmetic Comparisons

```prolog
X =:= Y      % numeric equality
X =\= Y      % numeric inequality

X < Y
X > Y
X =< Y
X >= Y
```

## Unification

```prolog
X = Y
```

## Strict Term Identity

```prolog
X == Y
```

## Collect Results

```prolog
findall(
    Port,
    listener(tcp, Port),
    Ports
).
```

## Module

```prolog
:- module(diagnostics, [
    unexpected_listener/1,
    service_running/1
]).
```

## Dynamic Facts

```prolog
:- dynamic listener/2.

assertz(listener(tcp, 8080)).

retract(listener(tcp, 8080)).

retractall(listener(_, _)).
```

## Brain Map

```text
foo.                    atom

Foo                     variable

_                       anonymous variable

listener(tcp, 22).      fact

reachable(X) :- ...     rule

?- reachable(X).        query

predicate/2             predicate name + arity

,                       AND

;                       OR

\+                      NOT

=                       unify

is                      evaluate arithmetic

=:=                     numeric equality

[H | T]                 list head/tail

member(X, List)         membership

findall(...)            collect solutions
```
