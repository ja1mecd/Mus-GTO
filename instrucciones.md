Instrucciones para usar la web.

(En un principio, nada de esto es necesario para el usuario, ya que debería funcionar por sí solo)

1. Primero hay que calcular la probabilidad de que una mano gane en los distintos lances. Para ello se utiliza el script generador_mus.py. Los datos se guardan en una base de datos SQL.
2. Dado que Google Sites no tiene la capacidad para leer directamente la base de datos de SQL, exportamos los datos de la base de datos de SQL a una hoja de cálculo de Google usando el script exportar_mysql_csv.py.
3. Ahora, usamos un Google Apps Script, google_apps_script_mus.js, que es capaz de leer los datos de la hoja de cálculo y es un API para la web de Google Sites.
4. El código fuente de la web está en el script index-v-googlesites.html. En la propia web, en el apartado de Configuración Inicial, viene detallado como integrar el API en la web.
5. También se pueden econtrar los datos de la base de datos en el fichero base_datos_mus.json.

Puede que haya erratas en el código y que no todo funcione a la perfección. En el display de un móvil no se ve bien, pero en una pantalla de ordenador no debería haber problemas.
