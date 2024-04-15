person(greg).
person(susan).

son(greg, david).
son(david, jack).

daughter(kim, david).
daughter(steph, david).

child(X,Y) :- son(X,Y).
child(X,Y) :- daughter(X,Y).

grandchild(X,Y) :- child(X,Z), child(Z,Y).
grandson(X,Y) :- son(X,Z), child(Z,Y).

male(X) :- son(X,Q).
female(X) :- daughter(X,Q).
grandson(X,Y) :- grandchild(X,Y), male(X).

granddaugher(X,Y) :- grandchild(X,Y), female(X).

grandmother(X,Y) :- grandchild(Y,X), female(X).


