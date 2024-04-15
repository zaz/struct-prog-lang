lower(List,V,Lower):-
   findall(Elem, (member(Elem, List), Elem < V), Lower).

upper(List,V,Upper):-
   findall(Elem, (member(Elem, List), Elem > V), Upper).

equal(List,V,Equal):- 
   findall(Elem, (member(Elem, List), Elem = V), Equal).

qsort([],[]).
qsort([V|Rest],Sorted):-
    lower(Rest, V, Lower),
    equal([V|Rest], V, Equal),
    upper(Rest, V, Upper),
    qsort(Lower, SortedLower),
    qsort(Upper, SortedUpper),
    append(SortedLower, Equal, SortedLowerEqual),
    append(SortedLowerEqual, SortedUpper, Sorted).
