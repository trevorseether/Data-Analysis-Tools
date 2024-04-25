 -------------------- TODOS LOS QUE TENGAN DNI (LA DATA ENVIADA DEBE SER NULEADA EL NRO DE DOCUMENTO Y EN EL USP PONER LA FECHA DE HOY)
 -------------------- VER QUE LOS TIPOS DE LISTA ESTEN TODOS DEL EXCEL SINO ACTIVAR LOS QUE NECESITES
declare @NroDocumento nvarchar(255)
 
declare CursorListaNegra cursor for
select NroDocumento from ListaNegraTablaTempo where len(ltrim(rtrim(NroDocumento)))>0
open CursorListaNegra
-- Avanzamos un registro y cargamos en las variables los valores encontrados en el primer registro
fetch next from CursorListaNegra  into @NroDocumento
while @@fetch_status = 0
begin
if (select count(1) from ListaNegra where  CONCAT(LTRIM(RTRIM(NroDocIdentidad)),LTRIM(RTRIM(NRORUC)))=@NroDocumento)>0
     begin
     print 0

        --------------------------------------
		declare @CodListaNegra int

		select @CodListaNegra=CodListaNegra from (SELECT  ROW_NUMBER() OVER(PARTITION BY CONCAT(
		LTRIM(RTRIM(NroDocIdentidad)),LTRIM(RTRIM(NRORUC)))  ORDER BY codlistanegra DESC ) AS r , *
			FROM ListaNegra  ) as r where   CONCAT(
		LTRIM(RTRIM(NroDocIdentidad)),LTRIM(RTRIM(NRORUC))) = @NroDocumento and r.r=1

		---- INSERTAR SOLO DETALLE CON @CodListaNegra

		insert into ListaNegraDetalle(
		CodListaNegra,ObservacionBloqueo,CodMotivoBloqueo,CodEstadoListaNegra,Fecha,CodUsuario, FechaSolicitud,FechaIngreso,CodTipoLista,MotivoBloqueo,CodTipoListaNegra
		 )
		 SELECT  @CodListaNegra,
		 --CONCAT(ENTIDAD,' - ',CARGO,' - ',TipoNoticia,'-',CONVERT(varchar,FECHAFIN,103))  AS ObservacionBloqueoBK,-----OBSERVACION
		 Observacion,
		-- 318 AS CodMotivoBloqueoBK,
		 1377 AS CodMotivoBloqueoBK,
		 314 AS CodEstadoListaNegraBK,
		 GETDATE() AS FechaBK,1 AS CodUsuarioBK,
		 FECHAINICIO AS FechaSolicitudBK,FECHAINICIO AS FechaIngresoBK,
		--IIF(tipolista='BANCO MUNDIAL',1036,
		--IIF(tipolista='BID',1037,
		--IIF(tipolista='COLEGIO ABOGADOS',1038,
		--IIF(tipolista='CONTRALORIA',1039,
		--IIF(tipolista='MEDIOS ADVERSOS',1040,
		--IIF(tipolista='OFAC',909,
		--IIF(tipolista='ONU',926,
		--IIF(tipolista='OSCE',1041,
		--IIF(tipolista='PEP',973,
		--IIF(tipolista='RECOMPENSAS',1042,
		-- NULL)))))))))) AS CodTipoListaBK,
		 NULL AS CodTipoListaBK,
		 --CONCAT(ENTIDAD,' - ',CARGO,' - ',TipoNoticia,'-',CONVERT(varchar,FECHAFIN,103)) AS MotivoBloqueoBK,-----OBSERVACION
		 Observacion,
		910 AS CodTipoListaNegra  
		 FROM ListaNegraTablaTempo where NroDocumento =@NroDocumento
         ---------------------------------------

     end
     else
     begin
      print @NroDocumento
		--------------------------------------------
    
		insert into ListaNegra(CodTipoPersona,CodTipoDocIdentidad,NroDocIdentidad,NroRuc,ApellidoPaterno,ApellidoMaterno,Nombres,RazonSocial,FlagBloqueo,
		Origen,
		CodTipoListaNegra
		)

		SELECT IIF(TipoDocto='RUC',2,1) AS CodTipoPersona,
		IIF(TipoDocto='DNI',5,IIF(TipoDocto='CARNET EXT.',6,IIF(TipoDocto='PASAPORTE',99,IIF(TipoDocto='RUC',100,1035)))) AS CodTipoDocIdentidad,
		IIF(TipoDocto<>'RUC',nrodocumento,NULL)    AS  NroDocIdentidad,
		IIF(TipoDocto='RUC',nrodocumento,NULL)    AS  NroRuc,
		APEPATERNO AS ApellidoPaterno,APEMATERNO AS ApellidoMaterno, IIF(TipoDocto='RUC',NULL,Nombres) AS Nombres,
		IIF(TipoDocto='RUC',Nombres,NULL) AS  RazonSocial,1 AS FlagBloqueo,'SM' AS Origen,
		910 AS CodTipoListaNegra
		FROM ListaNegraTablaTempo  where  NroDocumento =@NroDocumento
 
		DECLARE @CLAVE INT
		SELECT @CLAVE =@@IDENTITY
		insert into ListaNegraDetalle(
		CodListaNegra,ObservacionBloqueo,CodMotivoBloqueo,CodEstadoListaNegra,Fecha,CodUsuario, FechaSolicitud,FechaIngreso,CodTipoLista,MotivoBloqueo,CodTipoListaNegra
		)
		SELECT  @CLAVE,
		--CONCAT(ENTIDAD,' - ',CARGO,' - ',TipoNoticia,'-',CONVERT(varchar,FECHAFIN,103))  AS ObservacionBloqueoBK,-----OBSERVACION
		Observacion,
		-- 318 AS CodMotivoBloqueoBK,
		 1377 AS CodMotivoBloqueoBK,
		314 AS CodEstadoListaNegraBK,GETDATE() AS FechaBK,1 AS CodUsuarioBK,
		FECHAINICIO AS FechaSolicitudBK,FECHAINICIO AS FechaIngresoBK,
		--IIF(tipolista='BANCO MUNDIAL',1036,
		--IIF(tipolista='BID',1037,
		--IIF(tipolista='COLEGIO ABOGADOS',1038,
		--IIF(tipolista='CONTRALORIA',1039,
		--IIF(tipolista='MEDIOS ADVERSOS',1040,
		--IIF(tipolista='OFAC',909,
		--IIF(tipolista='ONU',926,
		--IIF(tipolista='OSCE',1041,
		--IIF(tipolista='PEP',973,
		--IIF(tipolista='RECOMPENSAS',1042,
		--NULL)))))))))) AS CodTipoListaBK,
		NULL AS CodTipoListaBK,
		--CONCAT(ENTIDAD,' - ',CARGO,' - ',TipoNoticia,'-',CONVERT(varchar,FECHAFIN,103)) AS MotivoBloqueoBK,-----OBSERVACION
		Observacion,
		910 AS CodTipoListaNegra  
		FROM ListaNegraTablaTempo where NroDocumento =@NroDocumento

		-----------------------------------------------
     end

 
fetch next from CursorListaNegra    into @NroDocumento
end
 
close CursorListaNegra
deallocate CursorListaNegra
 