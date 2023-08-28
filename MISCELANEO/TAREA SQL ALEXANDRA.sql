use Northwind
go

---1. Obtener todas las columnas de la tabla Region

 select*from INFORMATION_SCHEMA.COLUMNS 
  where TABLE_NAME = 'Region'
  select*from Region

---2. Obtener los FirstName y LastName de la tabla Employees.

select FirstName, 
       LastName 
	   from Employees  

---3. Obtener las columnas FirstName y LastName de la tabla Employees. Ordenados por la columna LastName. 

select FirstName, 
       LastName 
       from Employees  

order by LastName

---4. Obtener las filas de la tabla orders ordenadas por la columna Freight de mayor a menor; las columnas que presentara son: OrderID, OrderDate, ShippedDate, CustomerID, and Freight.

select OrderID, 
       OrderDate, 
       ShippedDate, 
       CustomerID,
       Freight 
	   from Orders 

order by Freight desc

---5. Obtener los empleados tengan el valor null en la columna region. 

select*from Employees 
where Region is NULL

---6. Obtener los empleados ordenados alfabéticamente por FirstName y LastName 

select*from Employees
order by FirstName, LastName 
---7. Obtener los empleados cuando la columna title tenga el valor de Sales Representatives y el campo city tenga los valores de Seattle o Redmond.

select * from Employees
where title = 'Sales Representative'
and (city = 'Seattle' or
     city = 'Redmond')


---8. Obtener las columnas company name, contact title, city y country de los clientes que están en la Ciudad de México o alguna ciudad de España excepto Madrid.

select CompanyName, 
       ContacTtitle, 
	   city,
	   country  from Customers

	   where (Country = 'Mexico' or
       Country = 'Spain')
	   and city != 'Madrid'


---9. Obtener la lista de órdenes, y mostrar una columna en donde se calcule el impuesto del 10% cuando el valor de la columna Freight >= 480.

select OrderID,
       FREIGHT,
CASE
	WHEN Freight > 480 	THEN Freight * 0.1
	ELSE 0
	END AS 'IMPUESTO'

from [Orders]
ORDER BY Freight DESC


---10. Obtener el numero de empleados para cada ciudad. 

select City ,
count(employeeid) as 'N° Empleados'
from Employees
group by City

---11. Obtener los clientes que colocaron una orden en Set/1997

--select * from Customers
--select * from Orders

select
A.CompanyName,A.ContactName, B.OrderID, B.OrderDate

from Customers as A
LEFT JOIN Orders AS B
ON (A.CustomerID = B.CustomerID)
WHERE B.OrderDate BETWEEN '19970901' AND '19970930'

order by OrderDate

---12. Obtener un reporte en donde se muestre la cantidad de ordenes por cada vendedor 

select A.EmployeeID, (A.LastName + ' ' +A.FirstName) AS 'EMPLEADO',COUNT(B.OrderID) AS 'ORDENES'
from Employees as A
left join Orders AS B
ON (A.EmployeeID = B.EmployeeID)
GROUP BY A.EmployeeID ,(A.LastName + ' ' +A.FirstName)

---13. Obtener un reporte por Vendedor que muestre el número de órdenes y el importe vendido para cada año de operaciones

select 
A.EmployeeID, 
(A.LastName + ' ' +A.FirstName) AS 'EMPLEADO',
COUNT(B.OrderID) AS 'N° ORDENES',
YEAR(B.OrderDate) AS 'AÑO DE OPERACIÓN',
ROUND(SUM((C.UnitPrice * C.Quantity) * (1 - C.Discount)),2) AS 'IMPORTE VENDIDO'

from Employees as A
left join Orders AS B
ON (A.EmployeeID = B.EmployeeID)
LEFT JOIN [Order Details]  AS C
ON (B.OrderID = C.OrderID)
GROUP BY A.EmployeeID ,(A.LastName + ' ' +A.FirstName), YEAR(B.OrderDate)
go
---14. Del reporte obtenido en la respuesta 13; muestre los 5 primeros vendedores para cada año.

WITH ventas_empleados AS (
    SELECT 
        A.EmployeeID, 
        (A.LastName + ' ' + A.FirstName) AS EMPLEADO,
        COUNT(B.OrderID) AS 'N° ORDENES',
        YEAR(B.OrderDate) AS 'AÑO DE OPERACIÓN',
        ROUND(SUM((C.UnitPrice * C.Quantity) * (1 - C.Discount)), 2) AS 'IMPORTE VENDIDO',
        ROW_NUMBER() OVER (PARTITION BY YEAR(B.OrderDate) ORDER BY SUM((C.UnitPrice * C.Quantity) * (1 - C.Discount)) DESC) AS numero_fila
    FROM Employees AS A
    LEFT JOIN Orders AS B ON (A.EmployeeID = B.EmployeeID)
    LEFT JOIN [Order Details] AS C ON (B.OrderID = C.OrderID)
    GROUP BY A.EmployeeID, (A.LastName + ' ' + A.FirstName), YEAR(B.OrderDate)
)

SELECT *
FROM ventas_empleados
WHERE numero_fila <= 5
ORDER BY 'AÑO DE OPERACIÓN', 'IMPORTE VENDIDO' DESC

---15. Muestre el total de ventas agrupando por categoría de productos.
SELECT * FROM [Order Details] A
SELECT * FROM [OrderS] B 
SELECT * FROM Products C 
SELECT * FROM Categories D

SELECT D.CategoryName, 
ROUND(SUM((A.UnitPrice * A.Quantity) * (1 - A.Discount)),2) AS 'TOTAL VENTAS'
FROM [Order Details] AS A
LEFT JOIN [OrderS] AS B
ON (A.OrderID = B.OrderID)
LEFT JOIN Products AS C
ON (A.ProductID = C.ProductID)
LEFT JOIN Categories AS D
ON (C.CategoryID = D.CategoryID)
GROUP BY D.CategoryName

---16. Del reporte obtenido en la respuesta 14; muestre la evolución de las ventas por categoría de productos agrupados para cada año de las operaciones.

---17. Muestre el reporte de ventas por Region.
SELECT 
    H.RegionDescription AS 'Region', 
    SUM(OD.UnitPrice * OD.Quantity) AS 'VENTAS' 
FROM Orders AS O
INNER JOIN [Order Details] AS OD 
ON O.OrderID = OD.OrderID
INNER JOIN Customers AS C 
ON O.CustomerID = C.CustomerID
INNER JOIN Employees AS E 
ON O.EmployeeID = E.EmployeeID
INNER JOIN EmployeeTerritories as F
ON F.EmployeeID = E.EmployeeID
INNER JOIN Territories as G
ON F.TerritoryID = G.TerritoryID
INNER JOIN Region AS H
ON G.RegionID = H.RegionID

GROUP BY H.RegionDescription
ORDER BY 'VENTAS' DESC



	select * from Orders
	select * from [Order Details]
	select * from Customers
	SELECT * FROM Employees
	SELECT * FROM EmployeeTerritories
	SELECT * FROM Territories
	SELECT * FROM Region


---18. Del reporte obtenido en la respuesta 17, muestre la evolución de ventas por región agrupadas para cada año de las operaciones.

SELECT 
    H.RegionDescription AS 'Region', 
    YEAR(O.OrderDate) AS 'AÑO', 
    SUM(OD.UnitPrice * OD.Quantity) AS 'VENTAS' 
FROM Orders AS O
INNER JOIN [Order Details] AS OD 
ON O.OrderID = OD.OrderID
INNER JOIN Customers AS C 
ON O.CustomerID = C.CustomerID
INNER JOIN Employees AS E 
ON O.EmployeeID = E.EmployeeID
INNER JOIN EmployeeTerritories as F
ON F.EmployeeID = E.EmployeeID
INNER JOIN Territories as G
ON F.TerritoryID = G.TerritoryID
INNER JOIN Region AS H
ON G.RegionID = H.RegionID

GROUP BY H.RegionDescription, YEAR(O.OrderDate)
ORDER BY H.RegionDescription, YEAR(O.OrderDate)


---19. Muestre un reporte de ventas agrupadas por País de embarque

SELECT 
ShipCountry AS 'PAÍS DE EMBARQUE', 
SUM(OD.UnitPrice * OD.Quantity) AS 'VENTAS'
FROM Orders AS O
INNER JOIN [Order Details] AS OD ON O.OrderID = OD.OrderID
INNER JOIN Customers AS C ON O.CustomerID = C.CustomerID
GROUP BY ShipCountry
ORDER BY 'VENTAS' DESC

---20. Del reporte anterior, muestre las ventas agrupadas por año de operaciones.

SELECT ShipCountry AS 'PAÍS DE EMBARQUE', YEAR(O.OrderDate) AS 'AÑO DE OPERACIÓN', SUM(OD.UnitPrice * OD.Quantity) AS 'VENTAS'
FROM Orders AS O
INNER JOIN [Order Details] AS OD ON O.OrderID = OD.OrderID
INNER JOIN Customers AS C ON O.CustomerID = C.CustomerID
GROUP BY ShipCountry, YEAR(O.OrderDate)
ORDER BY 'AÑO DE OPERACIÓN', 'VENTAS' DESC


