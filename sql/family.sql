SELECT
R.Nazwisko, R.EmailMamy, R.EmailTaty, R.TelMamy, R.TelTaty,
C.sysTitle AS Dziecko,
C.Imie AS Imie,
L.KodLinii,
C.id AS idDziecka,
L.id AS idLinii

FROM
r_storodzina AS R
JOIN r_stoewidencja AS E ON E.Rodzina = R.id
JOIN r_stoucznia AS C ON C.Rodzina = R.id AND E.Uczen = C.id
JOIN r_stolinia AS L ON L.id = E.Linia

WHERE (R.TelMamy=:tel OR R.TelTaty=:tel) and E.active = 1