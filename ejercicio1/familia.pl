% Ejercicio 1: arbol genealogico de la familia Simpson

% hombre(X): X es hombre.
hombre(abraham).
hombre(clancy).
hombre(herb).
hombre(homero).
hombre(bart).

% mujer(X): X es mujer.
mujer(mona).
mujer(jacqueline).
mujer(marge).
mujer(patty).
mujer(selma).
mujer(lisa).
mujer(maggie).
mujer(ling).

% progenitor(X, Y): X es padre o madre de Y.
progenitor(abraham, homero).
progenitor(abraham, herb).
progenitor(mona, homero).

progenitor(clancy, marge).
progenitor(clancy, patty).
progenitor(clancy, selma).
progenitor(jacqueline, marge).
progenitor(jacqueline, patty).
progenitor(jacqueline, selma).

progenitor(homero, bart).
progenitor(homero, lisa).
progenitor(homero, maggie).
progenitor(marge, bart).
progenitor(marge, lisa).
progenitor(marge, maggie).

progenitor(selma, ling).

% padre(X, Y): X es padre de Y.
padre(X, Y) :-
    progenitor(X, Y),
    hombre(X).

% madre(X, Y): X es madre de Y.
madre(X, Y) :-
    progenitor(X, Y),
    mujer(X).

% hijo(X, Y): X es hijo de Y.
hijo(X, Y) :-
    progenitor(Y, X),
    hombre(X).