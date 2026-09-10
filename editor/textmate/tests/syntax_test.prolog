% Prolog syntax-highlighting test

host(itpc).
host(wyn_laptop).

service(itpc, ssh, 22).
service(itpc, rdp, 3389).

remote_capable(Host) :-
    host(Host),
    service(Host, ssh, 22).