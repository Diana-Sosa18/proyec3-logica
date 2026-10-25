:- consult('familia.pl').

hermano(X, Y) :- hombre(X), progenitor(Z, X), progenitor(Z, Y), X \= Y.
hermana(X, Y) :- mujer(X), progenitor(Z, X), progenitor(Z, Y), X \= Y.
tio(X, Y) :- progenitor(Z, Y), hermano(X, Z).