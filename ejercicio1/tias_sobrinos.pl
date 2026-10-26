:- consult('hermanos_tios.pl').

% tia(X, Y): X es tia de Y.
tia(X, Y) :-
    progenitor(Z, Y),
    hermana(X, Z).

% sobrino(X, Y): X es sobrino de Y.
sobrino(X, Y) :-
    hombre(X),
    tio(Y, X).
sobrino(X, Y) :-
    hombre(X),
    tia(Y, X).

% sobrina(X, Y): X es sobrina de Y.
sobrina(X, Y) :-
    mujer(X),
    tio(Y, X).
sobrina(X, Y) :-
    mujer(X),
    tia(Y, X).
