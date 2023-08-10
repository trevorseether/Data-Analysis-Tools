DECLARE @Fecha1 DATETIME='20230808'
DECLARE @Fecha2 DATETIME='20230808'
 
SELECT
	Cc.IDVOUCHER,
	CC.CodTipoCaja ,
    s.CodigoSocio ,
        LEFT(CONCAT(LEFT(CONCAT(
    LTRIM(RTRIM(REPLACE(REPLACE(REPLACE(REPLACE(
    REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(
    IIF(S.CodTipoPersona=1,CONCAT(LTRIM(RTRIM(S.ApellidoPaterno)),SPACE(1),LTRIM(RTRIM(S.ApellidoMaterno)),SPACE(1), LTRIM(RTRIM(S.Nombres)))
    ,RTRIM(LTRIM(S.RazonSocial)))
    ,'=',''),'&',''),'/',''),'=',''),')',''),'#',''),'.',''),'Ñ','N'),'"',''),'(','')
        ,'Á','A'),'É','E'),'Í','I'),'Ó','O'),'Ú','U'
        ),CHAR(9),''),CHAR(10),''),CHAR(13),'')
        )),SPACE(150)),150),SPACE(150)),150) AS 'Socio',
        ISNULL(CONVERT(Varchar(10),CC.Fecha,103),' ') As 'FechaPago',
        CC.Concepto,CC.Total,
 
        AD.NumeroOperacionDestino, 
		EF.Descripcion AS 'Banco',
		C.NumeroCuenta,
        CC.FechaRegistro, 
		U.IdUsuario 

FROM  
	Socio AS S  
	INNER JOIN CajaCab CC ON S.CodSocio =CC.CodSocio 
	LEFT JOIN AdmisionDocumento AS AD ON CC.CodAdmisionDocumento =AD.CodAdmisionDocumento 
	LEFT JOIN TABLAMAESTRADET AS TM ON TM.CODTABLADET=AD.CODMONEDA
	LEFT JOIN EntidadFinanciera AS EF ON AD.CodBancoDestino =EF.CodEntidadFinanciera
	LEFT JOIN Usuario AS U ON CC.CodCajero =U.CodUsuario 
	LEFT JOIN  Cuenta AS C ON AD.CodCuentaDestino = C.CodCuenta 

WHERE
(CONVERT(Varchar(10),CC.Fecha,112)>=CONVERT(Varchar(10),@Fecha1,112) AND CONVERT(Varchar(10),CC.Fecha,112)<=CONVERT(Varchar(10),@Fecha2,112))
AND
--CC.Total>0 AND CC.Concepto LIKE 'APORTE INICIAL' 
CC.Total>0 AND (CC.Concepto LIKE 'APORTE%' or CC.Concepto LIKE 'CONCEPTO DE ADMISIÓN%')

ORDER BY CC.CONCEPTO, CC.Fecha 


----
--SELECT * FROM TablaMaestraDet WHERE CodTablaCab =97

--SELECT * FROM CajaCab WHERE IdVoucher ='I0577942'