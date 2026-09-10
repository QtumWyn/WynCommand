macro(m3, java, git).
macro(m4, zig, build).
macro(m6, elixir, networking).

healthy(git).
healthy(build).
unhealthy(networking).

depends_on(deploy, git).
depends_on(deploy, build).
depends_on(deploy, networking).

blocked(Task) :-
    blocked_by(Task, _).

unhealthy_macro(Macro, Purpose) :-
    macro(Macro, _, Purpose),
    unhealthy(Purpose).

blocked_by(Task, Macro) :-
    depends_on(Task, Purpose),
    unhealthy_macro(Macro, Purpose).