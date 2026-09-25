:- dynamic listener/1.
:- dynamic owned_by/2.

:- multifile listener/1.
:- multifile owned_by/2.

expected_owner(1716, kdeconnectd).
expected_owner(4768, wyn_hub).
expected_owner(4769, wyn_hub).
expected_owner(6463, discord).

healthy_listener(Port) :-
    listener(Port),
    owned_by(Port, Process),
    expected_owner(Port, Process).

unexpected_owner(Port, Expected, Actual) :-
    listener(Port),
    expected_owner(Port, Expected),
    owned_by(Port, Actual),
    dif(Expected, Actual).

ports_owned_by(Process, Ports) :-
    findall(Port, owned_by(Port, Process), Ports).