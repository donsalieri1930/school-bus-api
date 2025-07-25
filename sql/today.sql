SELECT
    B.*,
    C.sysTitle,
    L.KodLinii
FROM
    tblsmsbus AS B
JOIN r_stoucznia AS C ON B.idDziecka = C.id
JOIN r_stolinia AS L ON B.idLinii = L.id
WHERE B.dataDocelowa = CURDATE();