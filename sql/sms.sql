INSERT INTO `tblsmsbus` (
    `czasOdebrania`,
    `czasOdebraniaSMSAPI`,
    `numerTelefonu`,
    `dataDocelowa`,
    `tresc`,
    `idDziecka`,
    `idLinii`
) VALUES (
    :dateReceived,
    :dateReceivedAPI,
    :tel,
    :targetDate,
    :text,
    :childID,
    :lineID
);
