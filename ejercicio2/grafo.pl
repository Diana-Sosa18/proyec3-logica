% Ejercicio 2: grafo dirigido ({a,b,c,d}, {(a,b),(a,c),(a,d),(c,d)})

% arco(X, Y): existe una arista dirigida de X a Y.
arco(a, b).
arco(a, c).
arco(a, d).
arco(c, d).

% camino(X, Y, C): C es un camino desde X hasta Y.

% Caso base: hay un arco directo.
camino(X, Y, [X, Y]) :-
    arco(X, Y).

% Caso recursivo: pasar por un vertice intermedio Z.
camino(X, Y, [X | Resto]) :-
    arco(X, Z),
    camino(Z, Y, Resto).