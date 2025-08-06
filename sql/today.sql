SELECT
    B.*,
    C.sysTitle AS ImieDziecka,
    L.KodLinii,
    K.sysTitle AS Klasa
FROM
    tblsmsbus AS B
JOIN r_stoucznia AS C ON B.idDziecka = C.id
JOIN r_stolinia AS L ON B.idLinii = L.id
JOIN r_stoklasa AS K ON C.KlasaDU = K.id
WHERE B.dataDocelowa = CURDATE()
ORDER BY L.kodLinii, Klasa, C.Nazwisko, C.Imie;